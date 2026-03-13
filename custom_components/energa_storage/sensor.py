from .Constants import *


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(hass.data[DOMAIN][entry.entry_id][COORDINATOR].getSensorList(), True)
