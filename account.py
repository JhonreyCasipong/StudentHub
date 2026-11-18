"""
account.py - the Register and Login screens.

register()  creates a new account. The very first account becomes the
            Administrator, every later one is Staff.
login()     checks the username and password.

Both return (username, role) on success so the program can open the
dashboard right away, or None if the user cancelled or failed.
"""

import re

from common import *


def register():
    """Create a new account. The very first account becomes Administrator."""
    users = read_users()
    message = None

    while True:
        clear()
        header("REGISTER")
        info("  Username: 3-15 letters, numbers, or underscore")
        info("  Password: at least 6 characters")
        info("  Leave the username blank to go back.")
        mask_note()
        if message:
            error(message)
        print()

        values = form_input([("Username", False), ("Password", True),
                             ("Confirm", True)], cancel_if_first_blank=True)
        if values is None:
            return None
        username = clean(values[0])
        password, confirm_password = values[1], values[2]

        if not re.fullmatch(r"[A-Za-z0-9_]{3,15}", username):
            message = "Invalid username format. Try again."
        elif any(u[0].lower() == username.lower() for u in users):
            message = "That username is already taken. Try again."
        elif len(password) < 6:
            message = "Password is too short. Try again."
        elif password != confirm_password:
            message = "Passwords do not match. Try again."
        else:
            break

    role = "Staff" if users else "Administrator"
    salt, password_hash = hash_password(password)
    if append_record(USERS_FILE, [username, salt, password_hash, role]):
        print()
        success(f"Account created! You are registered as {role}.")
        info("Opening your dashboard...")
        pause()
        return username, role
    pause()
    return None


def login():
    """Return (username, role) on success, or None if cancelled/failed."""
    clear()
    header("LOGIN")

    if not read_users():
        error("No accounts yet. Please register first.")
        pause()
        return None

    info("Leave the username blank to go back.")
    mask_note()
    print()

    attempts = 0
    while attempts < 3:
        values = form_input([("Username", False), ("Password", True)],
                            cancel_if_first_blank=True)
        if values is None:
            return None
        username, password = values[0].strip(), values[1]

        for user in read_users():
            if user[0] == username and verify_password(password, user[1], user[2]):
                return user[0], user[3]
        attempts += 1
        error(f"Invalid username or password. ({3 - attempts} attempts left)")
        print()

    error("Too many failed attempts. Returning to the start menu.")
    pause()
    return None
