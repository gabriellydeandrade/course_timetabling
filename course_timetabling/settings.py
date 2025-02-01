from decouple import config
from enum import Enum

SAMPLE_SPREADSHEET_ID = config("SAMPLE_SPREADSHEET_ID", default="1MZ_LFco9SZ5FrZFt7CAUCJu4xHov9VtTuil0CyRx9jI")

class LicenseType(Enum):
    NAMED_USER_ACADEMIC = "Named-User Academic"
    WSL_ACADEMIC = "WSL Academic"

APP_LICENSE_TYPE = config("LICENSE_TYPE", default=LicenseType.NAMED_USER_ACADEMIC.value, cast=lambda v: v if v in LicenseType._value2member_map_ else LicenseType.NAMED_USER_ACADEMIC.value)
APP_LICENSE_ID = config("LICENSE_ID", default=123, cast=int)
APP_WLS_ACCESS_ID = config("WLS_ACCESS_ID", default="access_id")
APP_WS_SECRET = config("WS_SECRET", default="secret")

APP_CACHE_TTL = config("CACHE_TTL", default=829812309, cast=int)

APP_SHEETS_SCOPES = config("SHEETS_SCOPES", default=["https://www.googleapis.com/auth/spreadsheets.readonly"], cast=list)

# Model parameters

DUMMY_PROFESSOR_NAME = config("DUMMY_PROFESSOR", default="DUMMY")
DUMMY_COEFFICIENT = config("DUMMY_COEFFICIENT", default=0.00001, cast=float)
DEFAULT_COEFFICIENT = config("DEFAULT_COEFFICIENT", default=100, cast=int)
SERVICE_COURSE_COEFFICIENT_SP = config("SERVICE_COURSE_COEFFICIENT_SP", default=10, cast=int)
SERVICE_COURSE_COEFFICIENT_PP = config("SERVICE_COURSE_COEFFICIENT_PP", default=1, cast=int)
ZERO_COEFFICIENT = config("ZERO_COEFFICIENT", default=0, cast=int)

WEIGHT_FACTOR_PP = config("WEIGHT_FACTOR_PP", default=100, cast=int)
MIN_CREDITS_PERMANENT = config("MIN_CREDITS_PERMANENT", default=8, cast=int)
MAX_CREDITS_PERMANENT = config("MAX_CREDITS_PERMANENT", default=12, cast=int)

WEIGHT_FACTOR_PS = config("WEIGHT_FACTOR_PS", default=1000, cast=int)
MIN_CREDITS_SUBSTITUTE = config("MIN_CREDITS_SUBSTITUTE", default=8, cast=int)
MAX_CREDITS_SUBSTITUTE = config("MAX_CREDITS_SUBSTITUTE", default=12, cast=int)

SVC_MATH_COURSES = config("SVC_MATH_COURSES", default=["ICP231", "MAW123", "ICP478"], cast=list)
SVC_BASIC_COURSES = config("SVC_BASIC_COURSES", default=["ICP114", "ICP121", "MAW112"], cast=list)