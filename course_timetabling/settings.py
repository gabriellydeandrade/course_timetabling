from decouple import config

APP_LICENSE_ID = config("LICENSE_ID", default=123, cast=int)
APP_WLS_ACCESS_ID = config("WLS_ACCESS_ID", default="access_id")
APP_WS_SECRET = config("WS_SECRET", default="secret")
