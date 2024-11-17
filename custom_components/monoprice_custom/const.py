"""Constants for the Monoprice 6-Zone Amplifier Media Player component."""

CONF_NAME = "monoprice"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_SOURCES = "sources"
CONF_SOURCE_1 = "source_1"
CONF_SOURCE_2 = "source_2"
CONF_DELAY = 0.5
CONF_NOT_FIRST_RUN = "not_first_run"
CONF_CONTROLLER_DATA = "controller_data"

DOMAIN = "monoprice"

FIRST_RUN = "first_run"
MONOPRICE_OBJECT = "['zone_status':{14,1,1,1,1,0,0,0,0,0,1}]"

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
SERVICE_SET_MUTE = "set_mute"
SERVICE_SET_3D = "set_3d"
SERVICE_SET_TONE = "set_tone"

UNDO_UPDATE_LISTENER = "update_update_listener"
MAX_VOLUME = 79
PARALLEL_UPDATES = 1

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

SUPPORTED_CONTROLLER = "MQTT"
COMMANDS_ENCODING = "Raw"

COMMANDS = {
    "status": "status",
    "snapshot": "snapshot",
    "off": "off",
    "on": "on",
    "volumeSet": "volume",
    "volumeUp": "volume",
    "volumeDown": "volume",
    "frontLeft": "front_left",
    "frontRight": "front_right",
    "center": "center",
    "rearLeft": "rear_left",
    "rearRight": "rear_right",
    "subwoofer": "subwoofer",
    "balance": "balance",
    "bass": "bass",
    "middle": "middle",
    "treble": "treble",
    "3d": "3d",
    "tone": "tone",
    "mute": "mute",
    "setNormalBass": "set_normal_bass",
    "setHighBass": "set_high_bass",
    "setMediumBass": "set_medium_bass",
    "setLowBass": "set_low_bass",
}
