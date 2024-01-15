import asyncio
from typing import Annotated

from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, UploadFile, File, Form, WebSocket, Path
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ... import sunimagesaver
from src.database import SessionLocal

from . import crud_user
from . import user_schemas
from ..Comments import comments_schemas
from ..Middleware.Middleware import Middleware

from src.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=user_schemas.UserDTO)
async def read_user(authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    user_id = await Middleware.get_user_id_from_token(authorize)
    user = await crud_user.get_user(db, user_id)
    return user


@router.patch('/change_avatar')
async def change_avatar(user_id: Annotated[str, Form()], file: Annotated[UploadFile, File()],
                        db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()):
    allowed_types = ['image/jpeg', 'image/png', 'image/JPG']
    if file.content_type in allowed_types and await Middleware.user_id_checker(authorize, db, user_id):
        content = await file.read()
        sun_userapi_url = await sunimagesaver.get_sun_userapi_url(content)
    else:
        raise HTTPException(status_code=422, detail="Not right format of picture")

    user = await crud_user.change_user_avatar(db=db, user_id=int(user_id), image_path=sun_userapi_url)
    return user.avatar_path


@router.websocket("/check_name/{user_id}/ws")
async def check_existing_name(websocket: WebSocket, user_id: str = Path(title="The ID of the item to get"), db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    while True:

        loop = asyncio.get_event_loop()
        timer = loop.call_later(120, lambda: asyncio.ensure_future(websocket.close()))
        data = await websocket.receive_text()
        user = await crud_user.get_user_by_nickname(db, data)
        if data:
            timer.cancel()
        if user:
            await websocket.send_text(f"Имя {user.nickname} уже занято")
        elif data == 'Name changed':
            await websocket.close()
        else:
            await websocket.send_text('')


@router.patch('/change_name')
async def change_user_name(new_name: user_schemas.UserChangeNameDTO, authorize: AuthJWT = Depends(),
                           db: AsyncSession = Depends(get_db)):
    user_id = await Middleware.get_user_id_from_token(authorize)
    user = await crud_user.change_user_name(db, user_id, new_name.new_name)
    return user.nickname

@router.patch('/change_password')
async def change_user_password(schema: user_schemas.UserChangePasswordDTO,
                               authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    user_id = await Middleware.get_user_id_from_token(authorize)
    if await Middleware.check_user_password(db, schema.old_password, user_id):
        return await crud_user.change_user_password(db, int(user_id), schema)

@router.get('/get_comments/{user_id}', response_model=list[comments_schemas.UserCommentsDTO])
async def get_comments_of_user(user_id = Path(title='id of user'), db: AsyncSession = Depends(get_db),
                               authorize: AuthJWT = Depends()):
    if await Middleware.user_id_checker(authorize, db, int(user_id)):
        return await crud_user.get_comments_by_user(db, user_id)
