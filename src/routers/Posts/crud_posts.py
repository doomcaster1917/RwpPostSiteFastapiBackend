from sqlalchemy import select, text, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src import models


async def get_posts(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Post).offset(skip).limit(limit).order_by(models.Post.date_made.desc()))
    return result.scalars().all()

async def get_post(db: AsyncSession, post_id: int):
    try:
        query_post = text("""SELECT posts.id, posts.title, posts.text, posts.date_made, posts.img_path
                        FROM posts
                        WHERE posts.id =:post_id""").bindparams(post_id=post_id)
        query_comments = text("""WITH fullo as (SELECT text, owner_id, nickname, avatar_path, date_made, comments.id as comment_id, users.is_locked AS is_owner_locked from comments 
                        FULL OUTER JOIN users ON comments.owner_id = users.id WHERE comments.post_id =:post_id)
                        Select text, owner_id, nickname, avatar_path, date_made, comment_id, is_owner_locked from fullo
                        ORDER BY date_made;""").bindparams(post_id=post_id)
        result_post = await db.execute(query_post)
        result_comments = await db.execute(query_comments)

        comments = []
        comms_raw = result_comments.fetchall()

        for comment in comms_raw:
            if comment:
                comments.append({'comment_text':comment[0], 'owner_id':comment[1],
                                   'nickname': comment[2], 'avatar_path': comment[3],
                                 'date_made': comment[4].strftime(' %H:%M:%S / %m.%d.%Y'), 'comment_id': comment[5],
                                 'is_owner_locked': comment[6]})
            else:
                pass

        post = result_post.fetchone()
        if post:
            post_data = {'id': post[0], 'title': post[1], 'text': post[2], 'date_made':post[3].strftime('%m.%d.%Y'),
                         'img_path': post[4],
                         'comments': comments}
        else:
            post_data = {}

        return post_data

    except Exception as err:
            raise(err)


async def create_post(title, fulltext, image_path, db: AsyncSession):
    object_post = models.Post(title=title, text=fulltext, img_path=image_path)
    db.add(object_post)
    await db.commit()
    await db.refresh(object_post)
    result = await db.scalars(select(models.Post).options(selectinload(models.Post.comments)))
    item = result.first()
    return item

async def update_post(post_id: int, text: str, title:str, image_path:str, db: AsyncSession):
     post_raw = await db.execute(select(models.Post).where(models.Post.id == post_id))
     post = post_raw.scalar_one_or_none()
     post.title = title
     post.text = text
     post.img_path = image_path
     await db.commit()
     await db.refresh(post)
     return True

async def delete_post(post_id: int, db: AsyncSession):
    await db.execute(delete(models.Post).where(models.Post.id == post_id))
    await db.commit()
    return True