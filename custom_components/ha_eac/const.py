"""Constants."""
from datetime import timedelta

# Base component constants.
NAME = "EAC"
DOMAIN = "ha_eac"

#CONF_CITY = "city"

# Defaults
DEFAULT_NAME = NAME
SCAN_INTERVAL: timedelta = timedelta(seconds=60*30)