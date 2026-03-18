# Energa Storage

This Home Assistant integration allows detailed monitoring of your energy storage system using data you provide.
It **does not collect data itself**; instead, it calculates and tracks:

- Current energy stored in the buffer
- Energy deficits
- Energy losses
- Energy accumulated in the current billing period
- The oldest energy that will expire in the next billing period

You need to supply energy readings using another integration. This integration works seamlessly
with [hass-energa-my-meter](https://github.com/thedeemling/hass-energa-my-meter). Many thanks
to [@thedeemling](https://github.com/thedeemling), the project’s author, for enabling effortless and reliable data
collection.

## Installation

This integration is installed via **HACS**:

1. In Home Assistant, go to **HACS → Integrations → Custom Repositories**.
2. Enter the repository URL: `https://github.com/catgiggle/HomeAssistant-EnergaStorage`.
3. Set the type to **Integration** and click **Add**.
4. Install the integration through HACS.
5. Restart Home Assistant.
6. The integration will appear under **Configuration → Integrations**.

## Configuration

You can add **multiple instances** of this integration. Each instance has the following parameters:

![installation.png](docs/images/installation.png)

| Parameter                | Description                                                                         |
|--------------------------|-------------------------------------------------------------------------------------|
| `Display name`           | Display name for the instance (shown in Home Assistant UI).                         |
| `Internal name`          | Prefix for all sensor identifiers for this instance. Should be unique per instance. |
| `Exported energy sensor` | Sensor reporting energy exported to storage.                                        |
| `Imported energy sensor` | Sensor reporting energy imported from storage.                                      |

**Important:** Removing an instance does **not delete collected data**. Re-adding an instance with the same
`Internal name` restores previous data. The `Internal name` is also displayed as the **device serial number** in the UI.

## Features

- Tracks energy stored in the buffer.
- Calculates energy deficits and energy losses.
- Reports accumulated energy in the **current billing period**.
- Shows the **oldest energy** that will expire in the next billing period.
- Compatible with energy readings from other sensors/integrations.
- Can be used to generate statistics and automation triggers in Home Assistant.

![features.png](docs/images/features.png)

## Other Statistics

Combine this integration with the [utility_meter](https://www.home-assistant.io/integrations/utility_meter/) component
to track additional statistics, such as daily energy usage:

```yaml
utility_meter:
  daily_energy:
    source: sensor.my_storage_virtual_buffer_total
    cycle: daily
```

This allows you to monitor how much energy is added to or lost from the buffer each day.
