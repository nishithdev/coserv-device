from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN
import httpx

AUTH_URL = "https://coserv.smarthub.coop/services/oauth/auth/v2"

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
):
    user_id = entry.data["user_id"]
    password = entry.data["password"]
    async_add_entities([CoServAuthTokenSensor(user_id, password)], update_before_add=True)

class CoServAuthTokenSensor(SensorEntity):
    def __init__(self, user_id: str, password: str):
        self._user_id = user_id
        self._password = password
        self._attr_name = "CoServ Authorization Token"
        self._attr_unique_id = f"coserv_token_sensor_{user_id}"
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}
        self._attr_device_class = None
        self._attr_state_class = None

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, user_id)},
            name="CoServ Account",
            manufacturer="CoServ",
            model="SmartHub",
            entry_type="service"
        )

    async def async_update(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        cookies = {
            "JSESSIONID-consumer_1.0": "aed357ac-00ad-43a9-a623-495cb0c5a850",
            "XSRF-TOKEN": "Xv+SxTFmc1/RVhW7uY125Q==",
        }

        data = {
            "userId": self._user_id,
            "password": self._password
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(AUTH_URL, headers=headers, cookies=cookies, data=data)
                json_data = response.json()

                status = json_data.get("status", "").upper()

                if response.status_code == 200 and status == "SUCCESS" and "authorizationToken" in json_data:
                    token = json_data["authorizationToken"]
                    self._attr_native_value = token
                    self._attr_extra_state_attributes = {
                        "expires_in": json_data.get("expires_in"),
                        "token_type": json_data.get("token_type"),
                        "status": status,
                        "status_code": response.status_code
                    }
                else:
                    self._attr_native_value = "Login failed"
                    self._attr_extra_state_attributes = {
                        "status": status,
                        "authorizationToken": json_data.get("authorizationToken"),
                        "error": json_data.get("error_description", "No authorizationToken in response"),
                        "status_code": response.status_code
                    }

        except httpx.RequestError as e:
            self._attr_native_value = "Connection error"
            self._attr_extra_state_attributes = {
                "error": str(e)
            }

        except Exception as e:
            self._attr_native_value = "Unexpected error"
            self._attr_extra_state_attributes = {
                "error": str(e)
            }