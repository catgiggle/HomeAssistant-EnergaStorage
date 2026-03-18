class Coordinator:
    def __init__(self, sensorList, meterUpdater, bufferUpdater, sensorUpdater):
        self._sensorList = sensorList
        self._meterUpdater = meterUpdater
        self._bufferUpdater = bufferUpdater
        self._sensorUpdater = sensorUpdater

    def getSensorList(self):
        return self._sensorList

    def getMeterUpdater(self):
        return self._meterUpdater

    def getBufferUpdater(self):
        return self._bufferUpdater

    def getSensorUpdater(self):
        return self._sensorUpdater

    def update(self, shouldUpdateSensors=True):
        self._meterUpdater.update()
        self._bufferUpdater.update()
        self._sensorUpdater.update()

        if not shouldUpdateSensors:
            return

        for sensor in self._sensorList:
            sensor.async_schedule_update_ha_state()
