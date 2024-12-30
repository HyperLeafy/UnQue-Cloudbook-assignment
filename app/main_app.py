from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.routes.professor import router as proff_router
from app.routes.student import router as student_router
from app.database import db_engine, db_init


# initialize app
app = FastAPI()

# create all database tables
db_init()

# adding all routes 
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(proff_router, prefix="/professor", tags=["Professor"])
app.include_router(student_router, prefix="/student", tags=["Student"])

# system status endpoint
@app.get("/")
def read_root():
    return {"message": "Server is Live"}, 200
