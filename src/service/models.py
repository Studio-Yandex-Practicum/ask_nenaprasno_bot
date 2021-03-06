from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class HealthCheckResponseModel:
    bot_is_avaliable: bool = False
    site_api_is_avaliable: bool = False
