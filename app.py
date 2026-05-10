from flask import Flask, request, render_template, redirect, send_file, session, url_for
import io
import logging
import os
from datetime import date, timedelta

import pandas as pd
from datetime import datetime
from models import Visitor, Admin, connect_db
import requests
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO)

# ---------------- DATABASE ----------------
connect_db()

DEFAULT_ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@gmail.com").strip().lower()
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin@123")

def seed_default_admin():
    admin = Admin.objects(email=DEFAULT_ADMIN_EMAIL).first()

    if not admin:
        Admin(
            email=DEFAULT_ADMIN_EMAIL,
            password_hash=generate_password_hash(DEFAULT_ADMIN_PASSWORD)
        ).save()
        logging.info("Default admin created: %s", DEFAULT_ADMIN_EMAIL)


seed_default_admin()


# ---------------- SAVE TO DB ----------------
def save_to_db(data):
    # data is [student_name, student_number, course_name, parent_name, parent_contact]
    Visitor(
        student_name=data[0],
        student_number=data[1],
        course_name=data[2],
        parent_name=data[3],
        parent_contact=data[4]
    ).save()


# ---------------- CHECK DUPLICATE ----------------
def is_duplicate(phone):
    return Visitor.objects(student_number=phone).first() is not None


# ---------------- GET TOTAL ----------------
def get_total():
    return Visitor.objects.count()


def get_course_stats():
    pipeline = [
        {"$group": {"_id": "$course_name", "count": {"$sum": 1}}}
    ]
    results = Visitor.objects.aggregate(pipeline)
    return [(r["_id"], r["count"]) for r in results]


def get_gauge_stats():
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)
    start_of_today = datetime(now.year, now.month, now.day)

    monthly_visitors = Visitor.objects(created_at__gte=start_of_month).count()
    today_visitors = Visitor.objects(created_at__gte=start_of_today).count()

    return {
        "monthly": monthly_visitors,
        "today": today_visitors,
        "target": 100
    }

def get_weekly_trend():
    now = datetime.utcnow()
    seven_days_ago = datetime(now.year, now.month, now.day) - timedelta(days=6)
    
    pipeline = [
        {"$match": {"created_at": {"$gte": seven_days_ago}}},
        {"$project": {
            "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}
        }},
        {"$group": {"_id": "$date", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    
    results = list(Visitor.objects.aggregate(pipeline))
    db_dict = {r["_id"]: r["count"] for r in results}
    
    today_dt = date.today()
    labels = []
    data = []
    
    for i in range(6, -1, -1):
        d = today_dt - timedelta(days=i)
        labels.append(d.strftime("%a"))
        data.append(db_dict.get(d.strftime('%Y-%m-%d'), 0))
        
    return {"labels": labels, "data": data}


# ---------------- GET ALL VISITORS ----------------
def get_all_visitors(filter_type=None):
    now = datetime.utcnow()
    visitors_query = Visitor.objects
    
    if filter_type == "today":
        start_of_today = datetime(now.year, now.month, now.day)
        visitors_query = visitors_query.filter(created_at__gte=start_of_today)
    elif filter_type == "week":
        seven_days_ago = now - timedelta(days=7)
        visitors_query = visitors_query.filter(created_at__gte=seven_days_ago)

    visitors = visitors_query.order_by('-id')
    
    rows = []
    for v in visitors:
        rows.append((
            str(v.id),
            v.student_name,
            v.student_number,
            v.course_name,
            v.parent_name,
            v.parent_contact,
            v.created_at.strftime("%Y-%m-%d %H:%M:%S") if v.created_at else ""
        ))

    headers = ["ID", "Student Name", "Phone", "Course", "Parent", "Parent Contact", "Date Added"]
    return headers, rows


def verify_admin_login(email, password):
    admin = Admin.objects(email=email.strip().lower()).first()

    if not admin:
        return None

    if check_password_hash(admin.password_hash, password):
        return {"id": str(admin.id), "email": admin.email}

    return None


# ---------------- API CONFIG ----------------
INSTANCE_KEY = os.environ.get("ULTRAMSG_INSTANCE_ID", "instance143653")
TOKEN = os.environ.get("ULTRAMSG_TOKEN")
API_URL = f"https://api.ultramsg.com/{INSTANCE_KEY}/messages/chat"

# ---------------- ADMIN SESSION ----------------
app.secret_key = "super_secret_key_123"


# ---------------- WHATSAPP FUNCTION ----------------
def send_whatsapp_message(phone_number, message):
    if not TOKEN:
        return {"error": "Token not configured"}

    if not phone_number.startswith("+91"):
        phone_number = "+91" + phone_number.lstrip("0")

    payload = {"to": phone_number, "body": message}

    try:
        response = requests.post(f"{API_URL}?token={TOKEN}", json=payload, timeout=10)
        return response.json()
    except Exception as exc:
        return {"error": str(exc)}


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")


# ---------------- VISITOR FORM ----------------
@app.route("/visitor_form")
def visitor_form():
    return render_template("index.html")


# ---------------- SEND MESSAGE ----------------
@app.route("/send_message", methods=["POST"])
def send_message():
    student_name = request.form.get("student_name", "").strip()
    student_number = request.form.get("student_number", "").strip()
    course_name = request.form.get("course_name", "").strip()
    parent_name = request.form.get("parent_name", "").strip()
    parent_contact = request.form.get("parent_contact", "").strip()

    if not all([student_name, student_number, course_name, parent_name, parent_contact]):
        return "All fields are required."

    if not student_number.isdigit() or len(student_number) != 10:
        return "Invalid phone number. Must be 10 digits."

    if is_duplicate(student_number):
        return "This phone number is already registered."

    save_to_db([student_name, student_number, course_name, parent_name, parent_contact])
    logging.info("New visitor added: %s", student_name)

    message = f"""
Hello {student_name},

Welcome to Vikrant Group Of Institutions, Indore.

Thank you for visiting our campus.

Courses: Engineering, Management, Nursing, Pharmacy, Law

Scholarship:
https://www.vitm.edu.in/scholarship.html

Instagram:
https://www.instagram.com/vikrant.indore

Thanks
"""

    result = send_whatsapp_message(student_number, message)

    if "error" in result:
        return f"Saved but message failed: {result['error']}"

    return redirect("/visitor_form?success=1")


# ---------------- BULK MESSAGE ----------------
@app.route("/bulk_message", methods=["GET", "POST"])
def bulk_message():
    if not session.get("admin"):
        return redirect("/login")

    if request.method == "POST":
        message = request.form.get("message")
        manual_input = request.form.get("manual_numbers", "")
        numbers = []

        if manual_input.strip():
            for num in manual_input.replace(",", "\n").split("\n"):
                if num.strip():
                    numbers.append(num.strip())
                    
        # Process uploaded Excel file
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '' and file.filename.endswith('.xlsx'):
                try:
                    df = pd.read_excel(file)
                    # Find a column that looks like phone numbers
                    for col in df.columns:
                        col_str = str(col).lower()
                        if 'phone' in col_str or 'number' in col_str or 'contact' in col_str:
                            for val in df[col].dropna():
                                num_str = str(val).strip()
                                if num_str.endswith('.0'):
                                    num_str = num_str[:-2]
                                if num_str:
                                    numbers.append(num_str)
                            break
                except Exception as e:
                    logging.error(f"Error reading Excel file: {e}")
                    return f"Error reading Excel file: {e}"

        if not numbers:
            return "No numbers found."

        failed = []

        for number in numbers:
            result = send_whatsapp_message(number, message)
            if "error" in result:
                failed.append(number)

        if failed:
            return f"Failed for: {', '.join(failed)}"

        return redirect("/bulk_message?success=1")

    return render_template("bulk_message.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/login")

    total = get_total()
    course_stats = get_course_stats()
    gauge_stats = get_gauge_stats()
    weekly_trend = get_weekly_trend()
    return render_template("dashboard.html", 
                           total=total, 
                           course_stats=course_stats,
                           gauge_stats=gauge_stats,
                           weekly_trend=weekly_trend)


# ---------------- VIEW VISITORS ----------------
@app.route("/view_visitors")
def view_visitors():
    if not session.get("admin"):
        return redirect("/login")

    filter_type = request.args.get("filter")
    headers, rows = get_all_visitors(filter_type)
    return render_template("view.html", headers=headers, rows=rows)


# ---------------- DOWNLOAD FILE ----------------
@app.route("/download")
def download():
    visitors = Visitor.objects.order_by('-id')
    
    rows = []
    for v in visitors:
        rows.append((
            str(v.id),
            v.student_name,
            v.student_number,
            v.course_name,
            v.parent_name,
            v.parent_contact,
            v.created_at.strftime("%Y-%m-%d %H:%M:%S") if v.created_at else ""
        ))

    headers = ["ID", "Student Name", "Phone", "Course", "Parent", "Parent Contact", "Date Added"]

    df = pd.DataFrame(rows, columns=headers)
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(
        output,
        download_name="visitors.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ---------------- DELETE VISITOR FUNCTION ----------------
@app.route("/delete/<id>")
def delete_visitor(id):
    if not session.get("admin"):
        return redirect("/login")

    Visitor.objects(id=id).delete()

    return redirect("/view_visitors")


# ---------------- EDIT VISITOR ----------------
@app.route("/edit/<id>", methods=["GET", "POST"])
def edit_visitor(id):
    if not session.get("admin"):
        return redirect("/login")

    visitor_obj = Visitor.objects(id=id).first()
    if not visitor_obj:
        return "Visitor not found", 404

    if request.method == "POST":
        visitor_obj.update(
            student_name=request.form.get("student_name"),
            student_number=request.form.get("student_number"),
            course_name=request.form.get("course_name"),
            parent_name=request.form.get("parent_name"),
            parent_contact=request.form.get("parent_contact")
        )
        return redirect("/view_visitors")

    # Format for the template which expects a tuple-like row
    visitor = (
        str(visitor_obj.id),
        visitor_obj.student_name,
        visitor_obj.student_number,
        visitor_obj.course_name,
        visitor_obj.parent_name,
        visitor_obj.parent_contact,
        visitor_obj.created_at
    )

    return render_template("edit.html", visitor=visitor)


# ---------------- LOGIN METHOD ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        admin = verify_admin_login(email, password)

        if admin:
            session["admin"] = True
            session["admin_id"] = admin["id"]
            session["admin_email"] = admin["email"]
            return redirect("/dashboard")

        return "Invalid email or password"

    return render_template("login.html")


# ---------------- LOGOUT CONFIG ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- ERROR ----------------
@app.errorhandler(404)
def not_found(e):
    return "<h1>Page Not Found</h1>", 404


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
