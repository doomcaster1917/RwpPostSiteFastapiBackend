import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

DB_HOST_TEST = os.environ.get("DB_HOST_TEST")
DB_PORT_TEST = os.environ.get("DB_PORT_TEST")
DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
DB_USER_TEST = os.environ.get("DB_USER_TEST")
DB_PASS_TEST = os.environ.get("DB_PASS_TEST")

SECRET_AUTH = os.environ.get("SECRET_AUTH")
VK_TOKEN = os.environ.get("VK_TOKEN")

SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

class JWTSettings(BaseModel):
    authjwt_token_location: set = {'headers'}
    authjwt_secret_key: str = os.environ.get("SECRET_AUTH")
    authjwt_cookie_csrf_protect: bool = False
    # authjwt_cookie_samesite: str = 'none'
    authjwt_cookie_secure: bool = False
    #jwt_refresh token expires 30 days by default
    # Configure application to store and get JWT from cookies
    # Disable CSRF Protection for this example. default is True