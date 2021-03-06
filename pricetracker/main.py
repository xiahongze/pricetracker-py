from threading import Thread

from fastapi import FastAPI
from starlette.responses import RedirectResponse

from .api.page import router as page_router
from .api.price import router as price_router
from .api.user import router as user_router
from .api.utils import router as utils_router
from .api.website_config import router as config_router
from .config import config, logger
from .task import check_db_in_loop
from .version import VERSION

app = FastAPI(
    debug=config.debug,
    title="Price Tracker API",
    version=VERSION,
    description="Track Prices That Matter"
)


@app.get("/", summary="OpenAPI docs", tags=["Home"])
def home():
    return RedirectResponse("/docs")


app.include_router(user_router, prefix='/user',  tags=['User'])
app.include_router(page_router, prefix='/page',  tags=['Page'])
app.include_router(price_router, prefix='/price',  tags=['Price'])
app.include_router(config_router, prefix='/website-config',  tags=['WebsiteConfig'])
app.include_router(utils_router, prefix='/utils',  tags=['Utils'])


@app.on_event("startup")
def on_startup():
    logger.info(f"version={VERSION}")
    logger.info("starting background tasks...")
    t = Thread(target=check_db_in_loop, daemon=True)
    t.start()
    logger.info("done...")
