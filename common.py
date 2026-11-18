"""
common.py - shared settings and helpers used by every part of the program.

Contains: configuration, colors and display helpers, input helpers
(including the * password input), file handling, and password hashing.
"""

import hashlib
import hmac
import os
import re
import secrets
import sys

from theme import color

# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.txt")
STUDENTS_FILE = os.path.join(DATA_DIR, "students.txt")
SUBJECTS_FILE = os.path.join(DATA_DIR, "subjects.txt")
GRADES_FILE = os.path.join(DATA_DIR, "grades.txt")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.txt")

SYSTEM_TITLE = "STUDENT INFORMATION SYSTEM"
DELIM = "|"
PASSING_GRADE = 75.0
RESET = "\033[0m"
EMAIL_PATTERN = r"[^@\s]+@[^@\s]+\.[^@\s]+"

BANNER = r"""
  ____ ___ ____
 / ___|_ _/ ___|
 \___ \| |\___ \
  ___) | | ___) |
 |____/___|____/
"""


try:  # box-drawing characters need UTF-8 output
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ----------------------------------------------------------------------
# DISPLAY HELPERS
# ----------------------------------------------------------------------
# Colors only work in a real terminal. Editor "output" panels print the raw
# codes (like [92m) as text, so colors are switched off there automatically.
COLOR_ON = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def c(text, role="main"):
    """Color text using the active theme (plain text if colors are off)."""
    if not COLOR_ON:
        return str(text)
    return f"{color(role)}{text}{RESET}"


def clear():
    if COLOR_ON:
        os.system("cls" if os.name == "nt" else "clear")
    else:
        print("\n" * 3)


def header(title):
    """Print a title inside a double-line box."""
    width = 62
    print(c("╔" + "═" * (width - 2) + "╗"))
    print(c("║") + c(title.center(width - 2), "title") + c("║"))
    print(c("╚" + "═" * (width - 2) + "╝"))
    print()


def info(msg):
    print(c(msg, "accent"))


def error(msg):
    print(c("[!] " + msg, "error"))


def success(msg):
    print(c("[OK] " + msg, "main"))


def pause():
    try:
        input(c("\nPress Enter to continue...", "accent"))
    except EOFError:
        pass


def table(headers, rows, width=None):
    """Print a table with double-line box characters.
    If width is given, the last column stretches so the table fills it."""
    if not rows:
        info("(no records to display)")
        return
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    if width:
        extra = width - (sum(w + 2 for w in widths) + len(widths) + 1)
        if extra > 0:
            widths[-1] += extra

    def border(left, middle, right):
        return left + middle.join("═" * (w + 2) for w in widths) + right

    def row_line(cells, role="main"):
        parts = [f" {str(cell).ljust(widths[i])} " for i, cell in enumerate(cells)]
        return c("║") + c("║", role).join(c(p, role) for p in parts) + c("║")

    print(c(border("╔", "╦", "╗")))
    print(row_line(headers, "accent"))
    print(c(border("╠", "╬", "╣")))
    for row in rows:
        print(row_line(row))
    print(c(border("╚", "╩", "╝")))


# ----------------------------------------------------------------------
# INPUT HELPERS
# ----------------------------------------------------------------------
def clean(text):
    """Remove the file delimiter so records never get corrupted."""
    return text.replace(DELIM, "/").strip()


def ask(prompt, default=None):
    """Ask for non-empty text. If a default is given, Enter keeps it."""
    while True:
        suffix = f" [{default}]" if default is not None else ""
        value = clean(input(c(f"{prompt}{suffix}: ", "accent")))
        if value:
            return value
        if default is not None:
            return default
        error("This field cannot be empty.")


def ask_pattern(prompt, pattern, hint, default=None):
    """Ask until the answer fully matches a regex pattern."""
    while True:
        value = ask(prompt, default)
        if re.fullmatch(pattern, value):
            return value
        error(hint)


def ask_int(prompt, low, high, default=None):
    """Ask for a whole number between low and high."""
    while True:
        raw = ask(prompt, str(default) if default is not None else None)
        try:
            number = int(raw)
        except ValueError:
            error("Please enter a whole number.")
            continue
        if low <= number <= high:
            return number
        error(f"Value must be between {low} and {high}.")


def ask_float(prompt, low, high):
    """Ask for a number (decimals allowed) between low and high."""
    while True:
        raw = ask(prompt)
        try:
            number = float(raw)
        except ValueError:
            error("Please enter a number.")
            continue
        if low <= number <= high:
            return number
        error(f"Value must be between {low} and {high}.")


# ----- input forms drawn as a double-line table ------------------------
FORM_LABEL = 14   # width of the label column
FORM_VALUE = 45   # width of the value column (whole table = 62 wide)


def _form_border(left, middle, right):
    return c(left + "═" * FORM_LABEL + middle + "═" * FORM_VALUE + right)


def _form_row(label, filler=""):
    cell = c(f" {label.ljust(FORM_LABEL - 2)} ", "accent")
    return c("║") + cell + c("║") + filler.ljust(FORM_VALUE)


def _cursor_move(from_line, to_line):
    """Move the cursor up or down between lines of the drawn form."""
    if to_line < from_line:
        sys.stdout.write(f"\033[{from_line - to_line}A")
    elif to_line > from_line:
        sys.stdout.write(f"\033[{to_line - from_line}B")
    sys.stdout.flush()


def form_input(fields, cancel_if_first_blank=False):
    """Draw a complete input form as a double-line table, then let the user
    fill it in row by row.

        values = form_input([("Username", False), ("Password", True)])

    Each field is (label, is_password). Returns the typed values as a list,
    or None if cancel_if_first_blank is True and the first row was empty."""
    count = len(fields)

    if not COLOR_ON:
        # Plain console (no cursor movement): draw each row as it is typed.
        print(_form_border("╔", "╦", "╗"))
        values = []
        for i, (label, secret) in enumerate(fields):
            prefix = _form_row(label).rstrip() + " "
            values.append(ask_password("", prefix) if secret else input(prefix))
            if cancel_if_first_blank and i == 0 and not values[0].strip():
                print(_form_border("╚", "╩", "╝"))
                return None
            print(_form_border("╠", "╬", "╣") if i < count - 1
                  else _form_border("╚", "╩", "╝"))
        return values

    # 1) draw the whole empty table first, so the box is always complete
    print(_form_border("╔", "╦", "╗"))
    for i, (label, _) in enumerate(fields):
        print(_form_row(label) + c("║"))
        print(_form_border("╠", "╬", "╣") if i < count - 1
              else _form_border("╚", "╩", "╝"))
    total = 2 * count + 1          # the cursor is now just below the table
    line = total

    # 2) move into each row and let the user type in the value cell
    values = []
    cancelled = False
    for i, (label, secret) in enumerate(fields):
        row = 1 + 2 * i
        _cursor_move(line, row)
        sys.stdout.write(f"\033[{FORM_LABEL + 4}G")
        sys.stdout.flush()
        value = ask_password("", "") if secret else input()
        values.append(value)
        line = row + 1             # pressing Enter moved the cursor down
        if cancel_if_first_blank and i == 0 and not value.strip():
            cancelled = True
            break

    # 3) leave the cursor below the table
    _cursor_move(line, total)
    return None if cancelled else values


_mask_note_shown = False


def masking_mode():
    """Return 'windows', 'unix', or None if this console can't hide typing."""
    try:
        if os.name == "nt":
            import msvcrt  # noqa: F401
            return "windows" if sys.stdin.isatty() else None
        import termios
        termios.tcgetattr(sys.stdin.fileno())
        return "unix"
    except Exception:
        return None


def mask_note():
    """Tell the user once if this console cannot hide the typed password."""
    global _mask_note_shown
    if masking_mode() is None and not _mask_note_shown:
        info("(This console cannot show asterisks, so typing will be "
             "visible. Run the program in a real terminal.)")
        _mask_note_shown = True


def ask_password(prompt, shown_prompt=None):
    """Ask for a password and show * for every character typed.
    If the console can't read key-by-key (IDLE, some editor panels), it
    falls back to normal typing. shown_prompt replaces the default prompt
    text (used by the form rows)."""
    mask_note()
    if shown_prompt is None:
        shown_prompt = c(f"{prompt}: ", "accent")
    mode = masking_mode()
    if mode is None:
        return input(shown_prompt)

    print(shown_prompt, end="", flush=True)
    chars = []

    def handle(ch):
        """Process one key. Returns True when Enter is pressed."""
        if ch in ("\r", "\n"):
            return True
        if ch == "\x03":                      # Ctrl+C
            raise KeyboardInterrupt
        if ch == "\x04" and not chars:        # Ctrl+D
            raise EOFError
        if ch in ("\x08", "\x7f"):            # Backspace
            if chars:
                chars.pop()
                sys.stdout.write("\b \b")
        elif ch.isprintable():
            chars.append(ch)
            sys.stdout.write("*")
        sys.stdout.flush()
        return False

    if mode == "windows":
        import msvcrt
        while True:
            ch = msvcrt.getwch()
            if ch in ("\x00", "\xe0"):         # arrow/function key: skip it
                msvcrt.getwch()
                continue
            if handle(ch):
                break
    else:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch == "\x1b":                # arrow key: skip the sequence
                    sys.stdin.read(2)
                    continue
                if handle(ch):
                    break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    print()
    return "".join(chars)


def confirm(prompt):
    return ask(prompt + " (y/n)").lower() in ("y", "yes")


def choose(options):
    """Show the options [(key, label)] in a table and return the chosen key."""
    table(["No.", "Menu option"],
          [[f"[{key}]", label] for key, label in options], width=62)
    valid = [key for key, _ in options]
    while True:
        choice = input(c("\n> Choose: ", "accent")).strip()
        if choice in valid:
            return choice
        error("Invalid choice. Try again.")


# ----------------------------------------------------------------------
# FILE HANDLING
# ----------------------------------------------------------------------
def read_records(path):
    """Read a .txt file into a list of field lists. Missing file -> []."""
    records = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if line.strip():
                    records.append(line.split(DELIM))
    except FileNotFoundError:
        return []
    except (OSError, UnicodeDecodeError) as e:
        error(f"Could not read {path}: {e}")
    return records


def write_records(path, records):
    """Overwrite a .txt file with the given records. Returns True on success."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            for rec in records:
                f.write(DELIM.join(str(x) for x in rec) + "\n")
        return True
    except OSError as e:
        error(f"Could not save {path}: {e}")
        return False


def append_record(path, record):
    """Add one record to the end of a .txt file. Returns True on success."""
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(DELIM.join(str(x) for x in record) + "\n")
        return True
    except OSError as e:
        error(f"Could not save to {path}: {e}")
        return False


def ensure_data_files():
    """Create the data folder and empty data files if they don't exist."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        for path in (USERS_FILE, STUDENTS_FILE, SUBJECTS_FILE, GRADES_FILE,
                     SETTINGS_FILE):
            if not os.path.exists(path):
                open(path, "w", encoding="utf-8").close()
    except OSError as e:
        print(f"Cannot create data files: {e}")
        raise SystemExit(1)


def read_users():
    """Return a list of [username, salt, hash, role]."""
    return [u for u in read_records(USERS_FILE) if len(u) == 4]


# ----------------------------------------------------------------------
# PASSWORD HASHING (salted PBKDF2)
# ----------------------------------------------------------------------
def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                 bytes.fromhex(salt), 100_000).hex()
    return salt, digest


def verify_password(password, salt, stored_hash):
    _, digest = hash_password(password, salt)
    return hmac.compare_digest(digest, stored_hash)
