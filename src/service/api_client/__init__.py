from core.config import FAKE_API
from service.api_client.hemas import ShemasAPIService
from service.api_client.mock_shemas import MockShemasAPIService

if FAKE_API:
    ConreateAPIService = MockShemasAPIService
else:
    ConreateAPIService = ShemasAPIService
