from dotenv import dotenv_values

from service.api_client import (
    FakeAPIService, RealAPIService
)

env = dotenv_values()

FAKE_API = env.get("FAKE_API")

if FAKE_API:
    ConreateAPIService = FakeAPIService
else:
    ConreateAPIService = RealAPIService
