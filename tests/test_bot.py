import pytest
from telegram.ext import ApplicationBuilder, CommandHandler
from bot.handlers.start import start

@pytest.mark.asyncio
async def test_start_command():
    """
    Tests the /start command.
    """
    # This is a placeholder for a real test.
    # In a real scenario, you would mock the Telegram API and assert that the correct messages are sent.
    
    # For now, we'll just check that the handler is registered.
    
    application = ApplicationBuilder().token("TEST_TOKEN").build()
    
    # Check if the start handler is registered
    start_handlers = [h for h in application.handlers[0] if isinstance(h, CommandHandler) and h.command == ["start"]]
    
    assert len(start_handlers) > 0
