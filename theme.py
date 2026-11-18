"""
theme.py - terminal color themes and text colors.

Holds the available color themes, remembers which one is active, and
saves each user's choices to a .txt file so they come back at the next
login.

Besides the theme, an Administrator can pick a text color (Blue, White,
or Red). The text color replaces the theme's normal text color.

This file does not import any other project file, so every other file
can safely use it.
"""

DEFAULT_THEME = "Classic Green"
DEFAULT_TEXT_COLOR = "Theme default"

# Every theme defines the same four color roles:
#   main   normal text and table borders
#   accent labels, headings, and prompts
#   error  error messages
#   title  the bar behind screen titles
THEMES = {
    "Classic Green": {"main": "\033[92m", "accent": "\033[93m",
                      "error": "\033[91m", "title": "\033[30;42m"},
    "Ocean Blue":    {"main": "\033[96m", "accent": "\033[97m",
                      "error": "\033[91m", "title": "\033[30;46m"},
    "Amber Retro":   {"main": "\033[33m", "accent": "\033[93m",
                      "error": "\033[91m", "title": "\033[30;43m"},
    "Royal Purple":  {"main": "\033[95m", "accent": "\033[96m",
                      "error": "\033[91m", "title": "\033[97;45m"},
}

# Text colors an Administrator can choose (replaces the "main" role).
TEXT_COLORS = {
    "Blue":  "\033[94m",
    "White": "\033[97m",
    "Red":   "\033[91m",
}

# Gradient used for the banner: a list of (red, green, blue) color stops
# that the banner fades through from left to right and top to bottom.
GRADIENTS = {
    "Classic Green": [(0, 255, 70), (170, 255, 0), (255, 225, 0)],
    "Ocean Blue":    [(0, 210, 255), (80, 120, 255), (185, 100, 255)],
    "Amber Retro":   [(255, 205, 0), (255, 125, 0), (255, 60, 40)],
    "Royal Purple":  [(200, 80, 255), (255, 80, 200), (255, 150, 120)],
}

_active = DEFAULT_THEME
_text_color = DEFAULT_TEXT_COLOR


# ----------------------------------------------------------------------
# THEMES
# ----------------------------------------------------------------------
def theme_names():
    """Names of all themes, in display order."""
    return list(THEMES)


def get_theme():
    """Name of the theme that is active right now."""
    return _active


def set_theme(name):
    """Make a theme active. Returns False if the name is unknown."""
    global _active
    if name not in THEMES:
        return False
    _active = name
    return True


# ----------------------------------------------------------------------
# TEXT COLOR
# ----------------------------------------------------------------------
def text_color_names():
    """Text colors to choose from, ending with the 'Theme default' option."""
    return list(TEXT_COLORS) + [DEFAULT_TEXT_COLOR]


def get_text_color():
    """Name of the text color in use ('Theme default' if none is chosen)."""
    return _text_color


def set_text_color(name):
    """Choose a text color. Returns False if the name is unknown."""
    global _text_color
    if name != DEFAULT_TEXT_COLOR and name not in TEXT_COLORS:
        return False
    _text_color = name
    return True


# ----------------------------------------------------------------------
# COLOR LOOKUP
# ----------------------------------------------------------------------
def reset_theme():
    """Back to the default theme and text color (used on logout)."""
    set_theme(DEFAULT_THEME)
    set_text_color(DEFAULT_TEXT_COLOR)


def gradient_stops():
    """Color stops for the banner gradient. Returns None when the
    Administrator picked a text color, so the banner uses that one color."""
    if _text_color in TEXT_COLORS:
        return None
    return GRADIENTS[_active]


def color(role):
    """ANSI color code of a role ('main', 'accent', 'error', 'title')."""
    if role == "main" and _text_color in TEXT_COLORS:
        return TEXT_COLORS[_text_color]
    return THEMES[_active][role]


# ----------------------------------------------------------------------
# SAVING AND LOADING A USER'S SETTINGS
# File format, one line per user:  username|theme|text_color
# (older lines with only  username|theme  still load fine)
# ----------------------------------------------------------------------
def _read_settings(path):
    settings = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.rstrip("\n").split("|")
                if len(parts) == 2:
                    parts.append(DEFAULT_TEXT_COLOR)
                if len(parts) == 3:
                    settings[parts[0]] = (parts[1], parts[2])
    except (OSError, UnicodeDecodeError):
        pass
    return settings


def load_user_theme(username, path):
    """Activate the theme and text color saved for this user."""
    reset_theme()
    saved = _read_settings(path).get(username)
    if saved:
        set_theme(saved[0])
        set_text_color(saved[1])


def save_user_settings(username, path):
    """Save the theme and text color that are active right now.
    Returns True if they were saved."""
    settings = _read_settings(path)
    settings[username] = (get_theme(), get_text_color())
    try:
        with open(path, "w", encoding="utf-8") as f:
            for name, (theme, text) in settings.items():
                f.write(f"{name}|{theme}|{text}\n")
        return True
    except OSError:
        return False
