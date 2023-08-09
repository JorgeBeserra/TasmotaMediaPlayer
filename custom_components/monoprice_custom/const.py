"""Constants for the Monoprice 6-Zone Amplifier Media Player component."""

DOMAIN = "monoprice"

CONF_NAME = "monoprice"

CONF_SOURCES = "sources"

CONF_SOURCE_1 = "source_1"
CONF_SOURCE_2 = "source_2"
CONF_SOURCE_3 = "source_3"
CONF_SOURCE_4 = "source_4"
CONF_SOURCE_5 = "source_5"
CONF_SOURCE_6 = "source_6"

CONF_NOT_FIRST_RUN = "not_first_run"

SERVICE_SNAPSHOT = "snapshot"
SERVICE_RESTORE = "restore"

SERVICE_SET_FRONT_LEFT = "set_front_left"
SERVICE_SET_FRONT_RIGHT = "set_front_right"
SERVICE_SET_CENTER = "set_center"
SERVICE_SET_REAR_LEFT = "set_rear_left"
SERVICE_SET_REAR_RIGHT = "set_rear_right"
SERVICE_SET_SUBWOOFER = "set_subwoofer"

SERVICE_SET_BALANCE = "set_balance"
SERVICE_SET_BASS = "set_bass"
SERVICE_SET_MIDDLE = "set_middle"
SERVICE_SET_TREBLE = "set_treble"

FIRST_RUN = "first_run"
MONOPRICE_OBJECT = "['zone_status':{14,1,1,1,1,0,0,0,0,0,1}]"
UNDO_UPDATE_LISTENER = "update_update_listener"

ATTR_FRONT_LEFT = "level"
ATTR_FRONT_RIGHT = "level"
ATTR_CENTER = "level"
ATTR_REAR_LEFT = "level"
ATTR_REAR_RIGHT = "level"
ATTR_SUBWOOFER = "level"

ATTR_BALANCE = "level"
ATTR_BASS = "level"
ATTR_MIDDLE = "level"
ATTR_TREBLE = "level"

CONF_DELAY = 0.5
CONF_CONTROLLER_DATA = "controller_data"
SUPPORTED_CONTROLLER = "MQTT"
COMMANDS_ENCODING = "Raw"
COMMANDS = {"off": "OFF", "on": "ON", "volumeSet": "volumeSet", "volumeDown": "volumeDown", "volumeUp": "volumeUp", "frontLeft": "frontleft", "frontRight": "frontright", "rearLeft": "rearleft", "rearright": "rearright", "center": "MUTE", "subwoofer": "subwoofer", "mute": "mute", "3d": "3d", "tone": "tone"}