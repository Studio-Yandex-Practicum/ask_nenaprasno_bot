from dataclasses import dataclass


@dataclass
class HealthCheckResponseModel:
    bot_is_avaliable: bool = False
    site_api_is_avaliable: bool = False
