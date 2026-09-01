from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth_routes import router as auth_router
from app.routers.task_routes import router as task_routes
from app.routers.friendship_routes import router as friendship_routes
from app.routers.share_routes import router as share_routes
from app.routers.label_routes import router as label_routes
from app.routers.label_routes import task_labels_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(task_routes)
app.include_router(friendship_routes)
app.include_router(share_routes)
app.include_router(label_routes)
app.include_router(task_labels_router)

@app.get("/")
async def root():
    return {"message": "Task Manager API", "docs": "/docs"}





