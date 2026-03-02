from flask import Flask, jsonify, request
from flask_cors import CORS

import db

app = Flask(__name__)
CORS(app)


def _error(message="Not found"):
    # Spec: for simplicity all errors return 404
    return jsonify({"error": message}), 404


def _get_json_body():
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return None
    return data


def _parse_mark(value):
    """
    Accept int or numeric string, return int.
    Enforce 0-100.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        mark = value
    elif isinstance(value, str):
        s = value.strip()
        if s == "":
            return None
        if not s.isdigit() and not (s.startswith("-") and s[1:].isdigit()):
            return None
        try:
            mark = int(s)
        except ValueError:
            return None
    else:
        return None

    if mark < 0 or mark > 100:
        return None
    return mark


@app.route("/students")
def get_students():
    """
    Fetch all students from the database.
    return: Array of student objects
    """
    students = db.get_all_students()
    return jsonify(students), 200


@app.route("/students", methods=["POST"])
def create_student():
    """
    Create a new student.
    body: {name: str, course: str, mark?: int}
    return: created student
    """
    student_data = _get_json_body()
    if student_data is None:
        return _error("Invalid JSON body")

    name = student_data.get("name")
    course = student_data.get("course")
    mark_raw = student_data.get("mark", None)

    if not isinstance(name, str) or name.strip() == "":
        return _error("Missing or invalid name")
    if not isinstance(course, str) or course.strip() == "":
        return _error("Missing or invalid course")

    # mark is optional; if missing, we store 0 (keeps stats simple + consistent)
    if "mark" in student_data:
        mark = _parse_mark(mark_raw)
        if mark is None:
            return _error("Invalid mark")
    else:
        mark = 0

    created = db.insert_student(name.strip(), course.strip(), mark)
    return jsonify(created), 200


@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    """
    Update student details by id.
    body can include: name/course/mark (any subset)
    return: updated student
    """
    student_data = _get_json_body()
    if student_data is None:
        return _error("Invalid JSON body")

    # Ensure exists
    existing = db.get_student_by_id(student_id)
    if existing is None:
        return _error("Student not found")

    name = student_data.get("name", None)
    course = student_data.get("course", None)

    # Allow empty string? We choose: empty string is invalid if provided.
    if name is not None and (not isinstance(name, str) or name.strip() == ""):
        return _error("Invalid name")
    if course is not None and (not isinstance(course, str) or course.strip() == ""):
        return _error("Invalid course")

    mark = None
    if "mark" in student_data:
        mark = _parse_mark(student_data.get("mark"))
        if mark is None:
            return _error("Invalid mark")

    updated = db.update_student(
        student_id,
        name=name.strip() if isinstance(name, str) else None,
        course=course.strip() if isinstance(course, str) else None,
        mark=mark,
    )
    if updated is None:
        return _error("Student not found")
    return jsonify(updated), 200


@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    """
    Delete student by id.
    return: deleted student's id
    """
    deleted = db.delete_student(student_id)
    if deleted is None:
        return _error("Student not found")
    return jsonify(deleted), 200


@app.route("/stats")
def get_stats():
    """
    Return count, average, min, max of all student marks.
    """
    students = db.get_all_students()

    marks = []
    for s in students:
        m = s.get("mark", None)
        if isinstance(m, int):
            marks.append(m)

    # Edge case: no students (or no valid marks) -> return zeros
    if len(marks) == 0:
        return jsonify({"count": 0, "average": 0, "min": 0, "max": 0}), 200

    count = len(marks)
    avg = sum(marks) / count
    return (
        jsonify(
            {
                "count": count,
                "average": avg,
                "min": min(marks),
                "max": max(marks),
            }
        ),
        200,
    )


@app.route("/")
def health():
    """Health check."""
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
