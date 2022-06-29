from core.config import IS_FAKE_API
from service.api_client.mock_api_service import MockAPIService
from service.api_client.site_api_service import SiteAPIService

if IS_FAKE_API:
    APIService = MockAPIService
else:
    APIService = SiteAPIService
