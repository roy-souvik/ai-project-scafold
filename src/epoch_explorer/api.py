from fastapi import FastAPI
from epoch_explorer.routes import health_router

app = FastAPI(
    title="API Service",
    description="API Service to support AI powered apps",
    version="1.0.0"
)

# Include routers
app.include_router(health_router)