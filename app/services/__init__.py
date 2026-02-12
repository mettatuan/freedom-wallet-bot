"""
Business Logic Layer - Services

Services contain business logic extracted from handlers.
Handlers call services, services call models.

Architecture: Handler → Service → Model

Rules:
- NO Telegram imports in services
- NO message formatting in services
- NO abstract base classes
- NO dependency injection containers
- Just plain Python classes with business logic
"""

from app.services.registration_service import (
    RegistrationService,
    RegistrationResult,
)

__all__ = [
    "RegistrationService",
    "RegistrationResult",
]
