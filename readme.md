# https://cijene.org/

Projekt za arhiviranje, pretraživanje i prikaz cijena prema [Odluci NN 75/2025](https://narodne-novine.nn.hr/clanci/sluzbeni/2025_05_75_979.html). **WORK IN PROGRESS!**  

Nadam se da će kod nekome biti koristan za svoje istraživanje. Ovaj repository objavljen je pod AGPL-3.0 licencom. Molim vas da date adekvatan credit (npr. [poveznica](https://github.com/IamMusavaRibica/cijene.org/)) tamo gdje je potrebno. Ako imate neke komentare ili prijedloge, otvorite prvo issue pa ćemo diskutirati

**Također pogledajte: https://github.com/senko/cijene-api**

## Obična instalacija
- (neobavezno) definirajte environment varijable [`WAYBACK_ACCESS_KEY`, `WAYBACK_SECRET_KEY`](https://archive.org/account/s3.php) i `LOGLEVEL`
- po želji kreirajte `.venv` naredbom `py -m venv .venv` pa ga aktivirajte s `.\.venv\Scripts\activate` (na Windows treba `".venv/scripts/activate"`)
- instalacija svega potrebnog: `py -m pip install -r requirements.txt`
- uredite `cijene.toml`
- pokrenite server: `uvicorn main:app --host 0.0.0.0 --port 80` (ovo je na http, za https posebno generirajte certifikate i dodajte potrebne parametre za uvicorn)

## Docker instalacija
ove upute su pisane za Linux, na drugim OS-evima treba koristiti ekvivalentne naredbe  
1. [instalirajte docker](https://docs.docker.com/engine/install/)
2. git clone ovaj repositorij, uđite u njega (`cd`)
3. odlučite koji user će pokretati server pa pokrenite `sudo usermod -aG docker <user>` i restartajte ssh sesiju
4. `id -u <user>` i `id -g <user>` da dobijete UID i GID pa promijenite u `docker-compose.yml` ako nisu 1000
5. uredite `cijene.toml`, upute se nalaze u njemu
6. (opcionalno) napravite `.env` datoteku:
```
WAYBACK_ACCESS_KEY=AbCd
WAYBACK_SECRET_KEY=AbCd
LOGLEVEL=DEBUG
```
- prekopirajte wayback machine api ključeve odavde: https://archive.org/account/s3.php  
loglevel može biti DEBUG, INFO, ...
6. `sudo chmod +x launch_server.sh`
7. `./launch_server.sh`

server je sada dostupan na internom portu 16163, dodajte to u nginx (ili ekvivalentan program)

za gledanje logova:
```
docker logs -f cijeneorg
```

za cronjob:
1. `crontab -e`  (i dalje kao isti user!)
2. dodajte liniju:
```
5 8,20 * * * /usr/bin/flock -n /tmp/cijeneorg.lock /REPOSITORY/launch_server.sh >> /REPOSITORY/cron.log 2>&1
```
ovo će restartati server svaki dan u 8:05 i 20:05. **sve trgovine ažuriraju cjenike do 8:00**. promijenite ovo vrijeme u cronjobu po želji, **pripazite na vremenske zone** ovisno o tome gdje se vaš server nalazi    
naravno `/REPOSITORY/` zamijenite putanjem do direktorija gdje ste klonirali repo
