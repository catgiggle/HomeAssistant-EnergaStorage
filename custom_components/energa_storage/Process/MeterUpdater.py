import logging
from datetime import datetime

from ..Constants import *
from ..Utils.Database import Database

_LOGGER = logging.getLogger(__name__)


class MeterUpdater:
    def __init__(self, hass, importSensor, exportSensor, storagePath):
        self._hass = hass
        self._importSensor = importSensor
        self._exportSensor = exportSensor
        self._storagePath = storagePath

    def update(self):
        try:
            importedTotal = self._hass.states.get(self._importSensor).state
            exportedTotal = self._hass.states.get(self._exportSensor).state

            self._storeValues(float(importedTotal), float(exportedTotal))
        except (TypeError, ValueError):
            return

    def _storeValues(self, importedTotal, exportedTotal):
        now = datetime.now().strftime(DATETIME_FORMAT)

        with Database.connect(self._storagePath) as connection:
            connection.execute('''
                               INSERT INTO energa_meter (meteredAt, importedTotal, exportedTotal, isProcessed,
                                                         createdAt, modifiedAt)
                               VALUES (?, ?, ?, 0, ?, ?)
                               ''', (now, importedTotal, exportedTotal, now, now))
