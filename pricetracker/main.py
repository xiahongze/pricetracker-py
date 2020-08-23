from fastapi import FastAPI
from starlette.responses import RedirectResponse

from .api.user import router as user_router
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


app.include_router(user_router, tags=['User'])
