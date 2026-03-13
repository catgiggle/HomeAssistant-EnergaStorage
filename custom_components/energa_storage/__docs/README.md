# Energa Storage

This Home Assistant integration provides detailed monitoring of an energy storage system using data you supply. It does
**not collect data itself**; instead, it calculates and tracks:

- The current energy stored in the buffer
- Energy deficits
- Energy lost
- Energy accumulated in the current billing period
- The oldest energy that will expire in the next billing period

---

## Installation

This integration is installed via **HACS**:

1. In Home Assistant, go to **HACS → Integrations → Custom Repositories**.
2. Enter the repository URL "https://github.com/catgiggle/energa_storage".
3. Set type to **Integration**.
4. Click **Add** and then install the integration through HACS.
5. Restart Home Assistant.
6. The integration will appear under **Configuration → Integrations**.



funkcjonalności
dzienne statystki z utility_meter
O tym że dobrze to działa z https://github.com/thedeemling/hass-energa-my-meter


alias: My automation
triggers:
  - trigger: state
    entity_id:
      - sensor.energa_my_meter_01234567_to_grid_strefa_1
      - sensor.energa_my_meter_01234567_from_grid_strefa_1
actions:
  - action: energa_storage.update_meter
    metadata: {}
    data:
      entryName: my_energa_storage
      importedTotal: "{{ states('sensor.energa_my_meter_56500946_from_grid_strefa_1') }}"
      exportedTotal: "{{ states('sensor.energa_my_meter_56500946_to_grid_strefa_1') }}"
      meteredAt: "{{ now() }}"



Krótki opis
jak dodać
funkcjonalności
dzienne statystki z utility_meter
O tym że dobrze to działa z https://github.com/thedeemling/hass-energa-my-meter


alias: My automation
triggers:
  - trigger: state
    entity_id:
      - sensor.energa_my_meter_01234567_to_grid_strefa_1
      - sensor.energa_my_meter_01234567_from_grid_strefa_1
actions:
  - action: energa_storage.update_meter
    metadata: {}
    data:
      entryName: my_energa_storage
      importedTotal: "{{ states('sensor.energa_my_meter_56500946_from_grid_strefa_1') }}"
      exportedTotal: "{{ states('sensor.energa_my_meter_56500946_to_grid_strefa_1') }}"
      meteredAt: "{{ now() }}"
