from datetime import datetime

from homeassistant.helpers.template import is_number

from ..Constants import *
from ..Utils.Database import Database


class MeterUpdater:
    def __init__(self, hass, importSensor, exportSensor, storagePath):
        self._hass = hass
        self._importSensor = importSensor
        self._exportSensor = exportSensor
        self._storagePath = storagePath

    def update(self):
        importSensor = self._hass.states.get(self._importSensor)
        importedTotal = importSensor.state if importSensor else None
        exportSensor = self._hass.states.get(self._exportSensor)
        exportedTotal = exportSensor.state if exportSensor else None

        if is_number(importedTotal) and is_number(exportedTotal):
            self._storeValues(importedTotal, exportedTotal)

    def _storeValues(self, importedTotal, exportedTotal):
        now = datetime.now().strftime(DATETIME_FORMAT)

        with Database.connect(self._storagePath) as connection:
            connection.execute('''
                INSERT INTO energa_meter (meteredAt, importedTotal, exportedTotal, isProcessed, createdAt, modifiedAt)
                VALUES (?, ?, ?, 0, ?, ?)
            ''', (now, importedTotal, exportedTotal, now, now))
