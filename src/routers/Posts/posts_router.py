from typing import Annotated, Optional
from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter
from fastapi import Depends, HTTPException, UploadFile, File, Form, Path
from sqlalchemy.ext.asyncio import AsyncSession
from ... import sunimagesaver
from src.database import SessionLocal

from . import crud_posts
from . import posts_schemas
from ..Middleware.Middleware import Middleware

from src.database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
    responses={404: {"description": "Not found"}},
)



@router.get("/", response_model= list[posts_schemas.PostBaseDTO])
async def get_posts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud_posts.get_posts(db, skip=skip, limit=limit)

@router.get("/{post_id}", response_model= Optional[posts_schemas.PostDTO])
async def read_post(post_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_posts.get_post(db, post_id=post_id)

@router.post("/create_post")
async def create_post(title: Annotated[str, Form()], full_text: Annotated[str, Form()], file: Annotated[UploadFile, File()],
                      db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()):
    await Middleware.admin_checker(authorize, db)
    allowed_types = ['image/jpeg', 'image/png', 'image/JPG']
    if file.content_type in allowed_types:
        content = await file.read()
        sun_userapi_url = await sunimagesaver.get_sun_userapi_url(content)
    else:
        raise HTTPException(status_code=422, detail="Not right format of picture")

    await crud_posts.create_post(title, full_text, sun_userapi_url, db=db)
    return 'successfully'

@router.patch('/update_post/{post_id}')
async def update_post(text: Annotated[str, Form()],
                      title: Annotated[str, Form()], file: Annotated[UploadFile|str, File()],
                      post_id: str = Path(title="The ID of the item to get"),
                      db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()):
    await Middleware.admin_checker(authorize, db)

    #frontend can pass str url if image of post isn't changed or starlette.Uploadfile type if image is changed
    if isinstance(file, str):
        image_path = file

    else:
        content = await file.read() if file.content_type in ['image/jpeg', 'image/png', 'image/JPG'] \
            else HTTPException(status_code=422, detail="Not right format of picture")

        sun_userapi_url = await sunimagesaver.get_sun_userapi_url(content)
        image_path = sun_userapi_url

    post = await crud_posts.update_post(db=db, post_id=int(post_id),
                                        text=str(text), title=str(title), image_path=image_path)
    return post if post else HTTPException(status_code=500, detail="Ops. Something went wrong.")

@router.delete('/delete_post/{post_id}')
async def delete_post(post_id: str = Path(title="The ID of the item to get"), db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()):
    await Middleware.admin_checker(authorize, db)
    return await crud_posts.delete_post(post_id = int(post_id), db=db)


