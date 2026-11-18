"""
Student Information System
Start Menu -> Register -> Login -> Home -> Students, Subjects, Grades

Files:
  main.py      start menu, home screen, student/subject/grade records
  account.py   register and login screens
  theme.py     terminal color themes
  common.py    shared settings, display, input, file, and password helpers

Run: python main.py
"""

import os
from datetime import datetime

from common import *
from account import login, register
from theme import (get_text_color, get_theme, load_user_theme, reset_theme,
                   save_user_settings, set_text_color, set_theme,
                   text_color_names, theme_names)


# ----------------------------------------------------------------------
# STUDENT RECORDS
# Record format in students.txt:  id|name|course|year|email
# ----------------------------------------------------------------------
STUDENT_HEADERS = ["ID", "Name", "Course", "Year", "Email"]


def get_students():
    return [s for s in read_records(STUDENTS_FILE) if len(s) == 5]


def find_student(student_id):
    for student in get_students():
        if student[0].upper() == student_id.upper():
            return student
    return None


def add_student():
    header("ADD STUDENT")
    while True:
        student_id = ask_pattern("Student ID (3-15 letters, numbers, dash)",
                                 r"[A-Za-z0-9\-]{3,15}",
                                 "Invalid ID format.").upper()
        if find_student(student_id):
            error("That Student ID already exists.")
        else:
            break
    name = ask("Full name")
    course = ask("Course (e.g. BSIT)").upper()
    year = ask_int("Year level (1-6)", 1, 6)
    email = ask_pattern("Email", EMAIL_PATTERN, "Invalid email format.")

    if append_record(STUDENTS_FILE, [student_id, name, course, year, email]):
        success(f"Student {name} saved.")


def list_students():
    header("ALL STUDENTS")
    info("Sort by: 1=Name  2=ID  3=Course  4=Year level")
    sort_by = ask_int("Sort choice", 1, 4, 1)
    index = {1: 1, 2: 0, 3: 2, 4: 3}[sort_by]
    if sort_by == 4:
        key = lambda s: (int(s[3]), s[1].lower())
    else:
        key = lambda s: s[index].lower()
    students = sorted(get_students(), key=key)
    print()
    table(STUDENT_HEADERS, students)
    info(f"\nTotal students: {len(students)}")


def search_students():
    header("SEARCH STUDENTS")
    term = ask("Search by ID, name, or course").lower()
    matches = [s for s in get_students()
               if term in s[0].lower() or term in s[1].lower()
               or term in s[2].lower()]
    table(STUDENT_HEADERS, matches)
    info(f"\nMatches found: {len(matches)}")


def view_student_profile():
    header("STUDENT PROFILE")
    student = find_student(ask("Student ID"))
    if not student:
        error("Student not found.")
        return

    table(["Field", "Details"],
          [["Student ID", student[0]], ["Name", student[1]],
           ["Course", student[2]], ["Year level", student[3]],
           ["Email", student[4]]], width=62)
    print()

    rows = []
    units = 0
    total = 0.0
    for g in get_grades():
        if g[0].upper() == student[0].upper():
            subject = find_subject(g[1])
            title = subject[1] if subject else "(unknown)"
            unit = int(subject[2]) if subject else 0
            rows.append([g[1], title, unit, g[2], remark(g[2])])
            units += unit
            total += float(g[2])
    info("Subjects and grades:")
    table(["Code", "Subject", "Units", "Grade", "Remark"], rows)
    if rows:
        average = total / len(rows)
        info(f"\nSubjects taken: {len(rows)}   Total units: {units}")
        info(f"General average: {average:.2f}  ->  {remark(average)}")


def filter_students():
    header("FILTER STUDENTS")
    info("Filter by: 1=Course  2=Year level")
    mode = ask_int("Filter choice", 1, 2)
    if mode == 1:
        course = ask("Course (e.g. BSIT)").upper()
        matches = [s for s in get_students() if s[2].upper() == course]
        label = f"course {course}"
    else:
        year = ask_int("Year level (1-6)", 1, 6)
        matches = [s for s in get_students() if int(s[3]) == year]
        label = f"year level {year}"
    print()
    table(STUDENT_HEADERS, sorted(matches, key=lambda s: s[1].lower()))
    info(f"\nStudents in {label}: {len(matches)}")


def update_student():
    header("UPDATE STUDENT")
    student = find_student(ask("Student ID to update"))
    if not student:
        error("Student not found.")
        return

    info("Press Enter to keep the current value.\n")
    student[1] = ask("Full name", student[1])
    student[2] = ask("Course", student[2]).upper()
    student[3] = ask_int("Year level (1-6)", 1, 6, int(student[3]))
    student[4] = ask_pattern("Email", EMAIL_PATTERN,
                             "Invalid email format.", student[4])

    updated = [student if s[0].upper() == student[0].upper() else s
               for s in get_students()]
    if write_records(STUDENTS_FILE, updated):
        success("Student updated.")


def delete_student():
    header("DELETE STUDENT")
    student = find_student(ask("Student ID to delete"))
    if not student:
        error("Student not found.")
        return
    if not confirm(f"Delete {student[1]} and all their grades?"):
        info("Cancelled.")
        return
    remaining = [s for s in get_students() if s[0].upper() != student[0].upper()]
    if write_records(STUDENTS_FILE, remaining):
        remove_grades(student_id=student[0])
        success("Student and related grades deleted.")


def students_menu(role):
    while True:
        clear()
        header("STUDENT RECORDS")
        options = [("1", "Add student"), ("2", "List students"),
                   ("3", "Search students"), ("4", "View student profile"),
                   ("5", "Filter by course or year level"),
                   ("6", "Update student")]
        if role == "Administrator":
            options.append(("7", "Delete student (admin only)"))
        options.append(("0", "Back to main menu"))
        choice = choose(options)
        if choice == "0":
            return
        clear()
        actions = {"1": add_student, "2": list_students,
                   "3": search_students, "4": view_student_profile,
                   "5": filter_students, "6": update_student,
                   "7": delete_student}
        actions[choice]()
        pause()


# ----------------------------------------------------------------------
# SUBJECT RECORDS
# Record format in subjects.txt:  code|title|units
# ----------------------------------------------------------------------
SUBJECT_HEADERS = ["Code", "Title", "Units"]


def get_subjects():
    return [s for s in read_records(SUBJECTS_FILE) if len(s) == 3]


def find_subject(code):
    for subject in get_subjects():
        if subject[0].upper() == code.upper():
            return subject
    return None


def add_subject():
    header("ADD SUBJECT")
    while True:
        code = ask_pattern("Subject code (2-10 letters, numbers, dash)",
                           r"[A-Za-z0-9\-]{2,10}",
                           "Invalid code format.").upper()
        if find_subject(code):
            error("That subject code already exists.")
        else:
            break
    title = ask("Subject title")
    units = ask_int("Units (1-6)", 1, 6)

    if append_record(SUBJECTS_FILE, [code, title, units]):
        success(f"Subject {code} saved.")


def list_subjects():
    header("ALL SUBJECTS")
    subjects = sorted(get_subjects(), key=lambda s: s[0])
    table(SUBJECT_HEADERS, subjects)
    info(f"\nTotal subjects: {len(subjects)}")


def search_subjects():
    header("SEARCH SUBJECTS")
    term = ask("Search by code or title").lower()
    matches = [s for s in get_subjects()
               if term in s[0].lower() or term in s[1].lower()]
    table(SUBJECT_HEADERS, matches)
    info(f"\nMatches found: {len(matches)}")


def update_subject():
    header("UPDATE SUBJECT")
    subject = find_subject(ask("Subject code to update"))
    if not subject:
        error("Subject not found.")
        return

    info("Press Enter to keep the current value.\n")
    subject[1] = ask("Subject title", subject[1])
    subject[2] = ask_int("Units (1-6)", 1, 6, int(subject[2]))

    updated = [subject if s[0].upper() == subject[0].upper() else s
               for s in get_subjects()]
    if write_records(SUBJECTS_FILE, updated):
        success("Subject updated.")


def delete_subject():
    header("DELETE SUBJECT")
    subject = find_subject(ask("Subject code to delete"))
    if not subject:
        error("Subject not found.")
        return
    if not confirm(f"Delete {subject[0]} - {subject[1]} and all its grades?"):
        info("Cancelled.")
        return
    remaining = [s for s in get_subjects() if s[0].upper() != subject[0].upper()]
    if write_records(SUBJECTS_FILE, remaining):
        remove_grades(subject_code=subject[0])
        success("Subject and related grades deleted.")


def subjects_menu(role):
    while True:
        clear()
        header("SUBJECT RECORDS")
        options = [("1", "Add subject"), ("2", "List subjects"),
                   ("3", "Search subjects"), ("4", "Update subject")]
        if role == "Administrator":
            options.append(("5", "Delete subject (admin only)"))
        options.append(("0", "Back to main menu"))
        choice = choose(options)
        if choice == "0":
            return
        clear()
        actions = {"1": add_subject, "2": list_subjects,
                   "3": search_subjects, "4": update_subject,
                   "5": delete_subject}
        actions[choice]()
        pause()


# ----------------------------------------------------------------------
# GRADE RECORDS
# Record format in grades.txt:  student_id|subject_code|grade
# Grades are 0-100. PASSING_GRADE (75) or higher is PASSED.
# ----------------------------------------------------------------------
def get_grades():
    return [g for g in read_records(GRADES_FILE) if len(g) == 3]


def remove_grades(student_id=None, subject_code=None):
    """Delete grade records that belong to a deleted student or subject."""
    kept = []
    for g in get_grades():
        if student_id and g[0].upper() == student_id.upper():
            continue
        if subject_code and g[1].upper() == subject_code.upper():
            continue
        kept.append(g)
    write_records(GRADES_FILE, kept)


def remark(grade):
    return "PASSED" if float(grade) >= PASSING_GRADE else "FAILED"


def record_grade():
    header("RECORD / UPDATE GRADE")
    student = find_student(ask("Student ID"))
    if not student:
        error("Student not found. Add the student first.")
        return
    subject = find_subject(ask("Subject code"))
    if not subject:
        error("Subject not found. Add the subject first.")
        return

    grade = ask_float(f"Grade for {student[1]} in {subject[0]} (0-100)", 0, 100)
    grades = get_grades()
    for g in grades:
        if g[0].upper() == student[0].upper() and g[1].upper() == subject[0].upper():
            g[2] = f"{grade:.2f}"
            if write_records(GRADES_FILE, grades):
                success("Existing grade updated.")
            return
    if append_record(GRADES_FILE, [student[0], subject[0], f"{grade:.2f}"]):
        success("Grade recorded.")


def view_student_grades():
    header("STUDENT GRADE SHEET")
    student = find_student(ask("Student ID"))
    if not student:
        error("Student not found.")
        return

    table(["Student", "Course and year"],
          [[f"{student[1]} ({student[0]})", f"{student[2]} - Year {student[3]}"]])
    print()
    rows = []
    total = 0.0
    for g in get_grades():
        if g[0].upper() == student[0].upper():
            subject = find_subject(g[1])
            title = subject[1] if subject else "(unknown)"
            rows.append([g[1], title, g[2], remark(g[2])])
            total += float(g[2])
    table(["Code", "Subject", "Grade", "Remark"], rows)
    if rows:
        average = total / len(rows)
        info(f"\nGeneral average: {average:.2f}  ->  {remark(average)}")


def view_subject_grades():
    header("SUBJECT GRADE LIST")
    subject = find_subject(ask("Subject code"))
    if not subject:
        error("Subject not found.")
        return

    table(["Code", "Subject", "Units"], [[subject[0], subject[1], subject[2]]])
    print()
    rows = []
    total = 0.0
    for g in get_grades():
        if g[1].upper() == subject[0].upper():
            student = find_student(g[0])
            name = student[1] if student else "(unknown)"
            rows.append([g[0], name, g[2], remark(g[2])])
            total += float(g[2])
    table(["Student ID", "Name", "Grade", "Remark"], rows)
    if rows:
        info(f"\nClass average: {total / len(rows):.2f}")


def delete_grade():
    header("DELETE GRADE")
    student_id = ask("Student ID")
    code = ask("Subject code")
    grades = get_grades()
    kept = [g for g in grades
            if not (g[0].upper() == student_id.upper()
                    and g[1].upper() == code.upper())]
    if len(kept) == len(grades):
        error("No matching grade record found.")
        return
    if not confirm("Delete this grade?"):
        info("Cancelled.")
        return
    if write_records(GRADES_FILE, kept):
        success("Grade deleted.")


def grades_menu(role):
    while True:
        clear()
        header("GRADE RECORDS")
        options = [("1", "Record / update a grade"),
                   ("2", "View a student's grade sheet"),
                   ("3", "View grades by subject")]
        if role == "Administrator":
            options.append(("4", "Delete a grade (admin only)"))
        options.append(("0", "Back to main menu"))
        choice = choose(options)
        if choice == "0":
            return
        clear()
        actions = {"1": record_grade, "2": view_student_grades,
                   "3": view_subject_grades, "4": delete_grade}
        actions[choice]()
        pause()


# ----------------------------------------------------------------------
# SYSTEM SETTINGS
# ----------------------------------------------------------------------
def change_theme(username):
    header("CHANGE TERMINAL THEME")
    names = theme_names()
    rows = [[f"[{i}]", name, "<- active" if name == get_theme() else ""]
            for i, name in enumerate(names, 1)]
    table(["No.", "Theme", "Status"], rows, width=62)
    print()
    pick = ask_int("Pick a theme number", 1, len(names))
    set_theme(names[pick - 1])
    print()
    if save_user_settings(username, SETTINGS_FILE):
        success(f"Theme changed to {get_theme()} and saved.")
    else:
        error("Theme changed for this session only (could not save it).")


def change_text_color(username):
    header("CHANGE TEXT COLOR")
    info("  Changes the color of the normal text and table borders.")
    print()
    names = text_color_names()
    rows = [[f"[{i}]", name, "<- active" if name == get_text_color() else ""]
            for i, name in enumerate(names, 1)]
    table(["No.", "Text color", "Status"], rows, width=62)
    print()
    pick = ask_int("Pick a text color number", 1, len(names))
    set_text_color(names[pick - 1])
    print()
    if save_user_settings(username, SETTINGS_FILE):
        success(f"Text color changed to {get_text_color()} and saved.")
    else:
        error("Text color changed for this session only (could not save it).")


def change_password(username):
    header("CHANGE PASSWORD")
    info("  New password: at least 6 characters")
    mask_note()
    print()
    current, new, confirm_pw = form_input([("Current", True),
                                           ("New password", True),
                                           ("Confirm", True)])
    users = read_users()
    me = next((u for u in users if u[0] == username), None)
    if not me:
        error("User record not found.")
    elif not verify_password(current, me[1], me[2]):
        error("Current password is incorrect.")
    elif len(new) < 6:
        error("New password is too short.")
    elif new != confirm_pw:
        error("New passwords do not match.")
    else:
        me[1], me[2] = hash_password(new)
        if write_records(USERS_FILE, users):
            success("Password updated.")


def settings_menu(username, role):
    while True:
        clear()
        header("SYSTEM SETTINGS")
        options = [("1", "Change terminal theme"), ("2", "Change my password")]
        if role == "Administrator":
            options.append(("3", "Change text color (admin only)"))
        options.append(("0", "Back to main menu"))
        choice = choose(options)
        if choice == "0":
            return
        clear()
        if choice == "1":
            change_theme(username)
        elif choice == "2":
            change_password(username)
        else:
            change_text_color(username)
        pause()


# ----------------------------------------------------------------------
# DASHBOARD (shown after login or register)
# ----------------------------------------------------------------------
def class_average(grades):
    """Average of every recorded grade, or None if there are no grades."""
    if not grades:
        return None
    return sum(float(g[2]) for g in grades) / len(grades)


def show_dashboard_info(username, role):
    """Print the welcome area, system overview, and recent students."""
    now = datetime.now()
    students, subjects, grades = get_students(), get_subjects(), get_grades()
    average = class_average(grades)

    info(f"  Welcome, {username}!")
    table(["User", "Role", "Date", "Time"],
          [[username, role, f"{now:%b %d, %Y}", f"{now:%I:%M %p}"]], width=62)
    print()

    info("  SYSTEM OVERVIEW")
    table(["Students", "Subjects", "Grades", "Class average"],
          [[len(students), len(subjects), len(grades),
            f"{average:.2f}" if average is not None else "-"]])

    info("\n  RECENT STUDENTS")
    recent = [[s[0], s[1], s[2], s[3]] for s in reversed(students[-5:])]
    table(["ID", "Name", "Course", "Year"], recent)
    if not students:
        info("  Tip: open Student records and add your first student.")
    print()


def home(username, role):
    while True:
        clear()
        print_banner()
        header(SYSTEM_TITLE + " - DASHBOARD")
        show_dashboard_info(username, role)
        info("  MAIN MENU")
        choice = choose([("1", "Student records"), ("2", "Subject records"),
                         ("3", "Grade records"), ("4", "System settings"),
                         ("0", "Logout")])
        if choice == "1":
            students_menu(role)
        elif choice == "2":
            subjects_menu(role)
        elif choice == "3":
            grades_menu(role)
        elif choice == "4":
            settings_menu(username, role)
        else:
            success("Logged out. Goodbye!")
            pause()
            return


# ----------------------------------------------------------------------
# START MENU
# ----------------------------------------------------------------------
def open_dashboard(session):
    """Load the user's saved theme, show the dashboard, reset on logout."""
    username, role = session
    load_user_theme(username, SETTINGS_FILE)
    home(username, role)
    reset_theme()


def start_menu():
    while True:
        clear()
        print_banner()
        header(SYSTEM_TITLE)
        choice = choose([("1", "Login"), ("2", "Register"), ("0", "Exit")])
        if choice == "1":
            session = login()
            if session:
                open_dashboard(session)
        elif choice == "2":
            session = register()
            if session:
                open_dashboard(session)
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
