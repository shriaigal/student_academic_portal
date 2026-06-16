# 📘 Student Attendance Management System (SAP).

A full-featured Flask-based web application designed to digitize and streamline attendance tracking, student performance management, and academic administration.

---

## 🚀 Overview

The **Student Attendance Management System (SAP)** eliminates manual attendance processes and provides a centralized platform where:

- Students can track attendance and marks
- Admins can manage records efficiently
- Attendance is recorded using QR technology
- Data updates dynamically without page reloads

---

## ✨ Key Features

### 🔐 Authentication & Security
- Secure login/logout using Flask-Login
- Session-based authentication
- Role-based access (Admin / Student)
- Password protection & validation

### 📷 QR Code Attendance System
- Unique QR code generation for students
- Fast and contactless attendance marking
- Reduces proxy and manual errors
- Real-time attendance logging

### 📊 Student Dashboard
- View attendance percentage
- Access marks and subject-wise performance
- Interactive charts using Chart.js
- Personalized data display

### 🧑‍💼 Admin Panel
- Add/manage students and users
- Upload/update marks
- View attendance reports
- Monitor system activities
- Manage academic records

### ⚡ Real-Time Updates (AJAX)
- Dynamic data fetching
- No page reload required
- Smooth user experience

### 📧 Email Notification System
- Integrated Flask-Mail
- Feedback submission via email
- Alerts for important updates

### 📁 File Upload & Preview System
- Upload images, audio, and documents
- Preview before download
- Multi-quality download options

### 🎨 Modern UI/UX
- Dark-themed responsive design
- Clean dashboard layout
- Mobile-friendly interface

---

## 🛠️ Tech Stack

| Layer       | Technology Used |
|------------|----------------|
| Backend    | Python (Flask) |
| Database   | SQLite |
| Frontend   | HTML, CSS, JavaScript |
| Libraries  | Flask-Login, Flask-Mail |
| UI Enhancer| Chart.js, AJAX |

---

## 📂 Project Structure


SAP/
│── app.py
│── config.py
│── requirements.txt
│── instance/
│ └── ams.db
│── models/
│── routes/
│── utils/
│── static/
│── templates/
│── services/
│── tests/
│── .env
│── README.md


---

## ⚙️ Installation Guide

### 1️⃣ Clone Repository
```bash
git clone https://github.com/your-username/SAP.git
cd SAP
2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Configure Environment Variables

Create a .env file:

SECRET_KEY=your_secret_key
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
5️⃣ Run Application
python app.py
6️⃣ Open in Browser
http://127.0.0.1:5000/
🔑 Default Credentials (Change After Setup)
Admin Username: admin
Password: admin@123
📊 Database Schema (Overview)
👤 User Table
id
name
email
password
role
📅 Attendance Table
id
user_id
date
status
📝 Marks Table
id
user_id
subject
marks
🔌 API & AJAX Endpoints
/api/attendance → Fetch attendance
/api/marks → Fetch marks
/api/update → Real-time updates
🔒 Security Best Practices
Use environment variables for secrets
Enable HTTPS in production
Hash passwords (Werkzeug security)
Restrict admin routes
📸 Screens (Optional)

Add screenshots for:

Login Page
Dashboard
Attendance Page
Admin Panel
🌟 Future Enhancements
📱 Flutter Mobile App
🔔 Firebase Push Notifications
📊 AI-based performance analytics
☁️ Cloud database (MySQL/PostgreSQL)
🧠 Face Recognition Attendance
🧪 Testing
pytest
🤝 Contribution
Fork the repository
Create a new branch
Commit changes
Submit a Pull Request
👨‍💻 Developer

A S Shridatta Aigal
MCA Student | Full Stack Developer

📜 License

This project is developed for academic and learning purposes. Free to use and modify.

💡 Final Note

This project demonstrates:

Full-stack development
Real-time web applications
Clean architecture
Practical problem solving
