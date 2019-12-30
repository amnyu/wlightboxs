import logging
import voluptuous as vol

import requests
from time import sleep
# Import the device class from the component that you want to support
from homeassistant.components.light import (
    ATTR_BRIGHTNESS, Light, PLATFORM_SCHEMA, SUPPORT_BRIGHTNESS)
from homeassistant.const import CONF_HOST
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the wLightBoxS platform."""

    # Assign configuration variables. The configuration check takes care they are
    # present. 
    host = config.get(CONF_HOST)

    # Setup connection with device
    device = 'http://{}/'.format(host)
    # Verify that passed in configuration works
    status_code = requests.get(device).status_code
    if status_code != 200:
        _LOGGER.error("Could not connect to wLightBoxS")
        return False
    elif requests.get(device + "api/device/state").json()['device']['type'] != 'wLightBoxS':
        _LOGGER.error("Not a wLightBoxS device")

    # Add devices
    devices = [device]
    add_entities(wLightBoxS(device) for device in devices)


class wLightBoxS(Light):
    """Representation of an wLightBoxS."""

    def __init__(self, light):
        """Initialize a wLightBoxS."""

        self._light = light
        self._name = None
        self._state = None
        self._brightness = None
        self._supported_features = SUPPORT_BRIGHTNESS

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.
        """

        device_state = requests.get(self._light + "api/light/state")
        brightness_raw = device_state.json()['light']['currentColor']
        brightness = int(brightness_raw, 16)
        self._brightness = brightness
        return self._brightness

    @property
    def is_on(self):
        """Return true if light is on."""

        device_state = requests.get(self._light + "api/light/state")
        brightness_raw = device_state.json()['light']['currentColor']
        brightness = int(brightness_raw, 16)
        if brightness > 0:
            state = True
        else:
            state = False

        self._state = state
        return self._state

    @property
    def supported_features(self):
        """Flag supported features."""
        return self._supported_features

    def turn_on(self, **kwargs):
        """Instruct the light to turn on.
        """

        brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        brigthness_hex = '{0:02x}'.format(brightness)
        requests.get(self._light + "s/" + brigthness_hex)

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""

        requests.get(self._light + "s/00")

    def update(self):
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """

        device_state = requests.get(self._light + "api/device/state")
        sleep(0.5)
        light_state = requests.get(self._light + "api/light/state")

        device_name = device_state.json()['device']['deviceName']
        brightness_raw = light_state.json()['light']['currentColor']
        brightness = int(brightness_raw, 16)
        if brightness > 0:
            state = True
        else:
            state = False

        self._state = state
        self._brightness = brightness
        self._name = device_name
