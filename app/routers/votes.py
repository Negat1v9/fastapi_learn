from fastapi import APIRouter, status, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete

from .. import schemas, database, models, oauth2

router = APIRouter(
    prefix="/vote",
    tags=["Vote"],
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def vote(vote: schemas.Vote,
               db: AsyncSession = Depends(database.get_db),
               current_user: schemas.TokenData = Depends(
                   oauth2.get_current_user)):
    # query to select Post and check is None
    query = (select(models.Post)
            .where(models.Post.id == vote.post_id))
    # open connect database
    async with db.begin():
        # check post in db
        data = await db.execute(query)
        
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {vote.post_id} not found")
        # query to select vote
        vote_query = (select(models.Vote)
                    .where(and_(models.Vote.user_id == current_user.id,
                                models.Vote.post_id == vote.post_id)))

        # get vote from db
        vote_data = await db.execute(vote_query)
        # finded vote
        found_vote = vote_data.fetchone()
        # add vote in database 
        if vote.dir == 1:
            # if user is alredy veted
            if found_vote:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                    detail=f"user {current_user.id} has already voted on post {vote.post_id}")
                
            new_vote = models.Vote(post_id=vote.post_id,
                                   user_id=current_user.id)
            db.add(new_vote)
            await db.flush()
            return {"message": "Vote is succsesfuly added"}
        # if user unvote on post
        else:
            # if user want unvote to aldredy unvoted
            if not found_vote:
                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail=f"Vote does not exist")
            # query to delete vote
            q_delete = (delete(models.Vote)
                        .where(and_(models.Vote.post_id == vote.post_id,
                                    models.Vote.user_id == current_user.id)))
            await db.execute(q_delete)
            await db.flush()
            return {"message": "Vote is succsesfuly deleted"}
            
