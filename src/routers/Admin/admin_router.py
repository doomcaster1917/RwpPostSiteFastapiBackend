from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter
from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud_admin
from ..Middleware.Middleware import Middleware
from ..User import user_schemas

from src.database import get_db

router = APIRouter(
    prefix="/rwp_panel",
    tags=["/rwp_panel"],
    responses={404: {"description": "Not found"}},
)


@router.get("/get_all_users", response_model=list[user_schemas.UserDTO]) #для админки
async def get_all_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    await Middleware.admin_checker(Authorize, db)
    return await crud_admin.get_all_users(db, skip=skip, limit=limit)


@router.post('/check_is_admin')
async def check_is_admin(db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    return await Middleware.admin_checker(Authorize, db)


@router.patch("/block_user/{user_id}")
async def block_user(user_id: str = Path(title="The ID of the item to get"), db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    await Middleware.admin_checker(Authorize, db)
    return await crud_admin.block_user(user_id=int(user_id), db=db)

@router.patch("/unblock_user/{user_id}")
async def unblock_user(user_id: str = Path(title="The ID of the item to get"), db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    await Middleware.admin_checker(Authorize, db)
    return await crud_admin.unblock_user(user_id=int(user_id), db=db)

