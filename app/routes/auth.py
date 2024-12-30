from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.database import User, session_local
from passlib.context import CryptContext
import enum
from pydantic import BaseModel

# creating router
router = APIRouter()

passwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

outh_to_scheme = OAuth2PasswordBearer(tokenUrl="token")

# secret key for JWT
SECRET_KEY = "test_key"
ALGO = "HS256"

# setting designations
class DesignationStateEnum(str, enum.Enum):
    STUDENT = 'STUDENT'
    PROFESSOR = 'PROFESSOR'

# Pydantic models to handle incoming request bodies
class UserCreate(BaseModel):
    user_name: str
    passwd: str
    desigenate: DesignationStateEnum

class UserOut(BaseModel):
    id: int
    user_name: str
    desigenate: DesignationStateEnum
    
# Define the request body schema using Pydantic
class LoginRequest(BaseModel):
    user_name: str
    passwd: str


# function to get database control
def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

# function to hash password
def hash_passwd(passwd: str) -> str:
    return passwd_context.hash(passwd)

def verify_passwd(to_verify: str, hashed_password: str) -> bool:
    return passwd_context.verify(to_verify, hashed_password)

def create_access_token(data: dict) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm=ALGO)

# defining routes

# registration route
@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.user_name).first():
        raise HTTPException(status_code=400, detail="User already exists!!!")
    
    hashed_passwd = hash_passwd(user.passwd)
    new_user = User(username=user.user_name, password=hashed_passwd, designation=user.desigenate)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"id": new_user.id, "user_name": new_user.username, "desigenate": new_user.designation}


# Login route that uses the LoginRequest Pydantic model
@router.post("/login")
def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_request.user_name).first()
    if not user or not verify_passwd(login_request.passwd, user.password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    access_token = create_access_token(data={"sub": user.username, "designation": user.designation})
    return {"access_token": access_token, "token_type": "bearer"}

# function to get the instance of a user (row from the User table)
def get_curr_user(token_str: str = Depends(outh_to_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGO])
        user_name: str = payload.get("sub")
        user = db.query(User).filter(User.username == user_name).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
