from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import Settings

from app.main_router import router as main_router
from app.user_router import router as user_router
from app.opa_router import router as opa_router

use_opa: bool = True

settings = Settings()

def get_app() -> FastAPI:
    app = FastAPI(**settings.fastapi_kwargs)
    app.include_router(main_router)
    app.include_router(user_router)
    app.include_router(opa_router)
    return app


app = get_app()

if use_opa:
    from fastapi_opa import OPAConfig
    from fastapi_opa import OPAMiddleware
    from fastapi_opa.auth.auth_api_key import APIKeyConfig, APIKeyAuthentication

    opa_host = "http://localhost:8181"
    # Configure API keys
    api_key_config = APIKeyConfig(
        header_key="test",
        api_key="1234"
    )
    api_key_auth = APIKeyAuthentication(api_key_config)
    opa_config = OPAConfig(authentication=api_key_auth, opa_host=opa_host)
    app.add_middleware(OPAMiddleware, config=opa_config)


app.mount("/", StaticFiles(directory="app/static/dist"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)