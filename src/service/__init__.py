from core.config import IS_FAKE_API
from service.api_client_fake import FakeAPIService
from service.api_client_real import RealAPIService

if IS_FAKE_API:
    ConcreateAPIService = FakeAPIService
else:
    ConcreateAPIService = RealAPIService
