from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Path
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import SessionLocal

from . import comments_schemas
from . import crud_comments
from ..Middleware.Middleware import Middleware

from src.database import get_db

router = APIRouter(
    prefix="/comments",
    tags=["comments"],
    responses={404: {"description": "Not found"}},
)


@router.post("/create_comment")
async def create_comment(comment: comments_schemas.CommentCreateDTO, db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()):
    if await Middleware.user_id_checker(authorize, db, comment.owner_id):
        return await crud_comments.create_comment(db=db, comment=comment)


@router.patch('/edit_comment')
async def edit_comment(comment: comments_schemas.CommentEditDTO, db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()):
    comment_db = await crud_comments.get_comment(db, comment.comment_id)
    if await Middleware.user_id_checker(authorize, db, comment_db.owner_id):
        return await crud_comments.edit_comment(db=db, new_comment_text=comment.new_comment_text,
                                                comment_id=comment.comment_id)

# Post's comments are returned in single post get-request with the other post data, so method below is needed only in admin-panel
@router.get("/get_all_comments", response_model=list[comments_schemas.CommentJoinedDTO]) #для админки
async def get_all_comments(db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    await Middleware.admin_checker(Authorize, db)
    return await crud_comments.get_all_comments(db)

@router.delete('/delete_comment/{comment_id}')
async def delete_comment(comment_id: str = Path(title="The ID of the item to get"),
                         db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()):
    comment_db = await crud_comments.get_comment(db, int(comment_id))
    if await Middleware.user_id_checker(authorize, db, comment_db.owner_id):
        return await crud_comments.delete_comment(db=db, comment_id=int(comment_id))


