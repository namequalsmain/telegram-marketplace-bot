"""Bot entry point.

Wires together middlewares, routers, and starts polling.
"""

import asyncio
import logging

from bot import errors
from bot.admin import (
    broadcast as admin_broadcast,
)
from bot.admin import (
    catalog_edit as admin_catalog,
)
from bot.admin import (
    handlers as admin_handlers,
)
from bot.admin import (
    settings as admin_settings,
)
from bot.admin import (
    stats as admin_stats,
)
from bot.admin import (
    users as admin_users,
)
from bot.loader import bot, dp
from bot.logging_setup import setup_logging
from bot.middlewares import (
    DbSessionMiddleware,
    SubscriptionMiddleware,
    UserMiddleware,
)
from bot.user import (
    catalog as user_catalog,
)
from bot.user import (
    handlers as user_handlers,
)
from bot.user import (
    payments as user_payments,
)
from database.session import seed_defaults_and_bootstrap_admin

log = logging.getLogger("bot.main")


def _setup_middlewares() -> None:
    """Outer middlewares run BEFORE filters — needed because IsAdmin filter uses `session`.

    Order: db (provides session) → user (fetches User, blocks banned) → subscription.
    """
    for kind in (dp.message, dp.callback_query, dp.pre_checkout_query):
        kind.outer_middleware(DbSessionMiddleware())
    for kind in (dp.message, dp.callback_query):
        kind.outer_middleware(UserMiddleware())
        kind.outer_middleware(SubscriptionMiddleware())


def _setup_routers() -> None:
    # Admin routers go first so IsAdmin-filtered handlers win over user ones.
    dp.include_routers(
        errors.router,
        admin_handlers.router,
        admin_catalog.router,
        admin_broadcast.router,
        admin_stats.router,
        admin_users.router,
        admin_settings.router,
        user_handlers.router,
        user_catalog.router,
        user_payments.router,
    )


async def main() -> None:
    setup_logging()
    log.info("Starting bot")
    await seed_defaults_and_bootstrap_admin()
    _setup_middlewares()
    _setup_routers()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Bot stopped")
