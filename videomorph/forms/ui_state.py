from enum import Enum, auto

class AppState(Enum):
    """Application states for UI configuration."""
    EMPTY = auto()
    READY = auto()
    RUNNING = auto()
    STOPPED = auto()  # When stopped by user or error
    DONE = auto()

# Configuration for each state
# Keys match the widget names or logical groups in VideoMorphMW
UI_STATE_CONFIG = {
    AppState.EMPTY: {
        "add": True,
        "convert": False,
        "clear": False,
        "remove": False,
        "stop": False,
        "stop_all": False,
        "presets": False,
        "profiles": False,
        "output_dir": True,
        "subtitles_chb": False,
        "delete_chb": False,
        "tag_chb": False,
        "shutdown_chb": False,
        "play_input": False,
        "play_output": False,
        "info": False,
    },
    AppState.READY: {
        "add": True,
        "convert": True,
        "clear": True,
        "remove": True,
        "stop": False,
        "stop_all": False,
        "presets": True,
        "profiles": True,
        "output_dir": True,
        "subtitles_chb": True,
        "delete_chb": True,
        "tag_chb": True,
        "shutdown_chb": True,
        "play_input": False, # Logic in original was False for ready? 
                             # update_ui_when_ready set play_input=False. 
                             # But _enable_context_menu_action enables it.
                             # Let's stick to the original logic for now.
        "play_output": False,
        "info": False,
    },
    AppState.RUNNING: {
        "add": True,
        "convert": False,
        "clear": False,
        "remove": False,
        "stop": True,
        "stop_all": True,
        "presets": False,
        "profiles": False,
        "output_dir": False,
        "subtitles_chb": False,
        "delete_chb": False,
        "tag_chb": False,
        "shutdown_chb": True,
        "play_input": False,
        "play_output": False,
        "info": False,
    },
    AppState.STOPPED: {
        "add": True,
        "convert": True,
        "clear": True,
        "remove": False,
        "stop": False,
        "stop_all": False,
        "presets": True,
        "profiles": True,
        "output_dir": True,
        "subtitles_chb": True,
        "delete_chb": True,
        "tag_chb": True,
        "shutdown_chb": True,
        "play_input": False,
        "play_output": False,
        "info": False,
    },
    AppState.DONE: {
        "add": True,
        "convert": False,
        "clear": True,
        "remove": False,
        "stop": False,
        "stop_all": False,
        "presets": True,
        "profiles": True,
        "output_dir": True,
        "subtitles_chb": True,
        "delete_chb": True,
        "tag_chb": True,
        "shutdown_chb": True,
        "play_input": False,
        "play_output": False,
        "info": False,
    },
}
