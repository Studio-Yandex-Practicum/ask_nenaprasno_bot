from core.config import IS_FAKE_API
from service.api_client.hemas import ShemasAPIService
from service.api_client.mock_shemas import MockShemasAPIService

if IS_FAKE_API:
    ConreateAPIService = MockShemasAPIService
else:
    ConreateAPIService = ShemasAPIService
