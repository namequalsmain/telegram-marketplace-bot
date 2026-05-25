"""Global error handler — catches anything a handler throws so the bot survives."""

import logging

from aiogram import Router
from aiogram.types import ErrorEvent

router = Router(name="errors")
log = logging.getLogger("bot.errors")


@router.errors()
async def on_error(event: ErrorEvent) -> None:
    """Log unhandled handler errors with the originating update for context."""
    log.exception(
        "Unhandled error in handler. Update: %s",
        event.update.model_dump(exclude_none=True),
        exc_info=event.exception,
    )
