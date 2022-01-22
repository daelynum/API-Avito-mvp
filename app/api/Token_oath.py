from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "66b3bf352919ec6608c0e8cca7a9a0354cd0820156d4851e6a253f189e7a538b"  # генерирую  с openssl rand -hex 32
ALGORITHM = "HS256"


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
