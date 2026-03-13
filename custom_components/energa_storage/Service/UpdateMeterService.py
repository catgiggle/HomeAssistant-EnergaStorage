from datetime import datetime

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.exceptions import HomeAssistantError

from ..Constants import *
from ..Utils.Database import Database


class UpdateMeterService:
    def __init__(self, hass):
        self._hass = hass

    def register(self):
        self._hass.services.async_register(
            DOMAIN,
            'update_meter',
            self.handle,
            schema=vol.Schema({
                vol.Required('entryName'): cv.string,
                vol.Required('importedTotal'): cv.positive_float,
                vol.Required('exportedTotal'): cv.positive_float,
                vol.Required('meteredAt'): cv.datetime
            })
        )

    async def handle(self, request):
        config = self._resolveConfig(self._hass, request.data['entryName'])
        self._storeValue(request, config[STORAGE_PATH])
        config[COORDINATOR].update()

    @staticmethod
    def _resolveConfig(hass, entryName):
        entry = hass.data[DOMAIN][ENTRY_LIST].get(entryName)

        if entry is None:
            raise HomeAssistantError(f"No configuration found for entryName: '{entryName}'")

        return hass.data[DOMAIN][entry]

    @staticmethod
    def _storeValue(request, storagePath):
        with Database.connect(storagePath) as connection:
            connection.execute('''
                INSERT INTO energa_meter (meteredAt, importedTotal, exportedTotal, isProcessed, createdAt, modifiedAt)
                VALUES (?, ?, ?, 0, ?, ?)
            ''', (
                request.data['meteredAt'].strftime(DATETIME_FORMAT),
                request.data['importedTotal'],
                request.data['exportedTotal'],
                datetime.now().strftime(DATETIME_FORMAT),
                datetime.now().strftime(DATETIME_FORMAT)
            ))
