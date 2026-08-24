from dotenv import load_dotenv

from api.app_builder import AppBuilder
from api.db.lifespan import database_lifespan
from api.telemetry.lifespan import telemetry_lifespan
from logging_config import configure_logging


load_dotenv()


def main() -> None:
    import uvicorn

    configure_logging()

    app = (
        AppBuilder()
        .add_lifespan_manager(database_lifespan)
        .add_sync_lifespan_function(telemetry_lifespan)
        .build()
    )

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
