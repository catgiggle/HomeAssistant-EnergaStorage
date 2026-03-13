import logging

from homeassistant.const import UnitOfEnergy
from homeassistant.helpers.device_registry import DeviceInfo

from .Constants import *
from .Process.BufferUpdater import BufferUpdater
from .Process.Coordinator import Coordinator
from .Process.SensorUpdater import SensorUpdater
from .Process.StorageBuilder import StorageBuilder
from .Sensor.StorageSensor import StorageSensor
from .Service.UpdateMeterService import UpdateMeterService

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, _config):
    UpdateMeterService(hass).register()

    return True


async def async_setup_entry(hass, entry):
    entryConfig = _createEntryConfig(hass, entry)

    StorageBuilder(entryConfig[STORAGE_PATH]).build()
    entryConfig[COORDINATOR].update(shouldUpdateSensors=False)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass, entry):
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    _removeEntryConfig(hass, entry)

    return True


def _createEntryConfig(hass, entry):
    entryConfig = _parseEntryConfig(hass, entry)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entryConfig

    hass.data[DOMAIN].setdefault(ENTRY_LIST, {})
    hass.data[DOMAIN][ENTRY_LIST][entryConfig[CONFIG_NAME]] = entry.entry_id

    return entryConfig


def _removeEntryConfig(hass, entry):
    entryConfig = hass.data[DOMAIN][entry.entry_id]
    hass.data[DOMAIN].pop(entry.entry_id)
    hass.data[DOMAIN][ENTRY_LIST].pop(entryConfig[CONFIG_NAME], None)


def _parseEntryConfig(hass, entry):
    entryConfig = {
        CONFIG_NAME: entry.data.get(CONFIG_NAME),
        CONFIG_LABEL: entry.data.get(CONFIG_LABEL),
        STORAGE_PATH: hass.config.path(f".storage/{DOMAIN}/{entry.data.get(CONFIG_NAME)}.db"),
    }
    entryConfig[DEVICE_INFO] = _buildDeviceForEntry(entry, entryConfig[CONFIG_NAME], entryConfig[CONFIG_LABEL])
    entryConfig[COORDINATOR] = _buildCoordinator(entryConfig[DEVICE_INFO], entryConfig[CONFIG_NAME], entryConfig[STORAGE_PATH])

    return entryConfig


def _buildDeviceForEntry(entry, name, label):
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=label,
        model=f"{NAME} ({name})",
        manufacturer=AUTHOR,
        sw_version=VERSION,
    )


def _buildCoordinator(deviceInfo, configName, storagePath):
    return Coordinator(
        [
            StorageSensor('virtual_buffer_total', 'Total Virtual Buffer', 0, UnitOfEnergy.KILO_WATT_HOUR, deviceInfo, configName, storagePath),
            StorageSensor('virtual_buffer_head', 'Virtual Buffer Head', 0, UnitOfEnergy.KILO_WATT_HOUR, deviceInfo, configName, storagePath),
            StorageSensor('virtual_buffer_tail', 'Virtual Buffer Tail', 0, UnitOfEnergy.KILO_WATT_HOUR, deviceInfo, configName, storagePath),
            StorageSensor('energy_deficit_total', 'Total Energy Deficit', 0, UnitOfEnergy.KILO_WATT_HOUR, deviceInfo, configName, storagePath),
            StorageSensor('energy_lost_total', 'Total Energy Lost', 0, UnitOfEnergy.KILO_WATT_HOUR, deviceInfo, configName, storagePath),
        ],
        BufferUpdater(storagePath),
        SensorUpdater(storagePath),
    )
