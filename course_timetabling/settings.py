from decouple import config

SAMPLE_SPREADSHEET_ID = config("SAMPLE_SPREADSHEET_ID", default="1MZ_LFco9SZ5FrZFt7CAUCJu4xHov9VtTuil0CyRx9jI")

APP_LICENSE_ID = config("LICENSE_ID", default=123, cast=int)
APP_WLS_ACCESS_ID = config("WLS_ACCESS_ID", default="access_id")
APP_WS_SECRET = config("WS_SECRET", default="secret")

APP_CACHE_TTL = config("CACHE_TTL", default=0, cast=int)

# Model parameters

DUMMY_PROFESSOR_NAME = config("DUMMY_PROFESSOR", default="DUMMY")
DUMMY_COEFFICIENT = config("DUMMY_COEFFICIENT", default=0.00001, cast=float)
DEFAULT_COEFFICIENT = config("DEFAULT_COEFFICIENT", default=100, cast=int)
SERVICE_COURSE_COEFFICIENT_SP = config("SERVICE_COURSE_COEFFICIENT_SP", default=10, cast=int)
SERVICE_COURSE_COEFFICIENT_PP = config("SERVICE_COURSE_COEFFICIENT_PP", default=1, cast=int)
ZERO_COEFFICIENT = config("ZERO_COEFFICIENT", default=0, cast=int)
WEIGHT_FACTOR_PP = config("WEIGHT_FACTOR_PP", default=1000, cast=int)
MIN_CREDITS_PERMANENT = config("MIN_CREDITS_PERMANENT", default=8, cast=int)
MAX_CREDITS_SUBSTITUTE = config("MAX_CREDITS_SUBSTITUTE", default=12, cast=int)