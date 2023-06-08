from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import post, user, auth, votes


app: FastAPI = FastAPI(title="Test app")

# origins = ["http://localhost",
#            "http://localhost:8000"]

# app.add_middleware(
#     CORSMiddleware, 
#     allow_origins=["*"], 
#     allow_credentials=True, 
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(votes.router)

# ---------------------------
@app.get("/")
async def root():
    return {"message": "Hello"}    

