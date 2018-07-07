import os

SERVER_URL_PREFIX = os.getenv("SERVER_URL_PREFIX", "[Put your IP/domain name Here]")

MAX_URL_LEN = int(os.getenv("MAX_URL_LEN", "2000"))
DB_EXPIRE_TIME = int(os.getenv("DB_EXPIRE_TIME", "31536000"))
