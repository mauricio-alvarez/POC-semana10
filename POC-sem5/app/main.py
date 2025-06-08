from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.features.search.routes import router as search_router
from app.features.poke_img.routes import router as image_router  # Optional
from app.core.database import get_supabase
from app.core.logging_config import get_logger, log_execution_time
import time


# Get logger for main API
api_logger = get_logger("pokemon_main_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with logging"""
    start_time = time.time()
    api_logger.info("Starting Pokemon API application")
    
    try:
        # Initialize Supabase connection
        api_logger.info("Initializing Supabase connection")
        get_supabase()
        api_logger.info("Supabase connection initialized successfully")
        
        startup_time = (time.time() - start_time) * 1000
        api_logger.info(f"Application startup completed - Duration: {startup_time:.2f}ms")
        
        yield
        
    except Exception as e:
        api_logger.error(f"Error during application startup: {str(e)}")
        raise
    finally:
        api_logger.info("Shutting down Pokemon API application")

app = FastAPI(
    lifespan=lifespan,
    title="Pokemon API",
    description="Pokemon API with stats and images",
    version="1.0.0"
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request, call_next):
    """Log all HTTP requests and responses"""
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    method = request.method
    url = str(request.url)
    
    api_logger.info(f"Incoming request - {method} {url} from {client_ip}")
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        api_logger.info(
            f"Request completed - {method} {url} - "
            f"Status: {response.status_code} - Duration: {process_time:.2f}ms"
        )
        
        # Add custom header with response time
        response.headers["X-Process-Time"] = str(process_time)
        return response
        
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        api_logger.error(
            f"Request failed - {method} {url} - "
            f"Error: {str(e)} - Duration: {process_time:.2f}ms"
        )
        raise

# Include routers with logging
api_logger.info("Registering search router at /poke")
app.include_router(search_router, prefix="/poke")

api_logger.info("Registering image router")
app.include_router(image_router)

# Mount static files with logging
api_logger.info("Mounting static files at /images")
app.mount("/images", StaticFiles(directory="app/static/images"), name="images")

# extra endpoints
@app.get("/health")
@log_execution_time(api_logger)
async def health_check():
    """Health check endpoint with logging"""
    api_logger.info("Health check requested")
    
    try:
        # Test database connection
        supabase = get_supabase()
        api_logger.info("Database connection test successful")
        
        return {
            "status": "healthy",
            "service": "pokemon-api",
            "database": "connected",
            "timestamp": time.time()
        }
    except Exception as e:
        api_logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "pokemon-api",
            "database": "disconnected",
            "error": str(e),
            "timestamp": time.time()
        }

# Root endpoint
@app.get("/")
@log_execution_time(api_logger)
async def root():
    """Root endpoint with basic API information"""
    api_logger.info("Root endpoint accessed")
    return {
        "message": "Pokemon API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/poke/{pokemon_name}",
            "image": "/image/{pokemon_name}",
            "health": "/health",
            "docs": "/docs"
        }
    }

# Startup event logging
@app.on_event("startup")
async def startup_event():
    """Log startup completion"""
    api_logger.info("FastAPI application startup event completed")

# Shutdown event logging
@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown initiation"""
    api_logger.info("FastAPI application shutdown event initiated")