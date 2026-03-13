import math
from datetime import datetime

from dateutil.relativedelta import relativedelta

from ..Constants import *
from ..Utils.Database import Database


class BufferUpdater:
    def __init__(self, storagePath):
        self._storagePath = storagePath

    def update(self):
        with Database.connect(self._storagePath) as connection:
            recentImportedTotal, recentExportedTotal = self._resolveRecentTotals(connection)

            for currentMeasureId, currentMeteredAt, currentImportedTotal, currentExportedTotal in self._findUnprocessedMeters(connection):
                # Determine period
                meteredDate = datetime.strptime(currentMeteredAt[:10], '%Y-%m-%d')
                currentPeriod = self._resolvePeriodForDate(meteredDate)
                minimalPeriod = self._resolvePeriodForDate(meteredDate - relativedelta(months=12))

                # Detect meter resetting
                recentImportedTotal = 0 if recentImportedTotal > currentImportedTotal else recentImportedTotal
                recentExportedTotal = 0 if recentExportedTotal > currentExportedTotal else recentExportedTotal

                # Calculate delta of totals
                deltaImportedTotal = currentImportedTotal - recentImportedTotal
                deltaExportedTotal = currentExportedTotal - recentExportedTotal

                # Calculate taxed produced energy
                taxedProducedEnergy = round(0.8 * deltaExportedTotal, 4)

                # Process current measure
                self._invalidateExpiredBuffer(connection, minimalPeriod)
                self._increaseVirtualBuffer(connection, currentPeriod, taxedProducedEnergy)
                self._decreaseVirtualBuffer(connection, currentPeriod, deltaImportedTotal)
                self._markMeterAsProcessed(connection, currentMeasureId)

                # Prepare for next iteration
                recentImportedTotal = currentImportedTotal
                recentExportedTotal = currentExportedTotal

    @staticmethod
    def _resolvePeriodForDate(date):
        return math.ceil((date.year * 100 + date.month) / 2) * 2

    @staticmethod
    def _resolveRecentTotals(connection):
        result = connection.execute('''
            SELECT importedTotal, exportedTotal
            FROM energa_meter
            WHERE isProcessed = 1
            ORDER BY createdAt DESC
            LIMIT 1
        ''').fetchone()

        return (result[0], result[1]) if result else (0, 0)

    @staticmethod
    def _findUnprocessedMeters(connection):
        connection.execute('''
            SELECT id, meteredAt, importedTotal, exportedTotal
            FROM energa_meter
            WHERE isProcessed = 0
            ORDER BY createdAt ASC
        ''')

        return connection.fetchall()

    @staticmethod
    def _markMeterAsProcessed(connection, currentMeasureId):
        now = datetime.now().strftime(DATETIME_FORMAT)
        connection.execute('''
            UPDATE energa_meter
            SET isProcessed = 1, modifiedAt = ?
            WHERE id = ?
        ''', (now, currentMeasureId))

    @staticmethod
    def _findActiveBuffers(connection):
        connection.execute('''
            SELECT id, depositedEnergy, withdrawnEnergy
            FROM virtual_buffer
            WHERE isActive = 1
            ORDER BY period ASC
        ''')

        return connection.fetchall()

    @staticmethod
    def _invalidateExpiredBuffer(connection, minimalPeriod):
        now = datetime.now().strftime(DATETIME_FORMAT)
        connection.execute('''
            UPDATE virtual_buffer
            SET isActive = 0, modifiedAt = ?
            WHERE isActive = 1 AND period < ?
        ''', (now, minimalPeriod))

    @staticmethod
    def _increaseVirtualBuffer(connection, currentPeriod, depositedEnergy):
        now = datetime.now().strftime(DATETIME_FORMAT)
        connection.execute('''
            INSERT INTO virtual_buffer (period, depositedEnergy, withdrawnEnergy, isActive, createdAt, modifiedAt)
            VALUES (?, ?, 0, 1, ?, ?)
            ON CONFLICT (period) DO UPDATE SET
                depositedEnergy = depositedEnergy + excluded.depositedEnergy,
                modifiedAt = excluded.modifiedAt
        ''', (currentPeriod, depositedEnergy, now, now))

    def _decreaseVirtualBuffer(self, connection, currentPeriod, withdrawnEnergy):
        now = datetime.now().strftime(DATETIME_FORMAT)

        for bufferId, bufferDepositedEnergy, bufferWithdrawnEnergy in self._findActiveBuffers(connection):
            bufferAvailableEnergy = bufferDepositedEnergy - bufferWithdrawnEnergy
            consumedBufferEnergy = min(bufferAvailableEnergy, withdrawnEnergy)
            withdrawnEnergy -= consumedBufferEnergy

            connection.execute('''
                UPDATE virtual_buffer
                SET withdrawnEnergy = withdrawnEnergy + ?, modifiedAt = ?
                WHERE id = ?
            ''', (consumedBufferEnergy, now, bufferId))

        if withdrawnEnergy > 0:
            connection.execute('''
                INSERT INTO virtual_buffer (period, depositedEnergy, withdrawnEnergy, isActive, createdAt, modifiedAt)
                VALUES (?, 0, ?, 1, ?, ?)
                ON CONFLICT (period) DO UPDATE SET
                    withdrawnEnergy = withdrawnEnergy + excluded.withdrawnEnergy,
                    modifiedAt = excluded.modifiedAt
            ''', (currentPeriod, withdrawnEnergy, now, now))
