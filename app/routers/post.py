from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
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
async def get_posts(db: Session = Depends(get_db), 
                    curent_user: schemas.TokenData = Depends(get_current_user),
                    limit: int = 10, skip: int = 0,
                    search: str | None = ""):
    
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
            models.Post.id).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    return posts
# ---------------------------
    
# get all posts
@router.post("/", status_code=status.HTTP_201_CREATED,
          response_model=schemas.PostResponse)
async def create_posts(post: schemas.PostCreate,
                       db: Session = Depends(get_db), curent_user: schemas.TokenData = 
                       Depends(get_current_user)):
    new_post = models.Post(owner_id=curent_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post) # -> get back data from db
    
    return new_post
# ---------------------------

# get one post with id
@router.get("/{id}", response_model=schemas.PostVote)
async def get_post(id: int, db: Session = Depends(get_db), 
                   curent_user: int = Depends(get_current_user)):
    
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Post.id == models.Vote.post_id).group_by(
            models.Post.id).filter(models.Post.id == id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not faund")
        
    return post
# ---------------------------

# delete post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Session = Depends(get_db),
                      curent_user: schemas.TokenData = Depends(get_current_user)):
    
    post_query: models.Post = db.query(models.Post).filter(models.Post.id == id)
    post: models.Post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    
    if post.owner_id != curent_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to delete")
        
    post_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
# ---------------------------

# update post
@router.put("/{id}", response_model=schemas.PostResponse)
async def update_post(id: int, updated_post: schemas.PostCreate,
                      db: Session = Depends(get_db),
                      curent_user: schemas.TokenData = Depends(get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post: models.Post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not faund {id}")
    if post.owner_id != curent_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to update")
        
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()

