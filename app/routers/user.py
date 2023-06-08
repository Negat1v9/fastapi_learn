from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, models, utils
from .. database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# create new user
@router.post("/", status_code=status.HTTP_201_CREATED,
          response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate,
                      db: AsyncSession = Depends(get_db)):
    
    # hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    async with db.begin():
        db.add(new_user)
        await db.commit()
    return schemas.UserResponse(
        id=new_user.id,
        email=new_user.email,
        created_at=new_user.created_at
)
# ---------------------------

@router.get("/{id}", response_model=schemas.UserResponse)
async def get_user(id: int, db: AsyncSession = Depends(get_db)):
    query = (select(models.User)
            .where(models.User.id == id))
    async with db.begin():
        data = await db.execute(query)
    user = data.fetchone()[0]
    
    # user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id: {id} not difine")
    return user