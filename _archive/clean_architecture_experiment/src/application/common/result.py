"""Common result types for use cases."""

from typing import TypeVar, Generic, Optional
from dataclasses import dataclass
from enum import Enum


class ResultStatus(str, Enum):
    """Result status for use case execution."""
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"


T = TypeVar('T')


@dataclass
class Result(Generic[T]):
    """
    Generic result type for use case execution.
    
    Follows Railway Oriented Programming pattern:
    - Success path returns data
    - Failure path returns error message
    """
    
    status: ResultStatus
    data: Optional[T] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    @classmethod
    def success(cls, data: T) -> 'Result[T]':
        """Create a successful result."""
        return cls(status=ResultStatus.SUCCESS, data=data)
    
    @classmethod
    def failure(cls, error_message: str, error_code: Optional[str] = None) -> 'Result[T]':
        """Create a failure result (business logic error)."""
        return cls(
            status=ResultStatus.FAILURE,
            error_message=error_message,
            error_code=error_code
        )
    
    @classmethod
    def error(cls, error_message: str, error_code: Optional[str] = None) -> 'Result[T]':
        """Create an error result (technical error)."""
        return cls(
            status=ResultStatus.ERROR,
            error_message=error_message,
            error_code=error_code
        )
    
    def is_success(self) -> bool:
        """Check if result is successful."""
        return self.status == ResultStatus.SUCCESS
    
    def is_failure(self) -> bool:
        """Check if result is a failure."""
        return self.status == ResultStatus.FAILURE
    
    def is_error(self) -> bool:
        """Check if result is an error."""
        return self.status == ResultStatus.ERROR
    
    def __bool__(self) -> bool:
        """Allow using Result in boolean context (True if success)."""
        return self.is_success()
