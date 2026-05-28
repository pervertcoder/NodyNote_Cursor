from fastapi import APIRouter, HTTPException, Request, Response, status

from routers.user_router.use_api_class import (
    LoginBody,
    LoginResponse,
    MeResponse,
    RegisterBody,
    RegisterResponse,
)
from routers.user_router.user_db import (
    delete_session,
    delete_sessions_by_user_id,
    get_user_by_email,
    get_user_id_by_session_id,
    get_user_public_by_id,
)
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


@router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponse)
def login(request: Request, response: Response, body: LoginBody):
    row = get_user_by_email(body.email)
    if (not row) or (not User.verify_password(body.password, row["password_hash"])):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="帳號或密碼錯誤")

    delete_sessions_by_user_id(row["id"])
    session = User.create_session(
        user_id=row["id"],
        user_agent=request.headers.get("user-agent"),
    )
    response.set_cookie(
        key="session_id",
        value=session["session_id"],
        httponly=True,
        samesite="lax",
    )
    return LoginResponse(message="ok")


@router.get("/me", status_code=status.HTTP_200_OK, response_model=MeResponse)
def me(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登入")
    user_id = get_user_id_by_session_id(session_id)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登入")
    row = get_user_public_by_id(user_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登入")
    return MeResponse(**row)


@router.delete("/logout", status_code=status.HTTP_200_OK)
def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id:
        delete_session(session_id)
    response.delete_cookie("session_id")
    return {"message": "ok"}
