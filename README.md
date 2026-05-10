# 🚀 Visitor Management System

A full-stack web application to manage visitor records, send WhatsApp messages, and analyze visitor data using a modern dashboard.

---

## 📌 Features

* ✅ Add Visitor with complete details
* ✅ Send WhatsApp message automatically
* ✅ Bulk WhatsApp messaging
* ✅ View all visitor records
* ✅ Edit and Delete visitors (CRUD operations)
* ✅ Search by Name
* ✅ Filter by Course (Dropdown)
* ✅ Date Filter (Today / This Week)
* ✅ Download visitor data as Excel
* ✅ Responsive UI (Mobile + Desktop)
* ✅ PostgreSQL database (persistent storage)

---

## 🛠 Tech Stack

### 🔹 Frontend

* HTML5
* CSS3
* Bootstrap 5
* JavaScript

### 🔹 Backend

* Python
* Flask

### 🔹 Database

* PostgreSQL (Render)

### 🔹 API

* UltraMsg WhatsApp API

### 🔹 Deployment

* Render

---

## 📂 Project Structure

```
project/
│
├── app.py
├── requirements.txt
│
├── templates/
│   ├── home.html
│   ├── index.html
│   ├── dashboard.html
│   ├── view.html
│   ├── bulk_message.html
│   └── edit.html
│
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository

```bash
git clone https://github.com/Ankit13github/Visitor_Management_System.git
cd Visitor_Management_System
```

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Set Environment Variables

Create environment variables:

```
DATABASE_URL = your_postgresql_url
TOKEN = your_ultramsg_token
```

---

### 4️⃣ Run Application

```bash
python app.py
```

Open:

```
http://127.0.0.1:10000
```

---

## 🌐 Deployment (Render)

1. Push code to GitHub
2. Create Web Service on Render
3. Add environment variables
4. Add PostgreSQL database
5. Connect using `DATABASE_URL`
6. Deploy

---

## 📊 Features Breakdown

### 🔹 Visitor Form

* Add visitor details
* Validate input
* Prevent duplicates

### 🔹 Dashboard

* Shows total number of visitors

### 🔹 Visitor Records

* Table view of all visitors
* Edit & Delete functionality
* Search and filter

### 🔹 Filters

* 🔍 Search by name
* 🎓 Filter by course
* 📅 Filter by date (Today / Week)

### 🔹 Download

* Export visitor data to Excel

---

## 🧠 Database Schema

```sql
CREATE TABLE visitors (
    id SERIAL PRIMARY KEY,
    student_name TEXT,
    student_number TEXT,
    course_name TEXT,
    parent_name TEXT,
    parent_contact TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📱 Mobile Responsiveness

* Responsive layout using Bootstrap
* Optimized for mobile devices
* Clean UI for all screen sizes

---

## ⚠️ Notes

* ID values may have gaps (normal database behavior)
* Data is stored permanently using PostgreSQL
* Excel is used only for download functionality

---

## 🔥 Future Enhancements

* 🔐 Admin Login System
* 📊 Analytics Dashboard (Charts)
* 📅 Advanced Date Filtering
* 🔎 Backend Search (SQL-based)
* 📄 PDF Export
* 📷 Face Recognition Integration

---

## 👨‍💻 Author

**Ankit Malviya**
Final Year CSE Student

---

## ⭐ Acknowledgment

This project is built as part of learning full-stack development and real-world application design.

---

## 📌 License

This project is open-source and available for learning purposes.
