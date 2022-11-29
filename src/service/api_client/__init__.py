from core.config import settings
from service.api_client.mock_api_service import MockAPIService
from service.api_client.site_api_service import SiteAPIService

APIService = MockAPIService if settings.is_fake_api else SiteAPIService
