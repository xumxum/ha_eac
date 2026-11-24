"""Constants."""
from datetime import timedelta

# Base component constants.
NAME = "EAC"
DOMAIN = "ha_eac"

# Defaults
# Scan interval for updating sensor data. Default is 2 hours, even though EAC updates just daily.
SCAN_INTERVAL: timedelta = timedelta(seconds=60*60*2)