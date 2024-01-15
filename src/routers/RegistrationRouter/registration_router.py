import uuid
from fastapi import APIRouter, FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..User import crud_user

from ..User import user_schemas
from src.routers.aioSMTP import send_mail_async
from src.routers.redis_server import redis_server

from src.config import SMTP_USER

from src.database import get_db

app = FastAPI()
router = APIRouter(
    prefix="/registration",
    tags=["registration"],
    responses={404: {"description": "Not found"}},
)



@router.post('/')
async def create_account(data: user_schemas.UserCreateDTO, db: AsyncSession = Depends(get_db)):
    redis = await redis_server()


    existing_nickname = await crud_user.get_user_by_nickname(db=db, nickname=data.nickname)
    existing_email = await crud_user.get_user_by_email(db=db, email=data.email)

    if (existing_email and existing_email.email == data.email) or (existing_nickname and existing_nickname.nickname == data.nickname):
        raise HTTPException(status_code=406, detail="This nickname or email already exists")


    secure_code = str(uuid.uuid1().int)[:8]
    message = data.model_dump()

    await redis.hset(secure_code, mapping=message)
    await redis.expire(secure_code, 900)

    await send_mail_async(SMTP_USER, data.email, "verification_mail",
                          secure_code=secure_code)

    return "Successful registration"

# Returns nothing is successes case. User takes his tokens on /authentication/login endpoint.
@router.post('/input_secure_code')
async def check_code(taken_code: user_schemas.GetSecureCodeDTO, db: AsyncSession = Depends(get_db)):
    redis = await redis_server()
    codes = [key if str(key).isdigit() else None async for key in redis.scan_iter()]
    if codes:
        if str(taken_code.secure_code) in codes:
            user_cache = await redis.hgetall(str(taken_code.secure_code))
            model = user_schemas.UserCreateDTO(email = user_cache['email'], password = user_cache['password'], nickname = user_cache['nickname'])
            await crud_user.create_user(db, model)
            await redis.delete(str(taken_code.secure_code))

        else:
            raise HTTPException(status_code=406, detail="The input code doesnt match the secure code")
    else:
        raise HTTPException(status_code=404, detail="The input code time expired")



