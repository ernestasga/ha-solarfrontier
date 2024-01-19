"""Sensord for Solar Frontier Inverter."""
from python_solarfrontier.utils import UnitConverter

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Solar Frontier sensors based on a config entry."""
    coordinators = hass.data[DOMAIN][entry.entry_id]

    sensors = []
    # Add Power Yield Sensors
    yield_types = ['day', 'month', 'year', 'total']
    for yield_type in yield_types:
        sensors.append(
            SolarFrontierSensor(
                coordinators['power_yield'],
                yield_type,
                f"SF {yield_type.title()} Yield"  # Shorter user-friendly name
            )
        )

    # Add System Info Sensor
    sensors.append(
        SolarFrontierSensor(
            coordinators['system_info'],
            'nominal_power',
            'SF Nominal Power'
        )
    )

    # Add Measurement Sensors
    measurement_keys = [
            'dc_power', 'dc_voltage', 'dc_current', 'ac_voltage_phase_1', 'ac_voltage_phase_2',
            'ac_voltage_phase_3', 'ac_current_phase_1', 'ac_current_phase_2', 'ac_current_phase_3',
            'ac_frequency', 'ac_frequency_phase_1', 'ac_frequency_phase_2', 'ac_frequency_phase_3',
            'ac_power', 'ac_power_phase_1', 'ac_power_phase_2', 'ac_power_phase_3'
    ]
    for key in measurement_keys:
        friendly_name = key.replace('_', ' ').title()
        sensors.append(
            SolarFrontierSensor(
                coordinators['measurements'],
                key,
                f"SF {friendly_name}"
            )
        )

    async_add_entities(sensors, True)

class SolarFrontierSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Solar Frontier Sensor."""

    def __init__(self, coordinator, sensor_type: str, name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._name = name

    @property
    def unique_id(self) -> str:
        """Return a unique ID for this sensor."""
        return f"solar_frontier_{self._sensor_type}_sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self) -> float:
        """Return the state of the sensor as a numeric value."""
        raw_state = self.coordinator.data.get(self._sensor_type)
        if raw_state is None:
            return None
        try:
            converter = UnitConverter()
            return converter.get_value(raw_state)
        except ValueError:
            return None

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        raw_state = self.coordinator.data.get(self._sensor_type)
        if raw_state is None:
            return None
        try:
            converter = UnitConverter()
            return converter.get_unit(raw_state)
        except ValueError:
            return None

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the device class the sensor belongs to."""
        sensor_class_map = {
            'W': SensorDeviceClass.POWER,
            'kW': SensorDeviceClass.POWER,
            'MW': SensorDeviceClass.POWER,
            'V': SensorDeviceClass.VOLTAGE,
            'A': SensorDeviceClass.CURRENT,
            'Hz': SensorDeviceClass.FREQUENCY,
            'Wh': SensorDeviceClass.ENERGY,
            'kWh': SensorDeviceClass.ENERGY,
            'MWh': SensorDeviceClass.ENERGY
        }
        raw_state = self.coordinator.data.get(self._sensor_type)
        if raw_state is None:
            return None
        try:
            converter = UnitConverter()
            unit = converter.get_unit(raw_state)
            return sensor_class_map.get(unit, None)
        except ValueError:
            return None
