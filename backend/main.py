import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app
from routes import (
    content_routes, brand_routes as legacy_brand_routes, drift_routes, competitor_routes,
    trend_routes as legacy_trend_routes, prediction_routes, optimization_routes as legacy_opt_routes,
    compliance_routes, report_routes,
)

API_PREFIX = "/api/v1"

app.include_router(content_routes.router, prefix=API_PREFIX)
app.include_router(drift_routes.router, prefix=API_PREFIX)
app.include_router(competitor_routes.router, prefix=API_PREFIX)
app.include_router(prediction_routes.router, prefix=API_PREFIX)
app.include_router(compliance_routes.router, prefix=API_PREFIX)
app.include_router(report_routes.router, prefix=API_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
