from fastapi import APIRouter, HTTPException, status

from routers.user_router.use_api_class import RegisterBody, RegisterResponse
from routers.user_router.user_func import User

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=RegisterResponse)
def register(body: RegisterBody):
    dup = User.check_register_duplicates(body.username, body.email)
    if dup["email"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email 已被使用")
    if dup["username"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username 已被使用")
    row = User.register(body.username, body.email, body.password, body.color)
    return RegisterResponse(id=row["id"], username=row["username"], email=row["email"])
