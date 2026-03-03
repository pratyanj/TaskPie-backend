from decouple import config

# Database credentials
DB_NAME = config("DB_NAME", default="taskpy")
DB_USER = config("DB_USER", default="postgresql")
DB_PASSWORD = config("DB_PASSWORD")
DB_HOST = config("DB_HOST", default="localhost")
DB_PORT = config("DB_PORT", default="5432")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")

ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int)
REFRESH_TOKEN_EXPIRE_DAYS = config("REFRESH_TOKEN_EXPIRE_DAYS", cast=int)

GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET")

GOOGLE_REDIRECT_URI = config("GOOGLE_REDIRECT_URI")
GOOGLE_TOKEN_URL = config("GOOGLE_TOKEN_URL")
GOOGLE_USERINFO_URL = config("GOOGLE_USERINFO_URL")
