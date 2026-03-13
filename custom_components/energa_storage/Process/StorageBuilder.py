import os

from ..Utils.Database import Database


class StorageBuilder:
    def __init__(self, storagePath):
        self._storagePath = storagePath

    def build(self):
        os.makedirs(os.path.dirname(self._storagePath), exist_ok=True)

        with Database.connect(self._storagePath) as connection:
            connection.execute('''
                CREATE TABLE IF NOT EXISTS energa_meter (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meteredAt DATETIME NOT NULL,
                    importedTotal REAL NOT NULL,
                    exportedTotal REAL NOT NULL,
                    isProcessed INTEGER NOT NULL,
                    createdAt DATETIME NOT NULL,
                    modifiedAt DATETIME NOT NULL
                )
            ''')
            connection.execute('''
                CREATE TABLE IF NOT EXISTS virtual_buffer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    period INT NOT NULL UNIQUE,
                    depositedEnergy REAL NOT NULL,
                    withdrawnEnergy REAL NOT NULL,
                    isActive INTEGER NOT NULL,
                    createdAt DATETIME NOT NULL,
                    modifiedAt DATETIME NOT NULL
                )
            ''')
            connection.execute('''
                CREATE TABLE IF NOT EXISTS sensor_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    state REAL NOT NULL,
                    createdAt DATETIME NOT NULL,
                    updatedAt DATETIME NOT NULL,
                    changedAt DATETIME NOT NULL
                )
            ''')
            connection.execute('''
                CREATE TRIGGER IF NOT EXISTS update_energy_deficit_total_on_insert
                AFTER INSERT ON virtual_buffer
                BEGIN
                    INSERT INTO sensor_state (name, state, createdAt, updatedAt, changedAt)
                    VALUES (
                        'energy_deficit_total',
                        MIN(0, NEW.depositedEnergy - NEW.withdrawnEnergy),
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP
                    )
                    ON CONFLICT(name) DO UPDATE SET
                        state = state + excluded.state,
                        updatedAt = CURRENT_TIMESTAMP,
                        changedAt = CURRENT_TIMESTAMP;
                END;
            ''')
            connection.execute('''
                CREATE TRIGGER IF NOT EXISTS update_energy_deficit_total_on_update
                AFTER UPDATE OF depositedEnergy, withdrawnEnergy ON virtual_buffer
                BEGIN
                    INSERT INTO sensor_state (name, state, createdAt, updatedAt, changedAt)
                    VALUES (
                        'energy_deficit_total',
                        MIN(0, NEW.depositedEnergy - NEW.withdrawnEnergy) - MIN(0, OLD.depositedEnergy - OLD.withdrawnEnergy),
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP
                    )
                    ON CONFLICT(name) DO UPDATE SET
                        state = state + excluded.state,
                        updatedAt = CURRENT_TIMESTAMP,
                        changedAt = CURRENT_TIMESTAMP;
                END;
            ''')
            connection.execute('''
                CREATE TRIGGER IF NOT EXISTS update_energy_lost_total_on_deactivate_buffer
                AFTER UPDATE OF isActive ON virtual_buffer
                FOR EACH ROW WHEN OLD.isActive = 1 AND NEW.isActive = 0
                BEGIN
                    INSERT INTO sensor_state(name, state, createdAt, updatedAt, changedAt)
                    VALUES (
                        'energy_lost_total',
                        MAX(0, NEW.depositedEnergy - NEW.withdrawnEnergy),
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP
                    )
                    ON CONFLICT(name) DO UPDATE SET
                        state = state + excluded.state,
                        updatedAt = CURRENT_TIMESTAMP,
                        changedAt = CURRENT_TIMESTAMP;
                END;
            ''')
