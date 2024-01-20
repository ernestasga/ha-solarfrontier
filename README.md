# Solar Frontier Custom Integration for Home Assistant

<div align="center">
  <img src="https://github.com/ernestasga/python-solarfrontier/blob/main/images/solar-frontier-logo.png?raw=true" alt="solar-frontier-logo" >
</div>

Custom integration for Solar Frontier inverters. Based on [python-solarfrontier library](https://github.com/ernestasga/python-solarfrontier)

## Compatibility

**Confirmed to work with:**

* SF-WR-5503x

## Install

### via HACS
1. Go to HACS -> Integrations -> Custom repositories
2. Paste https://github.com/ernestasga/ha-solarfrontier and select Categoty - Integration
4. Go to Settings -> Integrations -> Add Integration
5. Search Solar Frontier and enter IP address of the inverter

### Manual
1. Download the repository
2. Copy the `custom_components/solarfrontier` folder into the `custom_components` folder of your Home Assistant installation.
3. Go to Settings -> Integrations -> Add Integration
4. Search Solar Frontier and enter IP address of the inverter