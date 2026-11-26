# EAC Meter Reading for Home Assistant

The EAC integration retrieves meter reading data from EAC and creates energy sensors in Home Assistant.

For each active meter, the integration creates:

- a **Consumption** sensor for the energy consumed from the grid;
- a **Production** sensor for solar energy exported to the grid, when the meter supports and reports solar production.

Accounts and smart meters must be set up with EAC first. Consult the EAC meter-reading manuals for instructions on creating an account and activating a smart meter:

- [EAC Meter Reading Service](https://meterreading-dso.eac.com.cy/login)

## Installation

### Home Assistant 2026.11 and newer

1. Open **Settings** > **Marketplace**.
2. Select **Add from link**.
3. Enter:

   ```text
   https://github.com/xumxum/ha_eac
   ```

4. Follow the prompts to add the repository.

### Older Home Assistant versions

Install the repository through HACS:

1. Open HACS.
2. Select **Integrations**.
3. Open the menu and select **Custom repositories**.
4. Add `https://github.com/xumxum/ha_eac` as an integration.
5. Download and install **EAC**.
6. Restart Home Assistant.

## Configuration

1. Open **Settings** > **Devices & services**.
2. Select **Add integration**.
3. Search for **EAC**.
4. Enter the username and password used at [meterreading-dso.eac.com.cy](https://meterreading-dso.eac.com.cy/login).

The integration supports active smart meters associated with the account. Meters without solar production data receive only a consumption sensor.

## Meter updates

Only smart meters are supported. Reading updates depend on EAC and are not controlled by this integration:

- EAC makes smart-meter readings available approximately every 24 hours.
- Non-smart meters and manually submitted billing-period readings are not supported.

The integration retrieves and displays the latest readings made available by EAC.

## Sensor usage

The consumption and production sensors can be added to Home Assistant's Energy dashboard as:

- **Consumption** — the grid energy consumed;
- **Production** — the solar energy returned to the grid.
