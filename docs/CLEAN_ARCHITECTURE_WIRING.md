"""Example: How to wire Clean Architecture handlers in main.py"""

# === Add these imports at the top of main.py ===
from src.infrastructure.di_container import initialize_container
from src.infrastructure.database import init_db
from src.presentation.handlers import (
    start_command,
    start_sheet_setup,
    receive_email,
    receive_phone,
    receive_sheet_url,
    receive_webapp_url,
    cancel_setup,
    AWAITING_EMAIL,
    AWAITING_PHONE,
    AWAITING_SHEET_URL,
    AWAITING_WEBAPP_URL,
    quick_record_transaction,
    balance_command,
    recent_transactions_command
)


# === Inside main() function, AFTER creating application ===
def main_with_clean_architecture():
    """Example of main() with Clean Architecture."""
    
    # Create application
    application = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )
    
    # === NEW: Initialize Clean Architecture ===
    
    # 1. Initialize database
    init_db()
    
    # 2. Initialize DI Container
    initialize_container(
        bot=application.bot,
        google_credentials_file="google_service_account.json",
        openai_api_key=settings.OPENAI_API_KEY,
        openai_model="gpt-4"
    )
    
    # === Register Clean Architecture Handlers ===
    
    # Start command
    application.add_handler(CommandHandler("start", start_command))
    
    # Sheet setup conversation
    from telegram.ext import ConversationHandler
    setup_conversation = ConversationHandler(
        entry_points=[
            CommandHandler("setup", start_sheet_setup),
            CallbackQueryHandler(start_sheet_setup, pattern="^setup_sheet$")
        ],
        states={
            AWAITING_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email)],
            AWAITING_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)],
            AWAITING_SHEET_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_sheet_url)],
            AWAITING_WEBAPP_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_webapp_url)],
        },
        fallbacks=[CommandHandler("cancel", cancel_setup)]
    )
    application.add_handler(setup_conversation)
    
    # Balance and recent transactions
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("recent", recent_transactions_command))
    
    # Quick transaction recording (catch-all message handler)
    # NOTE: This should be added LAST, with lower priority
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            quick_record_transaction
        ),
        group=10  # Lower priority group
    )
    
    # === Keep existing handlers (for backward compatibility) ===
    # ... existing handlers ...
    
    # Start bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


# === Benefits of Clean Architecture ===
"""
1. ✅ Testable - Use cases tested independently
2. ✅ Maintainable - Clear separation of concerns
3. ✅ Flexible - Easy to add new features
4. ✅ Database-agnostic - Repository pattern
5. ✅ Type-safe - DTOs with dataclasses
6. ✅ Error handling - Result type for clear success/failure

Old way:
    await save_user_to_db(user)  # Direct database access
    
New way:
    container = get_container()
    use_case = container.get_register_user_use_case(session)
    result = await use_case.execute(input_dto)
    
    if result.is_success():
        user_dto = result.data.user
"""
