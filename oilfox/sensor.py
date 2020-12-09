"""Oilfox."""

import logging

import oilfox as test
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_MONITORED_CONDITIONS,
    CONF_PASSWORD,
    PERCENTAGE,
    VOLUME_LITERS,
    TIME_MILLISECONDS
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

"""Platform for sensor integration."""

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "BatteryPercent": [
        "lastMetering",
        "battery",
        "Oilfox Battery",
        PERCENTAGE,
        "mdi:battery-high",
    ],
    "FillingPercentage": [
        "lastMetering",
        "fillingPercentage",
        "Oilfox Filling Percent",
        PERCENTAGE,
        "mdi:percent",
    ],
    "FillingLiter": [
        "lastMetering",
        "liters",
        "Oilfox Filling Liter",
        VOLUME_LITERS,
        "mdi:hydraulic-oil-level",
    ],
    "lastMetering": [
        "lastMetering",
        "serverDate",
        "Oilfox Last Metering",
        TIME_MILLISECONDS,
        "mdi:av-timer",
    ],

}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required("email"): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_MONITORED_CONDITIONS, default=[]): vol.All(
            cv.ensure_list, [vol.In(SENSOR_TYPES)]
        ),
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""

    email = config["email"]
    password = config[CONF_PASSWORD]
    monitoredcondition = config[CONF_MONITORED_CONDITIONS]

    """ Login to oilfox """
    con = test.api(email, password)
    try:
        tester = con.login()
    #_LOGGER.error(tester)
    except:
        _LOGGER.error('Could not connect to oilfox, please restart HA')
    if len(monitoredcondition) == 0:
        monitoredcondition = SENSOR_TYPES.keys()
    for sensor in monitoredcondition:
        add_entities(
            [
                oilfox(
                    con,
                    SENSOR_TYPES[sensor][2],
                    SENSOR_TYPES[sensor][0],
                    SENSOR_TYPES[sensor][1],
                    SENSOR_TYPES[sensor][3],
                    SENSOR_TYPES[sensor][4],
                )
            ]
        )


class oilfox(Entity):
    """Representation of a Sensor."""

    def getData(self):
        """Get sensor data."""
        #_LOGGER.error(self.api.getSummery())
        try:
            value = int(self.api.getSummery()['devices'][0][self.topic][self.sensorvalue])

        except:
            return "error"
        return value

    def __init__(self, con, sensorname, topic, sensorvalue, unit, icon):
        """Initialize the sensor."""
        self.api = con
        self.sensorname = sensorname
        self.topic = topic
        self.sensorvalue = sensorvalue
        self.mdi = icon
        self._unit_of_measurement = unit
        value = self.getData()
        if(value != "error"):
            self._state = value
            self._available = True
        else:
            self._available = False

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.sensorname

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self.mdi

    @property
    def state(self):
        """Return State."""
        return self._state

    @property
    def available(self):
        """Could the device be accessed during the last update call."""
        return self._available

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # self._state = 23
        value = self.getData()
        if(value != "error"):
            self._state = value
            self._available = True
        else:
            self._available = False
