"""
FreedomWalletBot Handlers Package

This package contains all Telegram bot handlers organized by feature.

Structure:
- user/: User-facing handlers (start, onboarding, registration, quick_record)
- premium/: Premium feature handlers (unlock flow, VIP commands)
- sheets/: Google Sheets integration handlers
- admin/: Admin panel handlers (metrics, fraud, payment)
- engagement/: User engagement handlers (reminders, celebrations, streaks)
- support/: Support handlers (tutorials, setup guides)
- core/: Core functionality handlers (message routing, callbacks, webapp)

LAW #1: Handlers only do Input → Service → Output
- Parse user input
- Call service layer (no direct database/API calls)
- Format and send response
"""

__all__ = []

