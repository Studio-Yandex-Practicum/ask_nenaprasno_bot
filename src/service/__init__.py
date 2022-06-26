from src.core.config import FAKE_API
from src.service.api_client_fake import FakeAPIService
from src.service.api_client_real import RealAPIService

if FAKE_API:
    ConreateAPIService = FakeAPIService
else:
    ConreateAPIService = RealAPIService
