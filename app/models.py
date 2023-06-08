from sqlalchemy import Column, Integer,\
    String, Boolean, TIMESTAMP, ForeignKey,\
        MetaData, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from .database import Base
        
# metadata = MetaData()

# user = Table(
#     "users",
#     metadata,
#     Column("id", Integer(), primary_key=True, nullable=False, autoincrement="auto"),
#     Column("email",String(), nullable=False, unique=True),
#     Column("password", String(), nullable=False),
#     Column("created_at", TIMESTAMP(timezone=True),
#                         nullable=False, server_default=text("now()"))
# )

# post = Table(
#     "posts",
#     metadata,
    
# )

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer(), primary_key=True, nullable=False, autoincrement="auto")
    email = Column(String(), nullable=False, unique=True)
    password = Column(String(), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer(), primary_key=True, nullable=False, autoincrement="auto")
    title = Column(String(), nullable=False)
    content = Column(String(), nullable=False)
    published = Column(Boolean(), server_default="TRUE", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    owner_id = Column(Integer() ,ForeignKey(User.id, ondelete="CASCADE"),
                      nullable=False)
    owner = relationship("User")
    
class Vote(Base):
    __tablename__ = "votes"
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey(
        "posts.id", ondelete="CASCADE"), primary_key=True)