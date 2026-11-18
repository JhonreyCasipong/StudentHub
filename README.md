# Student Information System

A terminal-based management system built with **Python 3** and **plain `.txt` files** for storage.
It runs entirely in the command line, with menu navigation, double-line box tables, colors, and
secure (salted and hashed) passwords.

> Final Laboratory Project | Python Programming and File Handling

---

## Features

**Accounts and security**
- Register and login with two roles: **Administrator** and **Staff**
- The first account registered becomes the Administrator; every later account is Staff
- Passwords are stored as a salted PBKDF2-HMAC-SHA256 hash, never as plain text
- Passwords show as `*****` while typing
- Staff accounts cannot delete records

**Dashboard**
- Opens right after login or registration
- Shows the system title, logged-in user and role, date and time
- System overview: number of students, subjects, grades, and the class average
- Recent students table and an organized main menu

**Student records** (`students.txt`)
- Add, list, search, update, and delete students
- View a full student profile with subjects, grades, units, and general average
- Filter by course or year level, and sort the list by name, ID, course, or year level

**Subject records** (`subjects.txt`)
- Add, list, search, update, and delete subjects

**Grade records** (`grades.txt`)
- Record or update a grade (0-100) for a student in a subject
- View a student's grade sheet with PASSED or FAILED remarks and the general average
- View all grades for a subject with the class average
- Deleting a student or a subject also removes their related grades

**Terminal design and themes**
- Double-line box tables for menus, lists, details, and the login and register forms
- 4 selectable color themes: Classic Green, Ocean Blue, Amber Retro, and Royal Purple
- Administrators can also change the text color to Blue, White, or Red
- Each user's theme and text color are saved and come back at the next login
- Colors switch off automatically in consoles that cannot show them

**System settings**
- Change the terminal theme
- Change your own password
- Change the text color (Administrator only)
- Return to the main menu

**File handling and validation**
- All data is saved to `.txt` files and loaded again when the program restarts
- Handles missing files, invalid inputs, duplicate IDs, and file errors without crashing

### Planned next
- Reports and summaries (class ranking, subject performance, students per course)

---

## Requirements

- Python 3.8 or newer
- No extra libraries needed (uses only the Python standard library)
- A real terminal is recommended (Termux, Command Prompt, PowerShell, macOS Terminal, Linux Terminal,
  or the terminal inside VS Code)

---

## Installation

1. Download or clone the project:
   ```
   git clone <your-repository-url>
   cd <your-project-folder>
   ```
2. Make sure these four files are in the same folder:
   ```
   main.py
   account.py
   theme.py
   common.py
   ```

**On Termux (Android)**
```
pkg install python git
```

---

## How to run

```
python main.py
```

On some systems, use `python3 main.py` instead.

1. Choose **Register** and create the first account. It becomes the Administrator and opens the
   dashboard right away.
2. Next time, choose **Login** with your username and password.
3. Use the dashboard menu to open Student, Subject, or Grade records.

The `data/` folder and its `.txt` files are created automatically on the first run.

---

## Project structure

```
project-folder/
├── main.py        # start menu, dashboard, student / subject / grade records
├── account.py     # register and login screens
├── theme.py       # terminal color themes
├── common.py      # shared settings, display, input, file, and password helpers
├── README.md
└── data/          # created automatically
    ├── users.txt
    ├── students.txt
    ├── subjects.txt
    ├── grades.txt
    └── settings.txt
```

---

## Data files

Each record is one line, with fields separated by `|`.

| File           | Format                                  | Example                                   |
|----------------|-----------------------------------------|-------------------------------------------|
| `users.txt`    | `username\|salt\|password_hash\|role`   | `admin\|9f2c...\|a41b...\|Administrator`  |
| `students.txt` | `id\|name\|course\|year\|email`         | `S-001\|Juan Cruz\|BSIT\|2\|juan@mail.com`|
| `subjects.txt` | `code\|title\|units`                    | `IT101\|Intro Programming\|3`             |
| `grades.txt`   | `student_id\|subject_code\|grade`       | `S-001\|IT101\|88.00`                     |
| `settings.txt` | `username\|theme\|text_color`           | `admin\|Ocean Blue\|Red`                  |

**Grading:** grades are from 0 to 100. A grade of **75 or higher** is PASSED, and anything below is
FAILED. You can change `PASSING_GRADE` in `common.py`.

---

## Roles and permissions

| Action                                         | Administrator | Staff |
|------------------------------------------------|:-------------:|:-----:|
| Add, list, search, view, filter, update records |      Yes      |  Yes  |
| Record and view grades                         |      Yes      |  Yes  |
| Change own theme and password                  |      Yes      |  Yes  |
| Change text color (Blue, White, Red)           |      Yes      |  No   |
| Delete students, subjects, and grades          |      Yes      |  No   |

---

## Troubleshooting

| Problem                                   | Fix                                                                  |
|-------------------------------------------|----------------------------------------------------------------------|
| `ModuleNotFoundError: No module named 'common'` | One of the four `.py` files is missing. Keep them in the same folder and run from that folder. |
| Weird codes like `[92m` on screen         | You are running in an editor panel. Run in a real terminal instead.   |
| Passwords are visible while typing        | Same cause. A real terminal shows `*****`.                           |
| Boxes look like `?` or garbled symbols    | Use a terminal font that supports box-drawing characters.            |
| Registered as Staff but you need Admin    | Delete `data/users.txt` and register again. Other data is kept.      |
| Forgot your password                      | Delete `data/users.txt` and register again. Other data is kept.      |

---

## Screenshots

Add your screenshots to a `screenshots/` folder and link them here:

- Login: `screenshots/login.png`
- Dashboard: `screenshots/dashboard.png`
- File operations (students, subjects, grades): `screenshots/file-operations.png`
- Reports: `screenshots/reports.png`
- Theme customization: `screenshots/themes.png`

---

## Author

**[Your Name]**
