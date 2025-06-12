import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
from starlette.responses import JSONResponse
from starlette.types import Scope

from cijeneorg.fetchers.archiver import LocalArchiver, WaybackArchiver
from cijeneorg.products_api import demo
from cijeneorg.utils import stylize_unit_price

templates = Jinja2Templates(directory='templates')
templates.env.filters['formatted_price'] = lambda x: f'{x:.2f} €' if x is not None else '-'
templates.env.globals['stylize'] = stylize_unit_price
templates.env.globals['_'] = __import__('builtins')
TemplateResponse = templates.TemplateResponse

logger.remove()
logger.add(
    sink=sys.stdout, level=os.getenv('LOGLEVEL', 'INFO'),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <magenta>{thread.name}</magenta> | <cyan>{name}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
)

async def _404handler(request: Request, exc: HTTPException):
    return TemplateResponse('_base.html', {'request': request}, status_code=404)


@asynccontextmanager
async def fastapi_lifespan(_app: FastAPI):
    logger.info('Starting FastAPI application')
    yield
    logger.info('Stopping...')
    LocalArchiver.shutdown()
    WaybackArchiver.shutdown()

class CacheControl(StaticFiles):
    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        if path.endswith('.js') or path.endswith('.css'):
            response.headers['Cache-Control'] = 'public, max-age=600'  #, immutable'
        return response

app = FastAPI(docs_url=None, lifespan=fastapi_lifespan, exception_handlers={404: _404handler})
app.provider = None
app.mount('/static', StaticFiles(directory='static'), name='static')
provider = demo()


@app.get('/')
async def read_root(request: Request):
    return TemplateResponse('index.html', {'request': request})

@app.get('/api/storelocations')
async def storelocs(request: Request):
    return JSONResponse([s.locations for s in provider._stores])


@app.get('/{page}')
async def read_page(request: Request, page: str):
    if page == 'robots.txt':
        return Response('User-agent: *\nDisallow: /', media_type='text/plain')
    if page in {'blog', 'contact', 'products'}:
        if Path(f'templates/{page}.html').is_file():
            return TemplateResponse(f'{page}.html', {'request': request, 'products': provider.products_by_id.values()})
    raise HTTPException(status_code=404)


@app.get('/product/{proizvod_id}')
async def read_product_page(request: Request, proizvod_id: str):
    if product := provider.products_by_id.get(proizvod_id):
        offers = provider.get_offers_by_product(product)
        return TemplateResponse('product_page.html', {
            'request': request, 'product': product, 'offers': offers
        })
    raise HTTPException(status_code=404)
