class Coordinator:
    def __init__(self, sensorList, bufferUpdater, sensorUpdater):
        self._sensorList = sensorList
        self._bufferUpdater = bufferUpdater
        self._sensorUpdater = sensorUpdater

    def getSensorList(self):
        return self._sensorList

    def getBufferUpdater(self):
        return self._bufferUpdater

    def getSensorUpdater(self):
        return self._sensorUpdater

    def update(self, shouldUpdateSensors=True):
        self._bufferUpdater.update()
        self._sensorUpdater.update()

        if not shouldUpdateSensors:
            return

        for sensor in self._sensorList:
            sensor.async_schedule_update_ha_state()
