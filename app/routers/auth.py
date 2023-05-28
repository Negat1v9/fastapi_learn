from fastapi import APIRouter, Depends, status,\
                HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. database import get_db
from .. models import User
from .. oauth2 import create_access_token
from .. utils import verify
from .. schemas import Token

router: APIRouter = APIRouter(tags=["Authentications"])

@router.post("/login")
async def login(user_credentails: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(get_db)):
    
    user = db.query(User).filter(
        User.email == user_credentails.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalidate query")
        
    if not verify(user_credentails.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Data")
    access_token = create_access_token(data= {"user_id": user.id})
    token: Token = Token(access_token=access_token,
                         token_type="bearer")
    
    return token