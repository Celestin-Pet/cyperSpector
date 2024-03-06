from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uvicorn
from datetime import datetime, timedelta
from jose import JWTError, jwt

from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
import secrets

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()


SECRET_KEY = secrets.token_urlsafe(32)

# FastAPI setup
app = FastAPI()

# CORS setup
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./csirts.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Generate a random secret key
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database models
class CSIRT(Base):
    __tablename__ = "csirts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    contacts = Column(String)


Base.metadata.create_all(bind=engine)

# Pydantic model for CSIRT data
class CSIRTCreate(BaseModel):
    name: str
    location: str
    contacts: str

class CSIRTUpdate(BaseModel):
    name: str
    location: str
    contacts: str

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

# Token authentication function
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Token verification function
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def authenticate_user(username: str, password: str):
    
    if username == "admin" and password == "12123":
        return {"username": username}
    return None

# CRUD operations for CSIRTs
@app.post("/csirts/")
def create_csirt(csirt: CSIRTCreate):
    db = SessionLocal()
    db_csirt = CSIRT(name=csirt.name, location=csirt.location, contacts=csirt.contacts)
    db.add(db_csirt)
    db.commit()
    db.refresh(db_csirt)
    return db_csirt

@app.get("/csirts/{csirt_id}")
def read_csirt(csirt_id: int):
    db = SessionLocal()
    db_csirt = db.query(CSIRT).filter(CSIRT.id == csirt_id).first()
    if db_csirt is None:
        raise HTTPException(status_code=404, detail="CSIRT not found")
    return db_csirt

@app.put("/csirts/{csirt_id}")
def update_csirt(csirt_id: int, csirt: CSIRTUpdate):
    db = SessionLocal()
    db_csirt = db.query(CSIRT).filter(CSIRT.id == csirt_id).first()
    if db_csirt is None:
        raise HTTPException(status_code=404, detail="CSIRT not found")
    db_csirt.name = csirt.name
    db_csirt.location = csirt.location
    db_csirt.contacts = csirt.contacts
    db.commit()
    return db_csirt

@app.delete("/csirts/{csirt_id}")
def delete_csirt(csirt_id: int):
    db = SessionLocal()
    db_csirt = db.query(CSIRT).filter(CSIRT.id == csirt_id).first()
    if db_csirt is None:
        raise HTTPException(status_code=404, detail="CSIRT not found")
    db.delete(db_csirt)
    db.commit()
    return {"message": "CSIRT deleted successfully"}


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
   
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected route 
@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"username": payload.get("sub")}

# Route for the root URL
@app.get("/")
async def read_root():
    return {"message": "Welcome to CSIRTs API"}


@app.get("/favicon.ico")
async def get_favicon():
    return FileResponse("path_to_your_favicon.ico")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=62145)
    
