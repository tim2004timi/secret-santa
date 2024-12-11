import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Этот объект конфигурации Alembic предоставляет доступ к значениям в .ini файле.
config = context.config

# Настройка логирования из конфигурационного файла
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Импорт ваших моделей
from src.main import Base
from src.config import settings

target_metadata = Base.metadata

# Установка строки подключения для SQLite
config.set_main_option(
    "sqlalchemy.url",
    f"sqlite+aiosqlite:///{settings.db_name}",
)


def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
