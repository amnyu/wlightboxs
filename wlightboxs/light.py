import logging
from time import sleep

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant.components.light import (
    ATTR_BRIGHTNESS, Light, PLATFORM_SCHEMA, SUPPORT_BRIGHTNESS)
from homeassistant.const import CONF_HOST, CONF_NAME

_LOGGER = logging.getLogger(__name__)

DEFAULT_HOST = '127.0.0.1'
DEFAULT_NAME = 'wLightBoxS'

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST, default=DEFAULT_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    host = config.get(CONF_HOST)
    device_name = config.get(CONF_NAME)

    device = 'http://{}/'.format(host)
    device_state = requests.get(device + "api/device/state")
    status_code = device_state.status_code

    if status_code != 200:
        _LOGGER.error("Could not connect to wLightBoxS")
        return False
    elif device_state.json()['device']['type'] != 'wLightBoxS':
        _LOGGER.error("Not a wLightBoxS device")

    add_entities([wLightBoxS(device, device_name)])


class wLightBoxS(Light):

    def __init__(self, light, name=None):
        self._light = light
        self._name = name
        self._state = None
        self._brightness = None
        self._supported_features = SUPPORT_BRIGHTNESS

    @property
    def name(self):
        return self._name

    @property
    def brightness(self):
        return self._brightness

    @property
    def is_on(self):
        return self._state

    @property
    def supported_features(self):
        return self._supported_features

    def turn_on(self, **kwargs):
        brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        brigthness_hex = '{0:02x}'.format(brightness)
        requests.get(self._light + "s/" + brigthness_hex)

    def turn_off(self, **kwargs):
        requests.get(self._light + "s/00")

    def update(self):
        light_state = requests.get(self._light + "api/light/state")

        brightness_raw = light_state.json()['light']['desiredColor']
        brightness = int(brightness_raw, 16)

        self._state = brightness > 0
        self._brightness = brightness
