import logging
from functools import partial

from homeassistant.const import UnitOfEnergy
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_track_state_change_event

from .Constants import *
from .Process.BufferUpdater import BufferUpdater
from .Process.Coordinator import Coordinator
from .Process.MeterUpdater import MeterUpdater
from .Process.SensorUpdater import SensorUpdater
from .Process.StorageBuilder import StorageBuilder
from .Sensor.StorageSensor import StorageSensor

_LOGGER = logging.getLogger(__name__)


async def async_setup(_hass, _config):
    return True


async def async_setup_entry(hass, entry):
    entryConfig = _createEntryConfig(hass, entry)

    StorageBuilder(entryConfig[STORAGE_PATH]).build()
    entryConfig[COORDINATOR].update(shouldUpdateSensors=False)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entryConfig[METER_UNSUBSCRIBER] = async_track_state_change_event(hass, [
        entryConfig[CONFIG_SENSOR_IMPORTED],
        entryConfig[CONFIG_SENSOR_EXPORTED]
    ], partial(_onTracedSensorChanged, coordinator=entryConfig[COORDINATOR]))

    return True


async def async_unload_entry(hass, entry):
    entryConfig = hass.data[DOMAIN][entry.entry_id]

    if entryConfig[METER_UNSUBSCRIBER] is not None:
        entryConfig[METER_UNSUBSCRIBER]()
        entryConfig[METER_UNSUBSCRIBER] = None

    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    _removeEntryConfig(hass, entry)

    return True


def _createEntryConfig(hass, entry):
    entryConfig = _parseEntryConfig(hass, entry)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entryConfig

    return entryConfig


def _removeEntryConfig(hass, entry):
    hass.data[DOMAIN].pop(entry.entry_id)


def _parseEntryConfig(hass, entry):
    entryConfig = {
        CONFIG_NAME: entry.data.get(CONFIG_NAME),
        CONFIG_LABEL: entry.data.get(CONFIG_LABEL),
        CONFIG_SENSOR_IMPORTED: entry.data.get(CONFIG_SENSOR_IMPORTED),
        CONFIG_SENSOR_EXPORTED: entry.data.get(CONFIG_SENSOR_EXPORTED),
        STORAGE_PATH: hass.config.path(f".storage/{DOMAIN}/{entry.data.get(CONFIG_NAME)}.db"),
    }
    entryConfig[DEVICE_INFO] = _buildDeviceForEntry(entry, entryConfig[CONFIG_NAME], entryConfig[CONFIG_LABEL])
    entryConfig[COORDINATOR] = _buildCoordinator(
        hass,
        entryConfig[DEVICE_INFO],
        entryConfig[CONFIG_NAME],
        entryConfig[STORAGE_PATH],
        entryConfig[CONFIG_SENSOR_IMPORTED],
        entryConfig[CONFIG_SENSOR_EXPORTED]
    )

    return entryConfig


def _buildDeviceForEntry(entry, name, label):
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=label,
        model=NAME,
        serial_number=name,
        manufacturer=AUTHOR,
        sw_version=VERSION,
    )


def _buildCoordinator(hass, deviceInfo, configName, storagePath, importSensor, exportSensor):
    return Coordinator(
        [
            StorageSensor('virtual_buffer_total', 'Total Virtual Buffer', 0, UnitOfEnergy.KILO_WATT_HOUR, deviceInfo, configName, storagePath),
            StorageSensor('virtual_buffer_head', 'Virtual Buffer Head', 0, UnitOfEnergy.KILO_WATT_HOUR, deviceInfo, configName, storagePath),
            StorageSensor('virtual_buffer_tail', 'Virtual Buffer Tail', 0, UnitOfEnergy.KILO_WATT_HOUR, deviceInfo, configName, storagePath),
            StorageSensor('energy_deficit_total', 'Total Energy Deficit', 0, UnitOfEnergy.KILO_WATT_HOUR, deviceInfo, configName, storagePath),
            StorageSensor('energy_lost_total', 'Total Energy Lost', 0, UnitOfEnergy.KILO_WATT_HOUR, deviceInfo, configName, storagePath),
        ],
        MeterUpdater(hass, importSensor, exportSensor, storagePath),
        BufferUpdater(storagePath),
        SensorUpdater(storagePath),
    )


async def _onTracedSensorChanged(_event, coordinator):
    coordinator.update()
