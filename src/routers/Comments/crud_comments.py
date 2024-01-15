from sqlalchemy import select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from ... import models

from . import comments_schemas


async def edit_comment(db: AsyncSession, new_comment_text: str, comment_id: int):
    result = await db.execute(select(models.Comment).where(models.Comment.id == comment_id))
    data = result.scalar_one_or_none()
    data.text = new_comment_text
    await db.commit()
    await db.refresh(data)

async def get_comment(db: AsyncSession, comment_id: int):
    result = await db.execute(select(models.Comment).where(models.Comment.id == comment_id))
    return result.scalar_one_or_none()

async def get_all_comments(db: AsyncSession):
    query = text("""SELECT comments.id AS comment_id, comments.text AS comment_text, 
                comments.date_made AS comment_date, comments.owner_id, comments.post_id AS post_id,
                posts.title, posts.img_path as post_img, users.avatar_path AS owner_avatar, users.nickname AS owner_nickname
            FROM comments JOIN users ON comments.owner_id = users.id JOIN posts ON comments.post_id = posts.id
            ORDER BY comment_date DESC;""")
    result = await db.execute(query)
    comms_raw = result.fetchall()
    comments = []
    for comment in comms_raw:
        if comment:
            comments.append({'comment_id': comment[0], 'comment_text': comment[1],
                             'comment_date': comment[2].strftime('%d.%m.%Y'), 'owner_id': comment[3],
                             'post_id': comment[4], 'post_title': comment[5], 'post_img': comment[6],
                             'owner_avatar': comment[7], 'owner_nickname': comment[8]})
        else:
            pass
    return comments

async def create_comment(db: AsyncSession, comment: comments_schemas.CommentCreateDTO):
    db_comment = models.Comment(**comment.model_dump())#, text=comment.text, author_id=comment.user_id, post_id=comment.post_id)
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment

async def delete_comment(comment_id: int, db: AsyncSession):
    await db.execute(delete(models.Comment).where(models.Comment.id == comment_id))
    await db.commit()
    return True