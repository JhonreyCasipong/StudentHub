print("hello")

"""
Student Information System
Step 1: Start Menu -> Register -> Login -> Home

Run: python main.py
"""

import getpass
import hashlib
import hmac
import os
import re
import secrets
from datetime import datetime

# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.txt")

SYSTEM_TITLE = "STUDENT INFORMATION SYSTEM"
DELIM = "|"
RESET = "\033[0m"

THEMES = {
    "Classic Green": {"main": "\033[92m", "accent": "\033[93m",
                      "error": "\033[91m", "head": "\033[30;42m"},
    "Ocean Blue":    {"main": "\033[96m", "accent": "\033[97m",
                      "error": "\033[91m", "head": "\033[30;46m"},
}
current_theme = "Classic Green"

BANNER = r"""
  ____ ___ ____
 / ___|_ _/ ___|
 \___ \| |\___ \
  ___) | | ___) |
 |____/___|____/
"""


# ----------------------------------------------------------------------
# DISPLAY HELPERS
# ----------------------------------------------------------------------
def c(text, role="main"):
    """Color text using the active theme."""
    return f"{THEMES[current_theme][role]}{text}{RESET}"


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def header(title):
    print(THEMES[current_theme]["head"] + f" {title} ".center(62) + RESET)
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


# ----------------------------------------------------------------------
# INPUT HELPERS
# ----------------------------------------------------------------------
def clean(text):
    """Remove the file delimiter so records never get corrupted."""
    return text.replace(DELIM, "/").strip()


def ask(prompt):
    """Ask for non-empty text."""
    while True:
        value = clean(input(c(f"{prompt}: ", "accent")))
        if value:
            return value
        error("This field cannot be empty.")


def ask_password(prompt):
    """Ask for a password without showing it (falls back to normal input)."""
    try:
        return getpass.getpass(c(f"{prompt}: ", "accent"))
    except (EOFError, KeyboardInterrupt):
        raise
    except Exception:
        return input(c(f"{prompt}: ", "accent"))


def choose(options):
    """Show numbered options [(key, label)] and return the chosen key."""
    for key, label in options:
        print(c(f"  [{key}] ", "accent") + c(label))
    valid = [key for key, _ in options]
    while True:
        choice = input(c("\n> Choose: ", "accent")).strip()
        if choice in valid:
            return choice
        error("Invalid choice. Try again.")


# ----------------------------------------------------------------------
# FILE HANDLING
# ----------------------------------------------------------------------
def ensure_data_files():
    """Create the data folder and users file if they don't exist yet."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(USERS_FILE):
            open(USERS_FILE, "w", encoding="utf-8").close()
    except OSError as e:
        print(f"Cannot create data files: {e}")
        raise SystemExit(1)


def read_users():
    """Return a list of [username, salt, hash, role]. Missing file -> []."""
    users = []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.rstrip("\n").split(DELIM)
                if len(parts) == 4:
                    users.append(parts)
    except FileNotFoundError:
        return []
    except (OSError, UnicodeDecodeError) as e:
        error(f"Could not read users file: {e}")
    return users


def save_user(username, salt, password_hash, role):
    """Append one user to users.txt. Returns True on success."""
    try:
        with open(USERS_FILE, "a", encoding="utf-8") as f:
            f.write(DELIM.join([username, salt, password_hash, role]) + "\n")
        return True
    except OSError as e:
        error(f"Could not save user: {e}")
        return False


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


# ----------------------------------------------------------------------
# REGISTER
# ----------------------------------------------------------------------
def register():
    """Create a new account. The very first account becomes Administrator."""
    clear()
    header("REGISTER")
    users = read_users()

    while True:
        username = ask("Username (3-15 letters, numbers, underscore)")
        if not re.fullmatch(r"[A-Za-z0-9_]{3,15}", username):
            error("Invalid username format.")
        elif any(u[0].lower() == username.lower() for u in users):
            error("That username is already taken.")
        else:
            break

    while True:
        password = ask_password("Password (min 6 characters)")
        if len(password) < 6:
            error("Password is too short.")
            continue
        if password != ask_password("Confirm password"):
            error("Passwords do not match.")
            continue
        break

    role = "Staff" if users else "Administrator"
    salt, password_hash = hash_password(password)
    if save_user(username, salt, password_hash, role):
        success(f"Account created! You are registered as {role}.")
        info("You can now log in from the start menu.")
    pause()


# ----------------------------------------------------------------------
# LOGIN
# ----------------------------------------------------------------------
def login():
    """Return (username, role) on success, or None if cancelled/failed."""
    clear()
    header("LOGIN")

    if not read_users():
        error("No accounts yet. Please register first.")
        pause()
        return None

    info("Leave the username blank to go back.\n")
    attempts = 0
    while attempts < 3:
        username = input(c("Username: ", "accent")).strip()
        if not username:
            return None
        password = ask_password("Password")
        for user in read_users():
            if user[0] == username and verify_password(password, user[1], user[2]):
                return user[0], user[3]
        attempts += 1
        error(f"Invalid username or password. ({3 - attempts} attempts left)")

    error("Too many failed attempts. Returning to the start menu.")
    pause()
    return None


# ----------------------------------------------------------------------
# HOME (dashboard)
# ----------------------------------------------------------------------
def home(username, role):
    while True:
        clear()
        print(c(BANNER))
        header(SYSTEM_TITLE)
        now = datetime.now()
        print(c(f"  Welcome, {username}! ", "accent") + c(f"[{role}]"))
        print(c(f"  Date: {now:%A, %B %d, %Y}   Time: {now:%I:%M %p}\n"))
        info("  More features are coming in the next steps.\n")
        choice = choose([("0", "Logout")])
        if choice == "0":
            success("Logged out. Goodbye!")
            pause()
            return


# ----------------------------------------------------------------------
# START MENU
# ----------------------------------------------------------------------
def start_menu():
    while True:
        clear()
        print(c(BANNER))
        header(SYSTEM_TITLE)
        choice = choose([("1", "Login"), ("2", "Register"), ("0", "Exit")])
        if choice == "1":
            session = login()
            if session:
                home(*session)
        elif choice == "2":
            register()
        else:
            return


def main():
    os.system("")  # enables ANSI colors on Windows terminals
    ensure_data_files()
    try:
        start_menu()
    except (KeyboardInterrupt, EOFError):
        pass
    print("\nProgram closed. Goodbye!")


if __name__ == "__main__":
    main()


