"""Support for departure information for public transport in Munich."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
import logging

from mvg import MvgApi, TransportType
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_NAME, UnitOfTime
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

from .const import (  # pylint: disable=unused-import
    CONF_NEXT_DEPARTURE,
    CONF_STATION,
    CONF_DESTINATIONS,
    CONF_LINES,
    CONF_PRODUCTS ,
    CONF_TIMEOFFSET,
    CONF_NUMBER,
    CONF_PRODUCTS,
    ATTRIBUTION,
    DOMAIN,
)

NONE_ICON = "mdi:clock"

SCAN_INTERVAL = timedelta(seconds=30)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    station = entry.data.get("station")
    destinations = entry.data.get("destinations").split(",")
    lines = entry.data.get("lines").split(",")
    products = entry.data.get("products").split(",")
    timeoffset = entry.data.get("timeoffset")
    number = entry.data.get("number")
    
    async_add_entities([MVGSensor(station, destinations, lines, products, timeoffset, number, station)], True)

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the MVGLive sensor."""
    sensors = []
    MVGSensor(
        nextdeparture.get(CONF_STATION),
        nextdeparture.get(CONF_DESTINATIONS),
        nextdeparture.get(CONF_LINES),
        nextdeparture.get(CONF_PRODUCTS),
        nextdeparture.get(CONF_TIMEOFFSET),
        nextdeparture.get(CONF_NUMBER),
        nextdeparture.get(CONF_NAME),
    )
    add_entities(sensors, True)

class MVGSensor(SensorEntity):
    """Implementation of an MVG sensor."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        station,
        destinations,
        lines,
        products,
        timeoffset,
        number,
        name,
    ):
        """Initialize the sensor."""
        self._station = station
        self._name = name
        self.data = MVGData(
            station, destinations, lines, products, timeoffset, number
        )
        self._state = None
        self._icon = NONE_ICON

    @property
    def name(self):
        """Return the name of the sensor."""
        if self._name:
            return self._name
        return self._station

    @property
    def native_value(self):
        """Return the next departure time."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if not (dep := self.data.departures):
            return None
        attr = dep[0]  # next depature attributes
        attr["departures"] = deepcopy(dep)  # all departures dictionary
        return attr

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def native_unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return UnitOfTime.MINUTES

    def update(self) -> None:
        """Get the latest data and update the state."""
        self.data.update()
        if not self.data.departures:
            self._state = None
            self._icon = NONE_ICON
        else:
            self._state = self.data.departures[0].get("time_in_mins", "-")
            self._icon = self.data.departures[0]["icon"]

def _get_minutes_until_departure(departure_time: int) -> int:
    """Calculate the time difference in minutes between the current time and a given departure time.
    Args:
        departure_time: Unix timestamp of the departure time, in seconds.
    Returns:
        The time difference in minutes, as a float.
    """
    current_time = datetime.now()
    departure_datetime = datetime.fromtimestamp(departure_time)
    time_difference = (departure_datetime - current_time).total_seconds()
    minutes_difference = int(time_difference / 60.0)
    return minutes_difference

class MVGData:
    """Pull data from the mvg.de web page."""

    def __init__(self, station, destinations, lines, products, timeoffset, number):
        """Initialize the sensor."""
        self._station_name = station
        self._destinations = destinations
        self._lines = lines
        self._products = products
        self._timeoffset = timeoffset
        self._number = number
        self._station = MvgApi.station(self._station_name)
        if self._station:
            self.mvg = MvgApi(self._station["id"])
        self.departures = []

    def update(self):
        """Update the connection data."""
        if not self._station or not self.mvg:
            self.departures = []
            _LOGGER.warning(
                "Station cannot be found by name: change name or use station id, e.g. de:99232:2353"
            )
            return
        try:
            _departures = self.mvg.departures(
                offset=self._timeoffset,
                limit=self._number,
                transport_types=[
                    transport_type
                    for transport_type in TransportType
                    if transport_type.value[0] in self._products
                ]
                if self._products
                else None,
            )
        except ValueError:
            self.departures = []
            _LOGGER.warning("Returned data not understood")
            return
        self.departures = []
        for _i, _departure in enumerate(_departures):
            # find the first departure meeting the criteria
            if (
                "" not in self._destinations[:1]
                and _departure["destination"] not in self._destinations
            ):
                continue

            if "" not in self._lines[:1] and _departure["line"] not in self._lines:
                continue

            time_to_departure = _get_minutes_until_departure(_departure["time"])

            if time_to_departure < self._timeoffset:
                continue

            # now select the relevant data
            _nextdep = {}
            for k in ("destination", "line", "type", "cancelled", "icon"):
                _nextdep[k] = _departure.get(k, "")
            _nextdep["time_in_mins"] = time_to_departure
            self.departures.append(_nextdep)
