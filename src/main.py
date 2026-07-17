from fastapi import FastAPI

from routes import (
    movie_router,
    accounts_router,
    profiles_router,
    users_activity_router
)
from lifespan import lifespan

app = FastAPI(
    title="Movies homework",
    description="Description of project",
    lifespan=lifespan
)

api_version_prefix = "/api/v1"

app.include_router(accounts_router, prefix=f"{api_version_prefix}/accounts", tags=["accounts"])
app.include_router(profiles_router, prefix=f"{api_version_prefix}/profiles", tags=["profiles"])
app.include_router(movie_router, prefix=f"{api_version_prefix}/theater", tags=["theater"])
app.include_router(users_activity_router, prefix=f"{api_version_prefix}/activity", tags=["activity"])
