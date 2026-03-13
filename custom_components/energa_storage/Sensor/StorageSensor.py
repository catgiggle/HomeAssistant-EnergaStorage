from homeassistant.components.sensor import SensorEntity

from ..Constants import DOMAIN
from ..Utils.Database import Database


class StorageSensor(SensorEntity):
    def __init__(self, entityName, entityLabel, stateAccuracy, stateUnit, deviceInfo, configName, storagePath):
        self._storagePath = storagePath
        self._isRegistered = False

        self._entityId = f"{configName}_{entityName}"
        self._entityName = entityName
        self._entityLabel = entityLabel
        self._stateAccuracy = stateAccuracy
        self._attr_unique_id = f"{DOMAIN}_{self._entityId}"
        self._attr_device_info = deviceInfo
        self._attr_native_unit_of_measurement = stateUnit
        self._attr_state_class = "measurement"

        self._state = None
        self._createdAt = None
        self._updatedAt = None
        self._changedAt = None

    @property
    def name(self):
        return self._entityLabel if self._isRegistered else self._entityId

    @property
    def native_value(self):
        if self._state is None:
            return None

        if self._stateAccuracy == 0:
            return int(self._state)

        return round(float(self._state), self._stateAccuracy)

    @property
    def extra_state_attributes(self):
        return {
            "created_at": self._createdAt,
            "updated_at": self._updatedAt,
            "changed_at": self._changedAt,
        }

    async def async_added_to_hass(self):
        self._isRegistered = True

    async def async_update(self):
        await self.hass.async_add_executor_job(self._syncUpdate)

    def _syncUpdate(self):
        with Database.connect(self._storagePath) as connection:
            for state, createdAt, updatedAt, changedAt in connection.execute(
                    'SELECT state, createdAt, updatedAt, changedAt FROM sensor_state WHERE name = ?',
                    (self._entityName,),
            ):
                self._state = state
                self._createdAt = createdAt
                self._updatedAt = updatedAt
                self._changedAt = changedAt
