from fastapi import HTTPException
from ..Admin import crud_admin
from ..User import crud_user


class Middleware:
    @staticmethod
    async def admin_checker(authorize, db):
        await authorize.jwt_required()
        current_user_id = await authorize.get_jwt_subject()
        if not await crud_admin.check_is_admin(db, current_user_id):
            raise HTTPException(status_code=403, detail="Not enought rights")
        else:
            return True

    # we match here user_id and current_user_id from jwt_auth instead just use current_id from jwt in functions
    # because functions in some routers we must have user_id argument to allow admin operate on other users objects
    @staticmethod
    async def user_id_checker(authorize, db, user_id):
        await authorize.jwt_required()
        current_user_id = await authorize.get_jwt_subject()
        compared_ids = current_user_id == int(user_id)
        if not compared_ids:
            raise HTTPException(status_code=403, detail="Wrong user_id")
        else:
            return True

    @staticmethod
    async def check_user_password(db, password, current_user_id):
        user = await crud_user.get_user(db, current_user_id)
        if (user and password != user.password) or not user:
            raise HTTPException(status_code=406, detail="Bad username or password")
        else:
            return user

    @staticmethod
    async def get_user_id_from_token(authorize):
        await authorize.jwt_required()
        return await authorize.get_jwt_subject()
