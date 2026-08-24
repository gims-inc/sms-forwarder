import logging
import time
from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncContextManager, AsyncGenerator, Callable, Self

from fastapi import FastAPI, Request

from api.health import router as health_router
from api.sms.router import router as sms_router

logger = logging.getLogger("sms.app")


class AppBuilder:
    def __init__(self) -> None:
        self._lifespan_managers: list[Callable[[FastAPI], AsyncContextManager]] = []

    def add_lifespan_manager(
        self, value: Callable[[FastAPI], AsyncContextManager]
    ) -> Self:
        self._lifespan_managers.append(value)
        return self

    def add_sync_lifespan_function(self, value: Callable[[FastAPI], None]) -> Self:
        @asynccontextmanager
        async def sync_lifespan_wrapper(app: FastAPI) -> AsyncGenerator:
            value(app)
            yield

        self._lifespan_managers.append(sync_lifespan_wrapper)
        return self

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI) -> AsyncGenerator:
        async with AsyncExitStack() as stack:
            for manager in self._lifespan_managers:
                await stack.enter_async_context(manager(app))
            yield

    def build(self) -> FastAPI:
        app = FastAPI(title="SMS Forwarder", lifespan=self._lifespan)

        @app.middleware("http")
        async def log_requests(request: Request, call_next):
            start = time.perf_counter()
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                "request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )
            return response

        app.include_router(health_router)
        app.include_router(sms_router)
        return app
