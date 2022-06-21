from core.config import DEBUG

from service.api_client import (
    FakeAPIService, RealAPIService
)

if DEBUG:
    ConreateAPIService = FakeAPIService
else:
    ConreateAPIService = RealAPIService
