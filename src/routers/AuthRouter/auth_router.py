from typing import Optional
from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import SessionLocal
from ..User import crud_user
from ..User import user_schemas
from src.database import get_db

app = FastAPI()
router = APIRouter(
    prefix="/authentication",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)


@router.post('/login', response_model=user_schemas.UserLoginDTO)
async def authentication(model: user_schemas.UserAuthenticationDTO, db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    user = await crud_user.get_user_by_email(db, model.email)
    if (user and model.password != user.password) or not user:
        raise HTTPException(status_code=401, detail="Bad username or password")
    user.access_token = await Authorize.create_access_token(subject=user.id)
    user.refresh_token = await Authorize.create_refresh_token(subject=user.id)
    return user




@router.post("/refresh", response_model=user_schemas.UserRefreshDTO)
async def refresh(db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):

    await Authorize.jwt_refresh_token_required()

    user_id = await Authorize.get_jwt_subject()
    user = await crud_user.get_user(db, user_id)
    new_access_token = await Authorize.create_access_token(subject=user_id)
    user.access_token = new_access_token
    return user

@router.post('/particalar_refresh', response_model=Optional[user_schemas.UserRefreshDTO])
async def refresh(db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    await Authorize.jwt_refresh_token_required()
    user_id = await Authorize.get_jwt_subject() or None
    if user_id:
        user = await crud_user.get_user(db, user_id)
        new_access_token = await Authorize.create_access_token(subject=user_id)
        user.access_token = new_access_token
        return user
    else:
        pass

#Вместо отзыва токена у пользователя и хранения его в deny листе проще прописать пользователю флаг "locked"