from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, update, delete
from .. import schemas, models
from .. database import get_db
from .. oauth2 import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)
# we return list posts becouse RM is List
@router.get("/", status_code=status.HTTP_200_OK,
            response_model=list[schemas.PostVote])
async def get_posts(db: AsyncSession = Depends(get_db), 
                    curent_user: schemas.TokenData = Depends(get_current_user),
                    limit: int = 10, skip: int = 0,
                    search: str | None = ""):
    query = (select(models.Post, func.count(models.Vote.post_id).label("votes"))
                .join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True)
                .where(models.Post.title.contains(search))
                .limit(limit)
                .group_by(models.Post.id))
    async with db.begin():
        req = await db.execute(query)

    data = req.fetchall()
    posts = [post for post in data]

    return posts
# ---------------------------
    
# create all posts
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_posts(post: schemas.PostCreate,
                       session: AsyncSession = Depends(get_db), 
                       curent_user: schemas.TokenData = Depends(get_current_user)):
    new_post = models.Post(owner_id=curent_user.id, **post.dict())
    async with session.begin():
        session.add(new_post)
        await session.flush()
        
    return new_post
# ---------------------------

# get one post with id
@router.get("/{id}", response_model=schemas.PostVote)
async def get_post(id: int, db: AsyncSession = Depends(get_db), 
                   curent_user: int = Depends(get_current_user)):
    
    query = (select(models.Post, func.count(models.Vote.post_id).label("votes"))
            .join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True)
            .where(models.Post.id == id)
            .group_by(models.Post.id))
    async with db.begin():
        data = await db.execute(query)
    post = data.fetchone()
    print(post)

    return post
# ---------------------------

# delete post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: AsyncSession = Depends(get_db),
                      curent_user: schemas.TokenData = Depends(get_current_user)):
    query = select(models.Post).where(models.Post.id == id)
    
    async with db.begin():
        
        delete_post = await db.execute(query)
        
        data = delete_post.fetchone()
        if data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"post with id: {id} was not found")
        post: models.Post = data[0]
    
        if post.owner_id != curent_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"Not authorized to delete")
        await db.delete(post)
        await db.flush()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
# ---------------------------

# update post
@router.put("/{id}", response_model=schemas.PostResponse)
async def update_post(id: int, updated_post: schemas.PostCreate,
                      db: AsyncSession = Depends(get_db),
                      curent_user: schemas.TokenData = Depends(get_current_user)):
    
    query = (select(models.Post)
             .where(models.Post.id == id))
    
    q_update = (update(models.Post)
                    .where(models.Post.id == id)
                    .values(updated_post.dict())
                    .returning(models.Post))
    async with db.begin():
        data = await db.execute(query)
        post: models.Post = data.fetchone()[0]
        if post == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not faund {id}")
        if post.owner_id != curent_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail=f"Not authorized to update")
        
        res = await db.execute(q_update)
        new_post = res.fetchone()[0]
        await db.commit()

    return new_post

