from sqlalchemy import select
from conftest import client, async_session_maker
from redis.asyncio import Redis
from httpx import AsyncClient
from typing import Union
from src import models
from fastapi import File, Response
import os

async def authorizated_request(ac: AsyncClient, ulr: str, request_method: str, redis_server: Redis, json_body: dict=None,
                                with_files: bool=None, picture_binary=None) -> Union[Response, dict]:
    access_token = await redis_server.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    files = {"file": ("file", picture_binary, "image/png")}
    if request_method == "POST":
        response = await ac.post(url=ulr, json=json_body, headers=headers)
        if with_files is True:
            response = await ac.post(url=ulr, data=json_body, headers=headers, files=files)
    elif request_method == "PATCH":
        response = await ac.patch(url=ulr, json=json_body, headers=headers)
        if with_files is True:
            response = await ac.patch(url=ulr, data=json_body, headers=headers, files=files)
    elif request_method == "GET":
        response = await ac.get(url=ulr, headers=headers)
    elif request_method == "DELETE":
        response = await ac.delete(url=ulr, headers=headers)
    else:
        raise "Wrong request method"

    return response

async def test_registration(ac: AsyncClient, test_user_info: dict):
    myCmd = 'redis-cli flushall'
    os.system(myCmd) # Cleanup redis-database via bash-command.
    response = await ac.post("/registration/", json=test_user_info)
    print(response.text)
    assert response.status_code == 200

# Returns nothing is successes case. User takes his tokens on /authentication/login endpoint.
async def test_input_code(redis_server: Redis, ac: AsyncClient):
    codes = [key if str(key).isdigit() else None async for key in redis_server.scan_iter()]
    response = await ac.post("/registration/input_secure_code", json={'secure_code': codes[0]})
    [await redis_server.delete(code) if code is not None else {} for code in codes]
    assert response.status_code == 200

async def test_login(ac: AsyncClient, redis_server: Redis, test_user_info: dict):
    response = await ac.post("/authentication/login", json={"email": test_user_info['email'], "password": test_user_info['password']})
    access_token = response.json()["access_token"]
    refresh_token = response.json()["refresh_token"]
    await redis_server.set("access_token", access_token)
    await redis_server.set("refresh_token", refresh_token)
    assert access_token, refresh_token

async def test_authentication_refresh(ac: AsyncClient, redis_server):
    refresh_token = await redis_server.get("refresh_token")
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = await ac.post("/authentication/refresh", headers=headers)
    new_access_token = response.json()['access_token']
    if new_access_token:
        await redis_server.set("access_token", new_access_token)
    assert new_access_token is not None
    assert response.status_code == 200

async def test_authentication_particular_refresh(ac: AsyncClient, redis_server):
    refresh_token = await redis_server.get("refresh_token")
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = await ac.post("/authentication/particalar_refresh", headers=headers)
    new_access_token = response.json()['access_token']
    if new_access_token:
        await redis_server.set("access_token", new_access_token)

    unathorized_response = await ac.post("/authentication/particalar_refresh")
    unathorized_token = unathorized_response.json()

    assert "access_token" not in unathorized_token.keys()
    assert new_access_token is not None
    assert response.status_code == 200

async def test_make_admin():
    async with async_session_maker() as session:
        user = await session.execute(select(models.User).where(models.User.id == 1))
        person = user.scalar_one_or_none()
        person.is_admin = True
        await session.commit()
        assert person.is_admin is True


async def test_posts_create(ac: AsyncClient, picture_binary: Union[bytes, File], redis_server: Redis):
    request_body = {"title":"test title", "full_text":"test full_text"}
    response = await authorizated_request(ac, "/posts/create_post", "POST", redis_server, request_body, True,
                                             picture_binary)
    assert response.status_code == 200

async def test_posts_update(ac: AsyncClient, picture_binary: Union[bytes, File], redis_server: Redis):
    request_body = {"title": "update test title", "text": "update test full_text"}
    response = await authorizated_request(ac, "posts/update_post/1", "PATCH", redis_server, request_body, True,
                                             picture_binary)
    assert response.status_code == 200

async def test_posts_get_all(ac: AsyncClient):
    response = await ac.get("/posts/")
    assert response.status_code == 200


async def test_posts_get_single(ac: AsyncClient):
    response = await ac.get("/posts/1")
    assert response.status_code == 200

# test_delete_post is lie below cause existing post need to be used as parent for future test-comments

async def test_comments_create(ac: AsyncClient, redis_server: Redis):
    request_body = {"text": "test comment", "owner_id": 1, "post_id": 1}
    response = await authorizated_request(ac, "/comments/create_comment", "POST",  redis_server, request_body)
    assert response.status_code == 200

async def test_comments_update(ac: AsyncClient, redis_server:Redis):
    request_body = {"new_comment_text": "test comment", "comment_id": 1}
    response = await authorizated_request(ac, "/comments/edit_comment", "PATCH", redis_server, request_body)
    assert response.status_code == 200

async def test_comments_get_all(ac: AsyncClient, redis_server:Redis):
    response = await authorizated_request(ac, "/comments/get_all_comments", "GET", redis_server)
    assert response.status_code == 200

# After creating comment we need to test complex posts method which returns post data with nested comments
async def test_posts_single_with_comments(ac: AsyncClient):
    response = await ac.get("/posts/1")
    assert response.status_code == 200
    assert len(response.json()['comments']) > 0
    assert len(response.json()['comments'][0]['comment_text']) > 0
    assert isinstance(response.json()['comments'][0]['comment_text'], str)


async def test_comments_delete(ac: AsyncClient, redis_server:Redis):
    response = await authorizated_request(ac, "/comments/delete_comment/1", "DELETE", redis_server)
    assert response.status_code == 200

async def test_websocket():
    pass
    # Made fully manual testing/postman-testing. Pytest disconnects websocket when meet infinite loop in websocket function.
    # Probably external process is required for this test
    # In next API versions will be testing via Gitlab-services

async def test_users_change_nickname(ac: AsyncClient, redis_server: Redis):
    new_name = "new_test_name"
    json_body = {"new_name": new_name}
    response = await authorizated_request(ac, "/users/change_name", "PATCH", redis_server, json_body)
    async with async_session_maker() as session:
        user = await session.execute(select(models.User).where(models.User.id == 1))
        person = user.scalar_one_or_none()
        changed_name = person.nickname

    assert changed_name == new_name
    assert response.status_code == 200

async def test_users_change_password(ac: AsyncClient, redis_server:Redis, test_user_info: dict):
    new_password = "<PASSWORD>"
    json_body = {"old_password": test_user_info['password'],"new_password": new_password}
    response = await authorizated_request(ac, "/users/change_password", "PATCH", redis_server, json_body)
    assert response.status_code == 200

async def test_users_change_avatar(ac: AsyncClient, redis_server: Redis, picture_binary: bytes):
    request_body = {"user_id": 1}
    response = await authorizated_request(ac, "users/change_avatar", "PATCH", redis_server, request_body, True,
                                          picture_binary)
    assert response.status_code == 200

async def test_users_get_user_comments(ac: AsyncClient, redis_server:Redis):
    response = await authorizated_request(ac, "/users/get_comments/1", "GET", redis_server)
    assert response.status_code == 200

async def test_users_get_user(ac: AsyncClient, redis_server: Redis):
    response = await authorizated_request(ac, "/users/", "GET", redis_server)
    assert len(response.json()) > 0
    assert response.status_code == 200

async def test_comments_delete(ac: AsyncClient, redis_server: Redis):
    response = await authorizated_request(ac, "/comments/delete_comment/1", "DELETE", redis_server)
    async with async_session_maker() as session:
        data = await session.execute(select(models.Comment))
        comments = data.scalars().all()

    assert not comments
    assert response.status_code == 200

async def test_posts_delete(ac: AsyncClient, redis_server: Redis):
    response = await authorizated_request(ac, "/posts/delete_post/1", "DELETE", redis_server)
    async with async_session_maker() as session:
        data = await session.execute(select(models.Post))
        posts = data.scalars().all()

    assert not posts
    assert response.status_code == 200

async def test_admin_check_is_admin(ac: AsyncClient, redis_server: Redis):
    response = await authorizated_request(ac, "/rwp_panel/check_is_admin", "POST", redis_server)
    async with async_session_maker() as session:
        user = await session.execute(select(models.User).where(models.User.id == 1))
        person = user.scalar_one_or_none()

    assert person.is_admin is True
    assert response.status_code == 200

async def test_admin_block_user(ac: AsyncClient, redis_server: Redis):
    response = await authorizated_request(ac, "/rwp_panel/block_user/1", "PATCH", redis_server)
    async with async_session_maker() as session:
        user = await session.execute(select(models.User).where(models.User.id == 1))
        person = user.scalar_one_or_none()

    assert person.is_locked is True
    assert response.status_code == 200

async def test_admin_unblock_user(ac: AsyncClient, redis_server: Redis):
    response = await authorizated_request(ac, "/rwp_panel/unblock_user/1", "PATCH", redis_server)
    async with async_session_maker() as session:
        user = await session.execute(select(models.User).where(models.User.id == 1))
        person = user.scalar_one_or_none()

    assert person.is_locked is False
    assert response.status_code == 200
