import hashlib
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime
from os import getenv
from pathlib import Path
from queue import Queue
from threading import Thread

import requests
from loguru import logger


@dataclass
class Pricelist:
    url: str
    address: str | None
    city: str | None
    store_id: str
    location_id: str | None
    dt: datetime
    filename: str
    request_kwargs: dict = field(default_factory=dict)


class _WaybackArchiverImpl:
    options: dict = {
        'capture_all': 'on',
        'capture_outlinks': '1',
        'skip_first_archive': '1',
        'if_not_archived_within': '6h',
        'delay_wb_availability': '1',
    }
    _headers: dict
    _thread: Thread
    _queue: Queue[str | None]
    _ready: bool = False

    def initialize(self, access_key: str, secret_key: str):
        self._headers = {
            'Accept': 'application/json',
            'Authorization': f'LOW {access_key}:{secret_key}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        self._queue = Queue()
        self._ready = True
        self._thread = Thread(target=self._worker, daemon=True, name='WaybackArchiverThread')
        self._thread.start()
        logger.info(f'WaybackArchiver initialized, worker thread id: {self._thread.native_id}')

    def archive(self, url: str):
        if not self._ready:
            raise RuntimeError('WaybackArchiver.archive(url) called before initialize()')
        self._queue.put(url)

    def _worker(self):
        if not self._ready:
            raise RuntimeError('wayback machine archiver ')
        while True:
            url = self._queue.get()
            if url is None:
                logger.debug('WaybackArchiver worker received shutdown signal')
                break
            time.sleep(21)  # put the sleep here so we don't have to wait for shutdown
            logger.debug(f'Save Page Now: {url}')
            try:
                data = {'url': url, **self.options}
                if 'zabac' in url:  # zabac is weird, better archive everything for now
                    del data['if_not_archived_within']
                r = requests.post(
                    'https://web.archive.org/save',
                    headers=self._headers,
                    data=data
                )
                r.raise_for_status()
            except Exception as e:
                logger.warning(f'error while archiving {url}: {e!r}')
                self._queue.put(url)  # re-queue the URL for later processing
            finally:
                self._queue.task_done()

    def shutdown(self):
        if self._ready:
            logger.info('Shutting down WaybackArchiver worker thread')
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                    self._queue.task_done()
                except:
                    break
            self._queue.put(None)
            self._thread.join()


class _LocalArchiverImpl:
    archive_dir = Path('archive').resolve()
    db_path = archive_dir / 'index.db'
    session = requests.Session()
    _initialized: bool = False
    _queue: Queue[Pricelist | None] = Queue()
    _thread: Thread

    def initialize(self):
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pricelists (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    url         TEXT    NOT NULL,
                    filename    TEXT    NOT NULL,
                    store_id    TEXT    NOT NULL,
                    location_id TEXT,
                    year        INTEGER NOT NULL,
                    month       INTEGER NOT NULL,
                    day         INTEGER NOT NULL,
                    hour        INTEGER NOT NULL,
                    minute      INTEGER NOT NULL,
                    second      INTEGER NOT NULL,
                    local_file  TEXT    NOT NULL,
                    sha256      TEXT    NOT NULL,
                    added_ts    INTEGER NOT NULL
                );
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_pricelists_ymd ON pricelists(year, month, day);')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_pricelists_url ON pricelists(url);')
            conn.commit()
        self._thread = Thread(target=self._worker, daemon=True, name='LocalArchiverThread')
        self._thread.start()
        self._initialized = True
        logger.info(f'Local archive initialized at {self.archive_dir}, worker thread id: {self._thread.native_id}')

    def now_ts(self) -> int:
        return int(time.time()) - 1_700_000_000  # smaller integers, just in case
        # return time.time_ns() // 100000000 - 17489851440

    def safe_filename(self, filename: str) -> str:
        return ''.join(c for c in filename if c.isalnum() or c in ' -_,.#&').rstrip()

    def _download_file(self, url: str, **kwargs) -> bytes:
        logger.debug(f'downloading {url} with {kwargs = }')
        try:
            response = self.session.get(url, timeout=60, **kwargs)
        except requests.exceptions.SSLError as e:
            logger.warning(f'SSLError while downloading {url}: {e!r}')
            logger.warning('retrying with verify=False')
            return self._download_file(url, **kwargs, verify=False)
        except requests.exceptions.ChunkedEncodingError as e:
            logger.error(f'ChunkedEncodingError while downloading {url}: {e!r}')
            raise e
        response.raise_for_status()
        return response.content

    def _save_new_file(self, pricelist: Pricelist, raw_data: bytes) -> Path:
        # logger.debug(f'saving {task}')
        sha256 = hashlib.sha256(raw_data).hexdigest()
        local_file = self.archive_dir / pricelist.store_id / pricelist.dt.strftime('%Y-%m-%d') \
                     / self.safe_filename(sha256[:8] + '_' + pricelist.filename)
        local_file.parent.mkdir(parents=True, exist_ok=True)
        with open(local_file, 'wb') as f:
            f.write(raw_data)

        relative_path = str(local_file.relative_to(self.archive_dir)).replace('\\', '/')
        with sqlite3.connect(self.db_path, timeout=80) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO pricelists (
                url, filename, store_id, location_id,
                year, month, day, hour, minute, second,
                local_file, sha256, added_ts
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''', (
                pricelist.url, pricelist.filename, pricelist.store_id, pricelist.location_id,
                pricelist.dt.year, pricelist.dt.month, pricelist.dt.day, pricelist.dt.hour, pricelist.dt.minute, pricelist.dt.second,
                relative_path, sha256, self.now_ts()
            ))
            conn.commit()

        return local_file

    def _fetch_local_file(self, url: str) -> list:
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT local_file, sha256, added_ts, id FROM pricelists 
            WHERE url = ? ORDER BY added_ts DESC;''', (url,))
            return cursor.fetchone()

    def _worker(self):
        while True:
            task = self._queue.get()
            if task is None:
                logger.debug('LocalArchiver worker received shutdown signal')
                break
            # logger.info(f'got task: {task}')
            try:
                row = self._fetch_local_file(task.url)
                path_exists = row and (self.archive_dir / row[0]).exists()
                # if we already fetched this in the last 6 hours
                if path_exists and row[2] - self.now_ts() < 60 * 60 * 6:
                    # logger.debug(f'file for {task.url} already exists and is recent enough, skipping download')
                    continue
                # otherwise, download the file and then store it if it's new or different sha256
                raw_data = self.fetch(task, return_it=True, force_download=True)
                # raw_data = self._download_file(task.url)
                # if not path_exists or not row or row[1] != hashlib.sha256(raw_data).hexdigest():
                #     if not path_exists and row:
                #         logger.warning(f'adding deleted file {task.filename}')
                #     elif row:
                #         logger.warning(f'got different sha256 for {task.url}, updating archive')
                #     self._save_new_file(task, raw_data)
            except requests.exceptions.HTTPError as e:
                logger.warning(f'got {e.response.status_code} for {task.url}: {e!r}')
            except Exception as e:
                logger.error(f'Error while processing task {task}: {e!r}')
                logger.exception(e)
            finally:
                self._queue.task_done()
                time.sleep(.01)

    def fetch(self, pricelist: Pricelist, return_it: bool = False, force_download: bool = False) -> bytes | None:
        # logger.debug(f'fetching {pricelist.url} with kwargs={pricelist.request_kwargs}')
        if 'plodine.hr/' in pricelist.url.lower():
            if 'headers' not in pricelist.request_kwargs:
                pricelist.request_kwargs['headers'] = {}
            pricelist.request_kwargs['headers']['verify'] = 'certs/www.plodine.hr.crt'
        if not return_it:
            self._queue.put(pricelist)
            return None
        if not force_download and (row := self._fetch_local_file(pricelist.url)):
            local_file = self.archive_dir / row[0]
            # logger.debug(f'checking local file {local_file} for {pricelist.url}')
            if local_file.exists() and hashlib.sha256(t := local_file.read_bytes()).hexdigest() == row[1]:
                return t
            logger.warning(f'local file {local_file} does not exist (deleted/changed?), re-downloading and updating index.db')
            with sqlite3.connect(self.db_path, timeout=30) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM pricelists WHERE id = ?;', (row[3],))
                conn.commit()
        raw_data = self._download_file(pricelist.url, **pricelist.request_kwargs)
        self._save_new_file(pricelist, raw_data)
        return raw_data

    def shutdown(self):
        if self._initialized:
            logger.info('Shutting down LocalArchiver worker thread')
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                    self._queue.task_done()
                except:
                    break
            self._queue.put(None)
            logger.info('Waiting for LocalArchiver worker thread to finish...')
            self._thread.join()


WaybackArchiver = _WaybackArchiverImpl()
if (a := getenv('WAYBACK_ACCESS_KEY')) and (s := getenv('WAYBACK_SECRET_KEY')):
    WaybackArchiver.initialize(a, s)

LocalArchiver = _LocalArchiverImpl()
LocalArchiver.initialize()
