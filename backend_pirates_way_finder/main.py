from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import admin_edge_router, admin_node_router, search_router
from app.routers import building_router
from app.routers import pathfinding_router
from app.routers import auth_router, map_data_router
from app.routers import rating_router, audit_log_router, notification_router
from app.core.grid_loader import grid_instance
from app.routers.path_router import router as path_router

app = FastAPI()

# Add CORS middleware to allow frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development. Restrict in production!
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.include_router(search_router.router)
app.include_router(building_router.router, prefix="/api", tags=["Buildings"])
app.include_router(pathfinding_router.router)
app.include_router(auth_router.router, prefix="/auth")
app.include_router(map_data_router.router, prefix="/map", tags=["Map Data"])
app.include_router(admin_node_router.router, prefix="/admin/nodes", tags=["Admin Nodes"])
app.include_router(admin_edge_router.router, prefix="/admin/edges", tags=["Admin Edges"])
app.include_router(rating_router.router, prefix="/ratings", tags=["Ratings"])
app.include_router(audit_log_router.router, prefix="/admin/audit-logs", tags=["Audit Logs"])
app.include_router(notification_router.router, prefix="/admin/notifications", tags=["Notifications"])
app.include_router(path_router)

@app.get("/")
def root():
    return {"message": "Pirates Way Finder Backend is running!"}

@app.on_event("startup")
def load_grid():
    print("🔄 Loading grid data...")
    try:
        grid_instance.load("app/static/grid.json")
        print(f"✅ Grid loaded: {grid_instance.w}x{grid_instance.h} cells")
        print(f"   Cell size: {grid_instance.cell_size}px")
    except Exception as e:
        print(f"❌ ERROR loading grid: {e}")
        print("⚠️  Pathfinding will NOT work without grid!")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Pirates Way Finder Backend...")
    print("📡 Listening on: http://0.0.0.0:8000")
    print("🌐 Access from network: http://[YOUR_IP]:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
