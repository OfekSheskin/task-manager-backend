from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth_routes import router as auth_router
from app.routers.task_routes import router as task_routes

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

@app.get("/")
async def root():
    return {"message": "Hello World"}





