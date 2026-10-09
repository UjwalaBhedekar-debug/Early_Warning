from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "studentcare.db"


# ---------------- DATABASE CONNECTION ----------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- CREATE DATABASE ----------------

def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            student_name TEXT NOT NULL,
            class_name TEXT NOT NULL,

            attendance REAL NOT NULL,
            internal_marks REAL NOT NULL,
            assignment_status TEXT NOT NULL,
            previous_marks REAL NOT NULL,

            english_marks REAL NOT NULL,
            maths_marks REAL NOT NULL,
            hindi_marks REAL NOT NULL,
            marathi_marks REAL NOT NULL,
            science_marks REAL NOT NULL,
            history_marks REAL NOT NULL,
            geography_marks REAL NOT NULL,

            risk_score INTEGER NOT NULL,
            risk_level TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------- RISK CALCULATION ----------------

def calculate_risk(attendance, internal_marks, assignment_status):

    score = 0

    # Attendance
    if attendance >= 90:
        score += 0
    elif attendance >= 75:
        score += 1
    else:
        score += 2

    # Internal Marks
    if internal_marks >= 75:
        score += 0
    elif internal_marks >= 50:
        score += 1
    else:
        score += 2

    # Assignment
    if assignment_status == "On Time":
        score += 0
    elif assignment_status == "Late":
        score += 1
    else:
        score += 2

    # Risk Level
    if score <= 1:
        level = "Low"
    elif score <= 3:
        level = "Medium"
    else:
        level = "High"

    return score, level


def get_subject_analysis(student):

    subjects = {
        "English": student["english_marks"],
        "Maths": student["maths_marks"],
        "Hindi": student["hindi_marks"],
        "Marathi": student["marathi_marks"],
        "Science": student["science_marks"],
        "History": student["history_marks"],
        "Geography": student["geography_marks"]
    }

    result = []

    for subject, marks in subjects.items():

        if marks < 50:

            level = "Weak"

            advice = (
                "Revise the basic concepts and practise "
                "questions regularly."
            )

        elif marks < 70:

            level = "Needs Improvement"

            advice = (
                "Increase practice and revision "
                "to improve performance."
            )

        else:

            level = "Good"

            advice = (
                "Good performance. Continue regular "
                "practice and revision."
            )

        result.append({
            "subject": subject,
            "marks": marks,
            "level": level,
            "advice": advice
        })

    return result
def create_analysis_report(student, subject_analysis):

    weak_subjects = []
    improvement_subjects = []
    good_subjects = []

    for item in subject_analysis:

        if item["level"] == "Weak":
            weak_subjects.append(item["subject"])

        elif item["level"] == "Needs Improvement":
            improvement_subjects.append(item["subject"])

        else:
            good_subjects.append(item["subject"])


    report_parts = []


    if weak_subjects:

        weak_names = ", ".join(weak_subjects)

        report_parts.append(
            "The student needs attention in "
            + weak_names
            + ". These subjects have marks below 50%."
        )


    if improvement_subjects:

        improvement_names = ", ".join(improvement_subjects)

        report_parts.append(
            "The student also needs improvement in "
            + improvement_names
            + ". Regular practice and revision can help improve performance."
        )


    if good_subjects:

        good_names = ", ".join(good_subjects)

        report_parts.append(
            "The student is performing well in "
            + good_names
            + "."
        )


    if not report_parts:

        return "No subject performance information is available."


    return " ".join(report_parts)





# ---------------- ADD STUDENT ----------------

@app.route("/add-student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        student_id = request.form["student_id"]
        student_name = request.form["student_name"]
        class_name = request.form["class_name"]

        attendance = float(request.form["attendance"])
        internal_marks = float(request.form["internal_marks"])
        assignment_status = request.form["assignment_status"]
        previous_marks = float(request.form["previous_marks"])

        english_marks = float(request.form["english_marks"])
        maths_marks = float(request.form["maths_marks"])
        hindi_marks = float(request.form["hindi_marks"])
        marathi_marks = float(request.form["marathi_marks"])
        science_marks = float(request.form["science_marks"])
        history_marks = float(request.form["history_marks"])
        geography_marks = float(request.form["geography_marks"])

        risk_score, risk_level = calculate_risk(
            attendance,
            internal_marks,
            assignment_status
        )

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO students (
                student_id,
                student_name,
                class_name,
                attendance,
                internal_marks,
                assignment_status,
                previous_marks,
                english_marks,
                maths_marks,
                hindi_marks,
                marathi_marks,
                science_marks,
                history_marks,
                geography_marks,
                risk_score,
                risk_level
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            student_name,
            class_name,
            attendance,
            internal_marks,
            assignment_status,
            previous_marks,
            english_marks,
            maths_marks,
            hindi_marks,
            marathi_marks,
            science_marks,
            history_marks,
            geography_marks,
            risk_score,
            risk_level
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("students"))

    return render_template("add_student.html")


# ---------------- SHOW ALL STUDENTS ----------------

@app.route("/students")
def students():

    conn = get_db_connection()

    students_data = conn.execute("""
        SELECT * FROM students
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=students_data
    )

@app.route("/result/<int:student_id>")
def result(student_id):

    conn = get_db_connection()

    student = conn.execute(
        """
        SELECT *
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    ).fetchone()

    conn.close()


    if student is None:
        return "Student not found", 404


    subject_analysis = get_subject_analysis(student)


    analysis_report = create_analysis_report(
        student,
        subject_analysis
    )


    weak_subjects = [
        item for item in subject_analysis
        if item["level"] == "Weak"
    ]


    improvement_subjects = [
        item for item in subject_analysis
        if item["level"] == "Needs Improvement"
    ]


    return render_template(
        "result.html",
        student=student,
        subject_analysis=subject_analysis,
        weak_subjects=weak_subjects,
        improvement_subjects=improvement_subjects,
        analysis_report=analysis_report
    )

@app.route("/dashboard")
def dashboard():

    conn = get_db_connection()

    # Get all students
    students_data = conn.execute(
        """
        SELECT *
        FROM students
        ORDER BY id DESC
        """
    ).fetchall()

    # Total students
    total_students = len(students_data)

    # Risk counts
    low_risk = sum(
        1 for student in students_data
        if student["risk_level"] == "Low"
    )

    medium_risk = sum(
        1 for student in students_data
        if student["risk_level"] == "Medium"
    )

    high_risk = sum(
        1 for student in students_data
        if student["risk_level"] == "High"
    )

    # Average attendance
    if total_students > 0:
        average_attendance = round(
            sum(student["attendance"] for student in students_data)
            / total_students,
            1
        )
    else:
        average_attendance = 0

    # Average internal marks
    if total_students > 0:
        average_internal_marks = round(
            sum(student["internal_marks"] for student in students_data)
            / total_students,
            1
        )
    else:
        average_internal_marks = 0

    # Low submission
    low_submission = sum(
        1
        for student in students_data
        if student["assignment_status"] != "On Time"
    )

    # Subject averages
    if total_students > 0:

        english_average = round(
            sum(student["english_marks"] for student in students_data)
            / total_students,
            1
        )

        maths_average = round(
            sum(student["maths_marks"] for student in students_data)
            / total_students,
            1
        )

        hindi_average = round(
            sum(student["hindi_marks"] for student in students_data)
            / total_students,
            1
        )

        marathi_average = round(
            sum(student["marathi_marks"] for student in students_data)
            / total_students,
            1
        )

        science_average = round(
            sum(student["science_marks"] for student in students_data)
            / total_students,
            1
        )

        history_average = round(
            sum(student["history_marks"] for student in students_data)
            / total_students,
            1
        )

        geography_average = round(
            sum(student["geography_marks"] for student in students_data)
            / total_students,
            1
        )

    else:

        english_average = 0
        maths_average = 0
        hindi_average = 0
        marathi_average = 0
        science_average = 0
        history_average = 0
        geography_average = 0

    conn.close()

    return render_template(
        "dashboard.html",

        students=students_data,

        total_students=total_students,

        low_risk=low_risk,

        medium_risk=medium_risk,

        high_risk=high_risk,

        average_attendance=average_attendance,

        average_internal_marks=average_internal_marks,

        low_submission=low_submission,

        english_average=english_average,

        maths_average=maths_average,

        hindi_average=hindi_average,

        marathi_average=marathi_average,

        science_average=science_average,

        history_average=history_average,

        geography_average=geography_average
    )


# ---------------- PERFORMANCE PAGE ----------------

@app.route("/performance")
def performance():

    conn = get_db_connection()

    students_data = conn.execute("""
        SELECT * FROM students
        ORDER BY student_name
    """).fetchall()

    conn.close()

    return render_template(
        "performance.html",
        students=students_data
    )


# ---------------- AT RISK PAGE ----------------

@app.route("/at-risk")
def at_risk():

    conn = get_db_connection()

    students_data = conn.execute("""
        SELECT * FROM students
        WHERE risk_level IN ('Medium', 'High')
        ORDER BY risk_score DESC
    """).fetchall()

    conn.close()

    return render_template(
        "at_risk.html",
        students=students_data
    )


# ---------------- SUPPORT PAGE ----------------

@app.route("/support")
def support():

    conn = get_db_connection()

    students_data = conn.execute("""
        SELECT * FROM students
        WHERE risk_level IN ('Medium', 'High')
        ORDER BY risk_score DESC
    """).fetchall()

    conn.close()

    return render_template(
        "support.html",
        students=students_data
    )

@app.route("/support-overview")
def support_overview():
    return render_template("support_overview.html")


# ---------------- IMPROVE PAGE ----------------

@app.route("/improve")
def improve():

    return render_template("improve.html")



def calculate_edit_risk(attendance, internal_marks, assignment_status):

    score = 0

    # Attendance
    if attendance >= 90:
        score += 0
    elif attendance >= 75:
        score += 1
    else:
        score += 2

    # Internal Marks
    if internal_marks >= 75:
        score += 0
    elif internal_marks >= 50:
        score += 1
    else:
        score += 2

    # Assignment Submission
    if assignment_status == "On Time":
        score += 0
    elif assignment_status == "Late":
        score += 1
    else:
        score += 2

    # Risk Level
    if score <= 1:
        risk_level = "Low"
    elif score <= 3:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return score, risk_level

@app.route("/edit-student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    if student is None:
        conn.close()
        return "Student not found", 404

    if request.method == "POST":

        student_id_value = request.form["student_id"]
        student_name = request.form["student_name"]
        class_name = request.form["class_name"]

        attendance = float(request.form["attendance"])
        internal_marks = float(request.form["internal_marks"])

        assignment_status = request.form["assignment_status"]

        previous_marks = float(request.form["previous_marks"])

        english_marks = float(request.form["english_marks"])
        maths_marks = float(request.form["maths_marks"])
        hindi_marks = float(request.form["hindi_marks"])
        marathi_marks = float(request.form["marathi_marks"])
        science_marks = float(request.form["science_marks"])
        history_marks = float(request.form["history_marks"])
        geography_marks = float(request.form["geography_marks"])

        # Recalculate risk after editing
        risk_score, risk_level = calculate_edit_risk(
            attendance,
            internal_marks,
            assignment_status
        )

        conn.execute(
            """
            UPDATE students
            SET
                student_id = ?,
                student_name = ?,
                class_name = ?,
                attendance = ?,
                internal_marks = ?,
                assignment_status = ?,
                previous_marks = ?,
                english_marks = ?,
                maths_marks = ?,
                hindi_marks = ?,
                marathi_marks = ?,
                science_marks = ?,
                history_marks = ?,
                geography_marks = ?,
                risk_score = ?,
                risk_level = ?
            WHERE id = ?
            """,
            (
                student_id_value,
                student_name,
                class_name,
                attendance,
                internal_marks,
                assignment_status,
                previous_marks,
                english_marks,
                maths_marks,
                hindi_marks,
                marathi_marks,
                science_marks,
                history_marks,
                geography_marks,
                risk_score,
                risk_level,
                student_id
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("students"))

    conn.close()

    return render_template(
        "edit_student.html",
        student=student
    )

@app.route("/delete-student/<int:student_id>", methods=["POST"])
def delete_student(student_id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("students"))

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
