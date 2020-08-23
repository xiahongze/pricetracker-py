from fastapi import FastAPI
from starlette.responses import RedirectResponse

from .api.page import router as page_router
from .api.price import router as price_router
from .api.user import router as user_router
from .api.website_config import router as config_router
from .config import config

app = FastAPI(
    debug=config.debug,
    title="Price Tracker API",
    version="0.1.0",
    description="Track Price That Matters"
)


@app.get("/", summary="OpenAPI docs", tags=["Home"])
def home():
    return RedirectResponse("/docs")


app.include_router(user_router, prefix='/user',  tags=['User'])
app.include_router(page_router, prefix='/page',  tags=['Page'])
app.include_router(price_router, prefix='/price',  tags=['Price'])
app.include_router(config_router, prefix='/website-config',  tags=['WebsiteConfig'])
