from starlette.config import Config
from starlette.datastructures import Secret

env_file_path = r'F:\q3-projects\fastapi_endpoints\fastapi_endpoints_neondb\fastapi_endpoints_neondb\.env'

try:
    config = Config(env_file=env_file_path)
except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret)
TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)