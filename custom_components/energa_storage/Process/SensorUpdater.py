from datetime import datetime

from ..Constants import *
from ..Utils.Database import Database


class SensorUpdater:
    def __init__(self, storagePath):
        self._storagePath = storagePath

    def update(self):
        with Database.connect(self._storagePath) as connection:
            data = connection.execute('SELECT COALESCE(SUM(MAX(depositedEnergy - withdrawnEnergy, 0)), 0) FROM virtual_buffer WHERE isActive = 1').fetchone()
            self._storeState(connection, 'virtual_buffer_total', data[0] if data else 0)

            data = connection.execute('SELECT MAX(depositedEnergy - withdrawnEnergy, 0) FROM virtual_buffer WHERE isActive = 1 ORDER BY period DESC LIMIT 1').fetchone()
            self._storeState(connection, 'virtual_buffer_head', data[0] if data else 0)

            data = connection.execute('SELECT MAX(depositedEnergy - withdrawnEnergy, 0) FROM virtual_buffer WHERE isActive = 1 ORDER BY period ASC LIMIT 1').fetchone()
            self._storeState(connection, 'virtual_buffer_tail', data[0] if data else 0)

    @staticmethod
    def _storeState(connection, name, state):
        now = datetime.now().strftime(DATETIME_FORMAT)

        connection.execute('''
            INSERT INTO sensor_state (name, state, createdAt, updatedAt, changedAt)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                state = excluded.state,
                updatedAt = excluded.updatedAt,
                changedAt = CASE
                    WHEN sensor_state.state = excluded.state
                    THEN sensor_state.changedAt
                    ELSE excluded.changedAt
                END
        ''', (name, state, now, now, now))
