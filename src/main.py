__NAME__ = 'app'

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from .config import JWTSettings
from .routers.Admin import admin_router
from .routers.AuthRouter import auth_router
from .routers.Comments import comments_router
from .routers.Posts import posts_router
from .routers.RegistrationRouter import registration_router
from .routers.User import users_router

# async def init_models():
#     async with engine.begin() as conn:
#         await conn.run_sync(models.Base.metadata.drop_all)
#         await conn.run_sync(models.Base.metadata.create_all)
#
# event_loop = asyncio.get_event_loop()
# asyncio.ensure_future(init_models(), loop=event_loop)

# async def fill_models():
#     # await TestingSQL.insertPosts()
#     # await TestingSQL.insertUsers()
#     # await TestingSQL.insertComments()
#
#
#
#
# event_loop = asyncio.get_event_loop()
# asyncio.ensure_future(fill_models(), loop=event_loop)

app = FastAPI()
app.include_router(users_router.router)
app.include_router(registration_router.router)
app.include_router(auth_router.router)
app.include_router(posts_router.router)
app.include_router(comments_router.router)
app.include_router(admin_router.router)



origins = [
    "http://localhost:3000",
    "http://localhost:3000/users",
    "http://localhost",
    "http://localhost:8080",
    "ws://localhost:3000",
    "WebSocket /ws"
]

app.add_middleware(
CORSMiddleware,
allow_origins= origins,
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)


@AuthJWT.load_config
def get_config():
    return JWTSettings()

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

