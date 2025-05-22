from fastapi import APIRouter
from controllers import userController,documentController,saccoMetricController,uploadController,chatController,dashboardController

api_router = APIRouter()


api_router.include_router(userController.router, prefix="/api/v1/users", tags=["Users"])
api_router.include_router(documentController.router, prefix="/api/v1/documents", tags=["Documents"])
api_router.include_router(saccoMetricController.router, prefix="/api/v1/metrics", tags=["Sacco Metrics"])
api_router.include_router(uploadController.router, prefix="/api/v1/upload", tags=["Uploads"])
api_router.include_router(chatController.router, prefix="/api/v1", tags=["Chat"]) 
api_router.include_router(dashboardController.router, prefix="/api/v1/dashboard", tags=["Dashboard"]) 

