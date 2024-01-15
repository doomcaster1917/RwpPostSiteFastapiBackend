from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src import models


async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()

async def block_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    person = result.scalar_one_or_none()
    if person == None:
        raise HTTPException(status_code=404, detail='Пользователя не существует')
    person.is_locked = True
    await db.commit()  # сохраняем изменения
    await db.refresh(person)
    return "Successful"

async def unblock_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    person = result.scalar_one_or_none()
    if person == None:
        raise HTTPException(status_code=404, detail='Пользователя не существует')
    person.is_locked = False
    await db.commit()
    await db.refresh(person)
    return "Successful"

async def check_is_admin(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    person = result.scalar_one_or_none()
    if person == None:
        raise HTTPException(status_code=404, detail='Пользователя не существует')
    return person.is_admin

