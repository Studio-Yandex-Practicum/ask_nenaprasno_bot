from core.config import FAKE_API
from service.api_client_fake import FakeAPIService
from service.api_client_real import RealAPIService

if FAKE_API:
    ConreateAPIService = FakeAPIService
else:
    ConreateAPIService = RealAPIService
