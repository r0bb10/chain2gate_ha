# Chain2Gate

Chain2Gate component for Home Assistant.

This is a custom component for Chain2Gate by MAC s.r.l.

The sensors imported in HomeAssistant are:
 - Instant Power (W)
 - Quarter-hour Average Power (W)
 - Quarter-hour Active Energy (Wh)
 - Total Active Energy (Wh)
 - Tariff Code

The sensors are updated once every 15 minutes (when a CF1 frame is received), the `Instant Power` sensor is also updated when a CF21 or CF22 frames are received (at 300 W intervals or when exceeding nominal available power).

In addition, when a CF22 frame (available power excess) a `chain2gate_power_limit_exceeded` event is fired with the following data:
 - `instant_power`: the current instant power,
 - `available_power`: the nominal available power,
 - `switch_off_seconds`: seconds until the switch-off.

## Installation

### Manual
Place the files inside `custom_components` in your `$CONFIG/custom_components` directory and restart HomeAssistant.

### HACS
Add a custom repository to HACS using the URL of this repository.

## Configuration
Once installed the component appears as an integration in HomeAssistant, you just have to provide the host (IP address, local domain, etc...) and the device should appear.