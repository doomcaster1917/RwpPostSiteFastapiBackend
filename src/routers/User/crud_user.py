from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from ... import models
from src.database import SessionLocal
from . import user_schemas


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
       await db.close()
async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str):
    meta = await db.execute(select(models.User).filter(models.User.email == email))
    return meta.scalar_one_or_none()

async def get_user_by_nickname(db: AsyncSession, nickname: str):
    result = await db.execute(select(models.User).filter(models.User.nickname == nickname))
    return result.scalar_one_or_none()

async def save_refresh_token(db: AsyncSession, user: models.User):
    db.add(user)
    await db.commit()
    await db.refresh(user)
async def create_user(db: AsyncSession, user: user_schemas.UserCreateDTO):
    object_user = models.User(**user.model_dump())
    db.add(object_user)
    await db.commit()
    await db.refresh(object_user)


async def change_user_name(db: AsyncSession, user_id: int, new_name: str):
    user = await db.execute(select(models.User).where(models.User.id == user_id))
    person = user.scalar_one_or_none()
    person.nickname = new_name
    print(person.nickname)
    await db.commit()
    await db.refresh(person)
    return person

async def change_user_avatar(db: AsyncSession, user_id: int, image_path: str):
    user = await db.execute(select(models.User).where(models.User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail='Пользователя не существует')
    person = user.scalar_one_or_none()
    person.avatar_path = image_path
    await db.commit()
    await db.refresh(person)
    return person

async def change_user_password(db: AsyncSession, current_user_id: int, schema=user_schemas.UserChangePasswordDTO):
    user = await db.execute(select(models.User).where(models.User.id == current_user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User with this id doesn't exist")
    person = user.scalar_one_or_none()
    person.password = schema.new_password
    await db.commit()
    await db.refresh(person)

async def get_comments_by_user(db: AsyncSession, user_id: int):
    query = text("""SELECT comments.id AS comment_id, comments.text AS comment_text, 
            comments.date_made AS comment_date, comments.owner_id, comments.post_id AS post_id,
            posts.title, posts.img_path as post_img
        FROM comments JOIN users ON comments.owner_id = users.id JOIN posts ON comments.post_id = posts.id
        WHERE users.id =:user_id ORDER BY comment_date;""").bindparams(user_id=int(user_id))
    result = await db.execute(query)
    comms_raw = result.fetchall()
    comments = []
    for comment in comms_raw:
        if comment:
            comments.append({'comment_id': comment[0], 'comment_text': comment[1],
                             'comment_date': comment[2].strftime('%d.%m.%Y'), 'owner_id': comment[3],
                             'post_id': comment[4], 'title': comment[5], 'post_img': comment[6]})
        else:
            pass
    return comments
