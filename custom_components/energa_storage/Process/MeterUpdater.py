from datetime import datetime

from ..Constants import *
from ..Utils.Database import Database


class MeterUpdater:
    def __init__(self, hass, importSensor, exportSensor, storagePath):
        self._hass = hass
        self._importSensor = importSensor
        self._exportSensor = exportSensor
        self._storagePath = storagePath

    def update(self):
        importedSensor = self._hass.states.get(self._importSensor)
        exportedSensor = self._hass.states.get(self._exportSensor)

        if not importedSensor or not exportedSensor:
            return
        try:
            self._storeValues(float(importedSensor.state), float(exportedSensor.state))
        except (TypeError, ValueError):
            return

    def _storeValues(self, importedTotal, exportedTotal):
        now = datetime.now().strftime(DATETIME_FORMAT)

        with Database.connect(self._storagePath) as connection:
            connection.execute('''
            INSERT INTO energa_meter (meteredAt, importedTotal, exportedTotal, isProcessed, createdAt, modifiedAt)
            VALUES (?, ?, ?, 0, ?, ?)
            ''', (now, importedTotal, exportedTotal, now, now))
