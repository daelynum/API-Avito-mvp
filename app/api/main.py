from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import uvicorn
from Token_oath import create_access_token
from routers import user, admin
from hashing import Hash
from models import Users
from database import get_db, engine, Base

app = FastAPI()

app.include_router(user.router)
app.include_router(admin.router)


@app.post('/login', tags=['Login'])
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.email == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Invalid Credentials")
    if not Hash.verify(user.password_hash, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Incorrect password")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host='127.0.0.1', port=8000)
