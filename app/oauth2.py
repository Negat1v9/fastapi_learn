from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from datetime import datetime, timedelta

from . config import settings
from . schemas import TokenData
from . database import get_db
from . import models


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#SECRET_KEY
#Algorithm
#Expretiation time

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTS = settings.access_token_minuts

def create_access_token(data: dict):
    
    copy_data = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTS)
    
    copy_data.update({"exp": expire})
    encoded_jwt = jwt.encode(copy_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt
    
def verify_access_token(token: str, creadentils_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        
        id = payload.get("user_id")
        if id is None:
            raise creadentils_exception
        token_data = TokenData(id=id)
    except JWTError:
        raise creadentils_exception
    return token_data
    
async def get_current_user(token: str = Depends(oauth2_scheme), 
                     db: AsyncSession = Depends(get_db)) -> TokenData:
    
    credentical_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Could not validate credentials",
                            headers={"WWW-Authencicate": "Bearer"})
    
    current_token = verify_access_token(token, credentical_exception)
    query = select(models.User).where(models.User.id == current_token.id)
    async with db.begin():
        user_req = await db.execute(query)
    # print(query)
    user: TokenData = user_req.fetchone()
    # user: TokenData = db.query(User).filter(User.id == current_token.id).first()
    return user[0]
    