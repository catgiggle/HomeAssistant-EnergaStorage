import re

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig
from homeassistant.util import slugify

from .Constants import *


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        formData = user_input or {}
        formErrors = {}

        fieldLabelValue = formData.get(CONFIG_LABEL, '').strip()
        fieldNameValue = formData.get(CONFIG_NAME, '').strip()
        fieldSensorExportedValue = formData.get(CONFIG_SENSOR_EXPORTED, '').strip()
        fieldSensorImportedValue = formData.get(CONFIG_SENSOR_IMPORTED, '').strip()

        normalizedName = None

        if user_input is not None:
            if not re.search(r'[a-zA-Z]', fieldLabelValue):
                formErrors[CONFIG_LABEL] = 'invalid_label'

            if fieldNameValue:
                if fieldNameValue == slugify(fieldNameValue):
                    normalizedName = fieldNameValue
                else:
                    formErrors[CONFIG_NAME] = 'invalid_name'
            else:
                normalizedName = slugify(fieldLabelValue)

            if self.hass.states.get(fieldSensorExportedValue) is None:
                formErrors[CONFIG_SENSOR_EXPORTED] = "entity_not_found"

            if self.hass.states.get(fieldSensorImportedValue) is None:
                formErrors[CONFIG_SENSOR_IMPORTED] = "entity_not_found"

            if not formErrors:
                return self.async_create_entry(title=fieldLabelValue, data={
                    CONFIG_LABEL: fieldLabelValue,
                    CONFIG_NAME: normalizedName,
                    CONFIG_SENSOR_EXPORTED: fieldSensorExportedValue,
                    CONFIG_SENSOR_IMPORTED: fieldSensorImportedValue,
                })

        return self.async_show_form(
            step_id='user',
            data_schema=vol.Schema({
                vol.Required(CONFIG_LABEL, default=fieldLabelValue): cv.string,
                vol.Optional(CONFIG_NAME, default=fieldNameValue): cv.string,
                vol.Required(CONFIG_SENSOR_EXPORTED, default=fieldSensorExportedValue): EntitySelector(
                    EntitySelectorConfig(include_entities=self._listAvailableSensors(), multiple=False)
                ),
                vol.Required(CONFIG_SENSOR_IMPORTED, default=fieldSensorImportedValue): EntitySelector(
                    EntitySelectorConfig(include_entities=self._listAvailableSensors(), multiple=False, )
                )
            }),
            errors=formErrors
        )

    def _listAvailableSensors(self):
        return [
            e.entity_id
            for e in self.hass.states.async_all()
            if e.entity_id.startswith('sensor.')
               and e.attributes.get('device_class') == 'energy'
               and e.attributes.get('state_class') == 'total_increasing'
        ]
