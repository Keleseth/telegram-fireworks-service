from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

# from src.database import alembic_models  # noqa
from sqlalchemy.orm import configure_mappers

from src.admin.config import setup_admin
from src.api.v1.router import main_router
from src.config import settings
from src.database.db_dependencies import engine
from src.utils.scheduler.scheduler import setup_scheduler, shutdown_scheduler

configure_mappers()
admin_app = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global admin_app
    setup_scheduler()
    admin_app = await setup_admin(app)
    yield
    shutdown_scheduler()
    await engine.dispose()


app = FastAPI(
    title=settings.app_title,
    description=settings.description,
    lifespan=lifespan,
)

# Добавляем middleware для перенаправления HTTP на HTTPS
#@app.middleware("http")
#async def redirect_to_https(request: Request, call_next):
#    if request.headers.get("x-forwarded-proto", "http") == "http":
#        # Если запрос пришел по HTTP, перенаправляем на HTTPS
#        url = request.url.replace(scheme="https")
#        response = Response(status_code=307)
#        response.headers["Location"] = str(url)
#        return response
#    return await call_next(request)


@app.middleware('http')
async def check_http(request: Request, call_next):  # noqa: ANN001, ANN201
    """Проверка протокола."""
    protocol = request.headers.get('X-Forwarded-Protocol', None)
    if protocol in ('http', 'https'):
        request.scope['scheme'] = protocol
    return await call_next(request)



# setup_admin(app)
app.router.include_router(main_router)

#app.mount("/statics/admin", StaticFiles(directory="/app/statics/admin"), name="static_admin")

def main():
    """Функция запустит управляющую функцию. Для доступа извне."""
    pass


if __name__ == '__main__':
    main()
