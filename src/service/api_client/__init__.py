from core.config import IS_FAKE_API
from service.api_client.mock_shemas import MockShemasAPIService
from service.api_client.shemas import ShemasAPIService

if IS_FAKE_API:
    ConreateAPIService = MockShemasAPIService
else:
    ConreateAPIService = ShemasAPIService
