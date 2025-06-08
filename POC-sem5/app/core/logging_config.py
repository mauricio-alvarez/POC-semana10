import logging
import time
from datetime import datetime
from functools import wraps
from typing import Callable
import os

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

class PokemonFormatter(logging.Formatter):
    """Custom formatter for Pokemon API logs"""
    
    def format(self, record):
        # Format: {Fecha}[POKEMON-SERVICE][Module][Function] Message
        timestamp = self.formatTime(record, datefmt='%Y-%m-%d %H:%M:%S')
        module = record.name
        function = record.funcName
        message = record.getMessage()
        
        formatted_message = f"{timestamp} [POKEMON-SERVICE] [{module}] [{function}] {message}"
        
        if record.levelno >= logging.ERROR:
            formatted_message = f"ERROR - {formatted_message}"
        elif record.levelno >= logging.WARNING:
            formatted_message = f"WARN - {formatted_message}"
        elif record.levelno >= logging.INFO:
            formatted_message = f"INFO - {formatted_message}"
        else:
            formatted_message = f"DEBUG - {formatted_message}"
            
        return formatted_message
    
# {Fecha}{Modulo}{API}{Funcion} Message
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [POKEMON-SERVICE] [%(name)s] [%(funcName)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            filename=f"logs/pokemon_api_{datetime.now().strftime('%Y%m%d')}.log",
            mode='a',
            encoding='utf-8'
        )
    ]
)

# Apply custom formatter to all handlers
for handler in logging.root.handlers:
    handler.setFormatter(PokemonFormatter())

def get_logger(module_name: str):
    """Get logger for specific module"""
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)
    return logger

def log_execution_time(logger: logging.Logger):
    """Decorator to log execution time for latency measurement"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            function_name = func.__name__
            logger.info(f"Starting execution - {function_name}")
            
            try:
                result = await func(*args, **kwargs)
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
                logger.info(f"Completed execution - {function_name} - Duration: {execution_time:.2f}ms")
                return result
            except Exception as e:
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000
                logger.error(f"Failed execution - {function_name} - Duration: {execution_time:.2f}ms - Error: {str(e)}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            function_name = func.__name__
            logger.info(f"Starting execution - {function_name}")
            
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000
                logger.info(f"Completed execution - {function_name} - Duration: {execution_time:.2f}ms")
                return result
            except Exception as e:
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000
                logger.error(f"Failed execution - {function_name} - Duration: {execution_time:.2f}ms - Error: {str(e)}")
                raise
        
        # Check if function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator

# Utility function to log database operations
def log_database_operation(logger: logging.Logger, operation: str, table: str, params: dict = None):
    """Log database operations with standardized format"""
    params_str = f" with params: {params}" if params else ""
    logger.info(f"Database operation - {operation} on table '{table}'{params_str}")

# Utility function to log API responses
def log_api_response(logger: logging.Logger, endpoint: str, status_code: int, response_size: int = None):
    """Log API responses with standardized format"""
    size_str = f" - Size: {response_size} bytes" if response_size else ""
    logger.info(f"API response - {endpoint} - Status: {status_code}{size_str}")

# Performance monitoring utilities
class PerformanceMonitor:
    """Context manager for performance monitoring"""
    
    def __init__(self, logger: logging.Logger, operation_name: str):
        self.logger = logger
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting operation - {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        execution_time = (end_time - self.start_time) * 1000
        
        if exc_type:
            self.logger.error(f"Operation failed - {self.operation_name} - Duration: {execution_time:.2f}ms - Error: {exc_val}")
        else:
            self.logger.info(f"Operation completed - {self.operation_name} - Duration: {execution_time:.2f}ms")


config_logger = get_logger("logging_config")
config_logger.info("Pokemon API logging system initialized")
config_logger.info(f"Log files will be saved to: logs/pokemon_api_{datetime.now().strftime('%Y%m%d')}.log")
config_logger.info("Logging format: {Fecha}[POKEMON-SERVICE][Module][Function] Message")