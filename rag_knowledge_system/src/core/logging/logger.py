"""
Centralized logging system for RAG Knowledge System.

This module provides structured logging with multiple backends,
correlation IDs, and performance monitoring capabilities.
"""

import os
import sys
import json
import uuid
import time
from typing import Any, Dict, Optional, Union
from pathlib import Path
from contextvars import ContextVar
from functools import wraps
from datetime import datetime

import structlog
from loguru import logger as loguru_logger

from src.core.config.settings import get_settings

# Context variables for request tracing
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
user_id: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
request_id: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


def add_correlation_id(logger, method_name, event_dict):
    """Add correlation ID to log entries for tracing."""
    cid = correlation_id.get()
    if cid:
        event_dict['correlation_id'] = cid
    
    uid = user_id.get()
    if uid:
        event_dict['user_id'] = uid
    
    rid = request_id.get()
    if rid:
        event_dict['request_id'] = rid
    
    return event_dict


def add_timestamp(logger, method_name, event_dict):
    """Add ISO timestamp to log entries."""
    event_dict['timestamp'] = datetime.utcnow().isoformat()
    return event_dict


def add_process_info(logger, method_name, event_dict):
    """Add process information to log entries."""
    event_dict['process_id'] = os.getpid()
    event_dict['thread_name'] = structlog.stdlib.get_logger().thread.name
    return event_dict


class PerformanceLogger:
    """Context manager for performance logging."""
    
    def __init__(self, operation_name: str, logger: Any = None):
        self.operation_name = operation_name
        self.logger = logger or get_logger(__name__)
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(
            "operation_started",
            operation=self.operation_name,
            timestamp=datetime.utcnow().isoformat()
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type:
            self.logger.error(
                "operation_failed",
                operation=self.operation_name,
                duration_seconds=duration,
                error_type=exc_type.__name__,
                error_message=str(exc_val),
                timestamp=datetime.utcnow().isoformat()
            )
        else:
            self.logger.info(
                "operation_completed",
                operation=self.operation_name,
                duration_seconds=duration,
                timestamp=datetime.utcnow().isoformat()
            )


def performance_logger(operation_name: Optional[str] = None):
    """Decorator for automatic performance logging."""
    def decorator(func):
        op_name = operation_name or f"{func.__module__}.{func.__name__}"
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            with PerformanceLogger(op_name):
                return func(*args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with PerformanceLogger(op_name):
                return await func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
    return decorator


def setup_logging():
    """Configure the logging system with multiple backends."""
    settings = get_settings()
    
    # Ensure log directory exists
    log_dir = Path(settings.storage.logs_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        add_correlation_id,
        add_timestamp,
        add_process_info,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if settings.is_development:
        # Pretty printing for development
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        # JSON formatting for production
        processors.append(structlog.processors.JSONRenderer())
    
    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure loguru for file logging
    loguru_logger.remove()  # Remove default handler
    
    # Console handler
    if settings.debug:
        loguru_logger.add(
            sys.stdout,
            level=settings.log_level,
            format="<green>{time}</green> | <level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            colorize=True
        )
    
    # File handlers
    loguru_logger.add(
        log_dir / "app.log",
        level=settings.log_level,
        format="{time} | {level} | {name}:{function}:{line} | {message}",
        rotation="100 MB",
        retention="30 days",
        compression="gz",
        serialize=not settings.debug,
    )
    
    # Error file handler
    loguru_logger.add(
        log_dir / "errors.log",
        level="ERROR",
        format="{time} | {level} | {name}:{function}:{line} | {message}",
        rotation="10 MB",
        retention="90 days",
        compression="gz",
        serialize=True,
    )
    
    # Performance log handler
    loguru_logger.add(
        log_dir / "performance.log",
        level="INFO",
        format="{time} | {level} | {message}",
        rotation="50 MB",
        retention="7 days",
        compression="gz",
        filter=lambda record: "operation_" in record["message"],
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name, defaults to caller's module name
        
    Returns:
        Configured structlog logger
    """
    if not structlog.is_configured():
        setup_logging()
    
    return structlog.get_logger(name)


def set_correlation_id(cid: str = None) -> str:
    """Set correlation ID for request tracing."""
    if not cid:
        cid = str(uuid.uuid4())
    correlation_id.set(cid)
    return cid


def set_user_id(uid: str) -> None:
    """Set user ID for request tracing."""
    user_id.set(uid)


def set_request_id(rid: str = None) -> str:
    """Set request ID for request tracing."""
    if not rid:
        rid = str(uuid.uuid4())
    request_id.set(rid)
    return rid


class LoggingMiddleware:
    """Middleware for automatic request logging."""
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger(__name__)
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Set up request tracing
        rid = set_request_id()
        cid = set_correlation_id()
        
        start_time = time.time()
        
        # Log request start
        self.logger.info(
            "request_started",
            method=scope["method"],
            path=scope["path"],
            query_string=scope["query_string"].decode(),
            client_host=scope["client"][0] if scope["client"] else None,
        )
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Log response
                duration = time.time() - start_time
                self.logger.info(
                    "request_completed",
                    method=scope["method"],
                    path=scope["path"],
                    status_code=message["status"],
                    duration_seconds=duration,
                )
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


# Initialize logging on import
setup_logging()

# Export main components
__all__ = [
    "get_logger",
    "setup_logging",
    "PerformanceLogger",
    "performance_logger",
    "set_correlation_id",
    "set_user_id", 
    "set_request_id",
    "LoggingMiddleware",
]