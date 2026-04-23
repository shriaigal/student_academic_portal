from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
import sqlite3
from flask import jsonify
import io
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user    
from werkzeug.utils import secure_filename
from datetime import timedelta
from io import BytesIO
import base64
import datetime  
from datetime import datetime
from flask_mail import Mail, Message
import time
import json



#port: http://127.0.0.1:5000/
#name @admin and password admin@123




app = Flask(__name__, template_folder='/SAP/templates')
app.config['SECRET_KEY'] = '2004'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ams.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'attendancemanagementsystem111@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = "jotw mjlc edrf bkdl"  # Use an App Password if 2FA is enabled
app.config['MAIL_DEFAULT_SENDER'] = 'attendancemanagementsystem111@gmail.com'

mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def init_db():
    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()



def init_db():
    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()

    # Create users table with rollno as the primary key
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        name TEXT NOT NULL,
                        rollno TEXT NOT NULL UNIQUE,
                        regno TEXT NOT NULL,
                        class TEXT NOT NULL,
                        section TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        gmail TEXT NOT NULL,
                        password TEXT NOT NULL,
                        profile_picture BLOB
                    )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            login_time TEXT,
            date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, date) 
        )
    ''')

    #slider
    conn = sqlite3.connect("ams.db")
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS sliders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slider1 BLOB NOT NULL,
            slider2 BLOB NOT NULL,
            slider3 BLOB NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            guest TEXT
        )
    """)
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS timetable (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    image BLOB NOT NULL,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

# Create 'total' table with 'days' column
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS total (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            days INTEGER NOT NULL,
            date TEXT NOT NULL
)
""")



    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INTEGER NOT NULL,
            subject1 TEXT NOT NULL,
            marks1 INTEGER NOT NULL,
            subject2 TEXT NOT NULL,
            marks2 INTEGER NOT NULL,
            subject3 TEXT NOT NULL,
            marks3 INTEGER NOT NULL,
            total_marks INTEGER NOT NULL,
            max_marks INTEGER NOT NULL,
            percentage REAL NOT NULL,
            exam_type TEXT NOT NULL,
            UNIQUE(user_id, exam_type),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        message TEXT NOT NULL)''')
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS late (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rollno TEXT NOT NULL,
            phone TEXT NOT NULL,
            message TEXT NOT NULL,
            date_sent TEXT NOT NULL,  -- Stores the date when the message was sent
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)


    cursor.execute('''CREATE TABLE IF NOT EXISTS faculty (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        profession TEXT NOT NULL,
                        department TEXT NOT NULL,
                        password TEXT NOT NULL)''')


    conn.commit()
    conn.close()


class User(UserMixin):
    def __init__(self, id, name, rollno, regno, class_name, section, phone, gmail, password, profile_picture):
        self.id = id
        self.name = name
        self.rollno = rollno
        self.regno = regno
        self.class_name = class_name
        self.section = section
        self.phone = phone
        self.gmail = gmail
        self.password = password
        self.profile_picture = profile_picture  # Add this attribute for profile picture

    @staticmethod
    def get(user_id):
        conn = sqlite3.connect('ams.db')
        cursor = conn.cursor()
        
        # Ensure you select profile_picture as well
        cursor.execute('SELECT id, name, rollno, regno, class, section, phone, gmail, password, profile_picture FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return User(*user)  # Unpack values correctly
        return None

def get_id(self):
        return str(self.id)

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        name = request.form['name']
        rollno = request.form['rollno']
        regno = request.form['regno']
        class_name = request.form['class']
        section = request.form['section']
        phone = request.form['phone']
        gmail = request.form['gmail']
        password = request.form['password']
        profile_picture = request.files['profile_picture'].read() if 'profile_picture' in request.files else None

        conn = sqlite3.connect('ams.db')
        cursor = conn.cursor()

        try:
            # Insert new user into the database
            cursor.execute("INSERT INTO users (name, rollno, regno, class, section, phone, gmail, password, profile_picture) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (name, rollno, regno, class_name, section, phone, gmail, password, profile_picture))
            conn.commit()
            conn.close()

            # Send welcome email
            send_welcome_email(gmail, name)

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            flash("Roll number already exists. Try another one.", "danger")
            conn.close()
            return redirect("/create_account")

    return render_template('create_account.html')

def send_welcome_email(to_email, name):
    try:
        msg = Message("Welcome to AMS", recipients=[to_email])
        msg.body = f"""
        Hello {name},

        Welcome to the Attendance Management System (AMS)! Your account has been successfully created.

        You can now log in and start using the system.

        Best Regards,
        AMS Team
        """
        mail.send(msg)
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")  

@app.route('/test-email')
def test_email():
    try:
        msg = Message("Flask-Mail Test", recipients=["recipient@gmail.com"])
        msg.body = "This is a test email from Flask-Mail!"
        mail.send(msg)
        return " Test email sent successfully!"
    except Exception as e:
        return f"Error sending email: {e}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        # Check if the user is the admin
        if name == "@admin" and password == "admin@123":
            session['user_id'] = "admin"
            return redirect(url_for('admin'))  # Redirect to the admin page

        conn = sqlite3.connect('ams.db')
        cursor = conn.cursor()

        # Check in 'users' table
        cursor.execute('SELECT * FROM users WHERE name = ?', (name,))
        user = cursor.fetchone()

        if user and user[8] == password:  # Ensure hashed password check
            user_obj = User(*user)
            login_user(user_obj)
            session['user_id'] = user[0]
            conn.close()
            return redirect(url_for('homepage'))  # Redirect normal users to homepage
        
        # Check in 'faculty' table
        cursor.execute('SELECT * FROM faculty WHERE name = ?', (name,))
        faculty = cursor.fetchone()
        conn.close()

        if faculty and faculty[4] == password:  # Ensure hashed password check
            session['user_id'] = faculty[0]
            session['user_role'] = 'faculty'
            return redirect(url_for('faculty_index'))  # Redirect faculty to faculty_index.html

        flash('Invalid username or password', 'error')  # Show error message only on failure
        return redirect(url_for('login'))  # Redirect back to clear form input

    return render_template('login.html')



@app.route('/')
# @login_required
def homepage():
    return render_template('index_new.html', user=current_user)  

# @app.route('/homepage')
# @login_required
# def homepage():
#     return render_template('home page.html', user=current_user)  # Pass user to template

# @app.route('/')
# # @login_required
# def homepage1():
#     return render_template('index.html', user=current_user)  # Pass user to template

@app.route('/dash_data')
@login_required
def dash_data():
    if current_user.is_authenticated:
        user_data = {
            "name": current_user.name,
            "rollno": current_user.rollno,
            "class_name": current_user.class_name,
            "section": current_user.section
        }
        return jsonify(user_data)
    return jsonify({"error": "User not authenticated"}), 401

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/dash')
@login_required
def dashboard():
    return render_template('dash_board.html', user=current_user)

@app.route('/get_qr_data')
@login_required
def get_qr_data():
    if current_user.is_authenticated:
        user_data = {
            "id":current_user.id,
            "name": current_user.name,
            "rollno": current_user.rollno,
            "regno": current_user.regno,
            "class_name": current_user.class_name,
            "section": current_user.section,
            "phone": current_user.phone,
            "gmail": current_user.gmail
        }
        return jsonify(user_data)
    return jsonify({"error": "User not authenticated"}), 401

@app.route('/profile_picture/<int:user_id>')
def profile_picture(user_id):
    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()
    cursor.execute('SELECT profile_picture FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()

    
    
    if row and row[0]:
        return send_file(io.BytesIO(row[0]), mimetype='image/jpeg')
    else:
        return "No Profile Picture", 404

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)  # Ensure this correctly calls the static method

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Log out the user
    flash("You have been logged out successfully.")  # Optional: Flash a message
    return redirect(url_for('login'))  # Redirect to the login page

@app.route('/upload_profile_picture', methods=['POST'])
@login_required
def upload_profile_picture():
    if 'profile_picture' not in request.files:
        return jsonify({"success": False, "message": "No file provided"}), 400
    
    file = request.files['profile_picture']
    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"}), 400

    image_data = file.read()

    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET profile_picture = ? WHERE id = ?", (image_data, current_user.id))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Profile picture updated successfully!",
        "image_url": url_for('profile_picture', user_id=current_user.id)
    })

@app.route('/qr_code')

def qr_code():
    return render_template('qr_code.html')  # Renders the QR Code page

@app.route('/sliderimg')
# @login_required  # Ensure only logged-in users can access this page
def sliderimg():
    return render_template('events_and_news.html')  # Renders the QR Code page

@app.route('/store_qr_data', methods=['POST'])
def store_qr_data():
    data = request.json
    
    try:
        conn = sqlite3.connect('ams.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO admins (user_id, login_time, date)
            VALUES (?, ?, ?)
        ''', (data['id'], data['loginTime'], data['date']))

        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/upload_slider', methods=['GET', 'POST'])
def upload_slider():
    if request.method == 'POST':
        # Validate file input
        if 'slider1' not in request.files or 'slider2' not in request.files or 'slider3' not in request.files:
            flash("All three images are required.", "error")
            return redirect(url_for('sliderimg'))

        slider1 = request.files['slider1']
        slider2 = request.files['slider2']
        slider3 = request.files['slider3']

        if slider1.filename == '' or slider2.filename == '' or slider3.filename == '':
            flash("All three images must be selected.", "error")
            return redirect(url_for('sliderimg'))

        # Read file data as binary (BLOB)
        slider1_blob = slider1.read()
        slider2_blob = slider2.read()
        slider3_blob = slider3.read()

        # Store images in SQLite as BLOB
        conn = sqlite3.connect("ams.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sliders (slider1, slider2, slider3)
            VALUES (?, ?, ?)
        """, (slider1_blob, slider2_blob, slider3_blob))
        conn.commit()
        conn.close()

        flash("Slider images uploaded successfully!", "success")
        return redirect(url_for('admin'))

    return render_template('events_and_news.html')

@app.route('/get_latest_slider/<int:image_number>')
def get_latest_slider(image_number):
    conn = sqlite3.connect("ams.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT slider1, slider2, slider3 FROM sliders ORDER BY id DESC LIMIT 1")  # Fetch latest row
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return "Image not found", 404

    image_data = row[image_number - 1]  # Selects slider1, slider2, or slider3
    return send_file(io.BytesIO(image_data), mimetype="image/jpeg")

# Database connection
def get_db_connection():
    conn = sqlite3.connect("ams.db")  # Using "ams.db"
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/add_news_form', methods=['GET'])
def add_news_form():
    return render_template('news.html')

# Route to handle news submission
@app.route('/add_news', methods=['POST'])
def add_news():
    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        time = request.form['time']
        guest = request.form['guest']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO news (title, date, time, guest) VALUES (?, ?, ?, ?)", 
                           (title, date, time, guest))
            conn.commit()
            flash("News added successfully!", "success")
        except sqlite3.IntegrityError:
            flash("An error occurred. Please try again.", "error")
        finally:
            conn.close()
        
        return redirect(url_for('add_news_form'))  # Redirect back to the form page')

@app.route('/news')
def display_news():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news ORDER BY date DESC, time DESC")  # Fetch all news sorted by date/time
    news_list = cursor.fetchall()
    conn.close()
    return render_template('display_news.html', news_list=news_list)

@app.route('/api/latest_event')
def api_latest_event():
    conn = sqlite3.connect("ams.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM news ORDER BY date DESC, time DESC LIMIT 1")  # Fetch only the latest event
    latest_event = cursor.fetchone()
    conn.close()

    if latest_event:
        return {"event": dict(latest_event)}
    else:
        return {"event": None}  # Return None if no events exist
    
# TOTAL_CLASSES = total_days_value  # Set total classes in a month

def get_login_count(user_id):
    """Fetch the number of times the user has logged in from the admins table."""
    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()

    # Ensure the user_id exists in the database
    cursor.execute('SELECT COUNT(*) FROM admins WHERE user_id = ?', (user_id,))
    login_count = cursor.fetchone()[0] or 0  # Default to 0 if no records

    conn.close()
    return login_count

def get_total_classes():
    """Fetch the total number of classes (sum of all days) from the database."""
    conn = sqlite3.connect("ams.db")
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(days) FROM total")  # Sum all days
    result = cursor.fetchone()

    conn.close()

    return result[0] if result[0] is not None else 0


def get_student_attendance(user_id):
    """Calculate attendance percentage based on login count."""
    attended_classes = get_login_count(user_id)  # Get logins as attended classes
    total_classes = get_total_classes()  # Get total classes from the database
    
    attendance_percentage = (attended_classes / total_classes) * 100 if total_classes > 0 else 0

    return {
        "user_id": user_id,
        "attended": attended_classes,
        "total_classes": total_classes,
        "percentage": f"{attendance_percentage:.2f}%"
    }

def get_student_profile(user_id):
    """Fetch student profile details."""
    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name, rollno, class, section FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "name": user[0],
            "rollno": user[1],
            "class_name": user[2],
            "section": user[3]
        }
    return {"error": "User not found"}

@app.route('/profile_data')  
@login_required  # Ensure only logged-in users access this
def profile_data():
    user_id = current_user.id  # Flask-Login provides the current user
    profile_info = get_student_profile(user_id)
    return jsonify(profile_info)

@app.route('/student_attendance')  
@login_required  # Ensure only logged-in users access this
def student_attendance():
    user_id = current_user.id  
    attendance_info = get_student_attendance(user_id)
    return jsonify(attendance_info)

@app.route('/admin', methods=['GET'])
def admin():
    return render_template('admin_page.html')

@app.before_request
def refresh_session():
    session.modified = True

@app.route('/home', methods=['GET'])
def home():
    return render_template('index_new.html')

@app.route('/chart', methods=['GET'])
def chart():
    return render_template('chart.html')

@app.route('/clgcalendar', methods=['GET'])
def clgcalendar():
    return render_template('clg_calendar.html')

@app.route('/event_newss', methods=['GET'])
def event_newss():
    return render_template('event_news.html')

@app.route('/time_table')
def upload_form():
    return render_template('upload_time_table.html')

@app.route('/about')
def about():
    return render_template('about_of_this_software.html')

@app.route('/feature')
def feature():
    return render_template('feature.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    categories = ["I_BCA_A", "I_BCA_B", "II_BCA_A", "II_BCA_B", "III_BCA_A", "III_BCA_B"]
    
    with sqlite3.connect('ams.db') as conn:
        cursor = conn.cursor()
        
        for category in categories:
            if category in request.files:
                image = request.files[category].read()  # Read the image as binary data
                cursor.execute("INSERT INTO timetable (category, image) VALUES (?, ?)", (category, image))
        
        conn.commit()
    
    return redirect('/faculty_index')

@app.route('/display')
def index():
    return render_template('display_time_table.html')  # Load the HTML page

@app.route('/get_images')
def get_images():
    with sqlite3.connect('ams.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT category, image FROM timetable WHERE id IN (SELECT MAX(id) FROM timetable GROUP BY category)")
        images = cursor.fetchall()

    image_data = {
        category: base64.b64encode(image).decode('utf-8') if image else None
        for category, image in images
    }

    return jsonify(image_data)  # Return JSON data

# 🔹 Global variable to store total days
total_days_value = 0  

# Function to fetch total days from the database and store in a global variable
def update_total_days():
    global total_days_value
    conn = sqlite3.connect("ams.db")
    cursor = conn.cursor()
    cursor.execute("SELECT days FROM total WHERE id = 1")
    row = cursor.fetchone()
    conn.close()

    total_days_value = row[0] if row else 0  # Update global variable
    return total_days_value

# 🔹 Initialize total_days_value before using it
# update_total_days()  

# 🔹 Now you can use the global variable safely
TOTAL_CLASSES = total_days_value
totaldays = total_days_value
  # No NameError
tt=total_days_value

# Route to insert/update days in the 'total' table
@app.route('/add_days', methods=['POST'])
def add_days():
    try:
        data = request.get_json()
        new_days = int(data.get('days'))
        class_date = data.get('date')

        if new_days is None or not class_date:
            return jsonify({"error": "Both days and date are required"}), 400

        conn = sqlite3.connect("ams.db")
        cursor = conn.cursor()

        # Insert a new row with days and date
        cursor.execute("INSERT INTO total (days, date) VALUES (?, ?)", (new_days, class_date))

        conn.commit()

        # Get updated total
        cursor.execute("SELECT SUM(days) FROM total")
        total_days = cursor.fetchone()[0] or 0

        conn.close()

        return jsonify({"message": f"Added {new_days} days on {class_date}. Total is now {total_days}.", "total_days": total_days})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



#Fetch total days in real-time (No global variable)
@app.route('/get_total_days', methods=['GET'])
def get_total_days():
    try:
        conn = sqlite3.connect("ams.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(days) FROM total")
        total_days = cursor.fetchone()[0] or 0
        conn.close()

        return jsonify({"total_days": total_days})

    except Exception as e:
        return jsonify({"error": str(e)}), 500




def get_attendance_data():
    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()

    query = '''
    SELECT 
        u.name, 
        u.rollno, 
        u.class, 
        u.section, 
        COUNT(a.user_id) AS attending_classes, 
        (COUNT(a.user_id) * 100.0 / (SELECT COUNT(DISTINCT date) FROM admins)) AS attendance_percentage
    FROM users u
    LEFT JOIN admins a ON u.id = a.user_id
    GROUP BY u.id;
    '''
    
    cursor.execute(query)
    attendance_data = cursor.fetchall()
    conn.close()

    return attendance_data

@app.route('/admindata')
def admindata():
    return render_template('admindata.html')


@app.route('/get_attendance')
def get_attendance():
    data = retrieve_attendance_data()  # Fetch attendance data
    total_classes = get_total_classes()  # Set total classes manually

    attendance_list = [
        {
            'name': row[0],
            'rollno': row[1],
            'class': row[2],
            'section': row[3],
            'attending_classes': row[4],
            'attendance_percentage': round(row[5], 2) if row[5] is not None else 0
        }
        for row in data
    ]

    return jsonify({'total_classes': total_classes, 'attendance': attendance_list})

 # Define a default value (change as needed)
 # Assign the value

TOTAL_CLASSES = total_days_value

import sqlite3

def retrieve_attendance_data(class_name=None, section=None):
    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()

    # Fetch total_classes from the "total" table
    cursor.execute("SELECT days FROM total ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    total_classes = result[0] if result else 1  # Default to 1 to avoid division by zero

    query = '''
    SELECT 
        u.name, 
        u.rollno, 
        u.class, 
        u.section, 
        COUNT(a.user_id) AS attending_classes, 
        (COUNT(a.user_id) * 100.0 / ?) AS attendance_percentage
    FROM users u
    LEFT JOIN admins a ON u.id = a.user_id
    WHERE 1=1
    '''
    
    params = [total_classes]
    if class_name:
        query += " AND u.class = ?"
        params.append(class_name)
    if section:
        query += " AND u.section = ?"
        params.append(section)
    
    query += " GROUP BY u.id"

    cursor.execute(query, params)
    attendance_data = cursor.fetchall()
    
    conn.close()
    return attendance_data

@app.route('/attendance_dashboard')
def attendance_dashboard():
    return render_template('fetch_data.html')

@app.route('/attendance_filter', methods=['GET'])
def fetch_filtered_attendance():
    class_name = request.args.get('class', None)
    section = request.args.get('section', None)
    
    data = retrieve_attendance_data(class_name, section)
    attendance_list = [
        {
            'name': row[0],
            'rollno': row[1],
            'class': row[2],
            'section': row[3],
            'attending_classes': row[4],
            'attendance_percentage': round(row[5], 2) if row[5] is not None else 0
        }
        for row in data
    ]
    return jsonify(attendance_list)

# Route to render the HTML form
@app.route('/total')
def total():
    return render_template('total.html')

# Database connection function
def get_db_connection():
    conn = sqlite3.connect("ams.db")
    conn.row_factory = sqlite3.Row
    return conn

# Forgot Password Route
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form["username"]
        rollno = request.form["rollno"]
        regno = request.form["regno"]
        gmail = request.form["gmail"]
        new_password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Check if passwords match
        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("forgot_password"))

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute('''SELECT * FROM users WHERE name=? AND rollno=? AND regno=? AND gmail=?''', 
                       (username, rollno, regno, gmail))
        user = cursor.fetchone()

        if user:
            #Updating password directly without hashing
            cursor.execute("UPDATE users SET password=? WHERE rollno=?", (new_password, rollno))
            conn.commit()
            conn.close()

            flash("Password updated successfully!", "success")
            return redirect(url_for("login"))  # Redirect to login page
        else:
            flash("User details do not match!", "danger")

        conn.close()

    return render_template("forgot_password.html")

def fetch_logged_in_admins():
    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()
    
    # Fetch user details (name, rollno) along with admin login details
    cursor.execute("""
        SELECT admins.user_id, users.name, users.rollno, admins.login_time, admins.date 
        FROM admins
        JOIN users ON admins.user_id = users.id
        WHERE admins.login_time IS NOT NULL
    """)
    
    admins = cursor.fetchall()
    conn.close()
    
    # Convert to a list of dictionaries for JSON response
    return [{'user_id': row[0], 'name': row[1], 'rollno': row[2], 'login_time': row[3], 'date': row[4]} for row in admins]

@app.route('/admin_main')
def admin_main():
    return render_template('admin_main_data.html')

@app.route('/get_logged_in_admins')
def get_logged_in_admins():
    return jsonify(fetch_logged_in_admins())

@app.route('/student_marks')
def student_marks():
    return render_template('add_student.html')

# Database connection function
def get_db_connection():
    conn = sqlite3.connect("ams.db")  # Change the database name if needed
    conn.row_factory = sqlite3.Row
    return conn

# Function to get user ID from roll number
def get_user_id(rollno):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE rollno = ?", (rollno,))
    user = cursor.fetchone()
    conn.close()
    return user["id"] if user else None  # Return user ID if found, else None

# Route to display the form and insert data
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':  # Handle form submission
        rollno = request.form['rollno']
        user_id = get_user_id(rollno)

        if not user_id:
            flash("Error: Roll number not found!", "danger")
            return redirect('/add_student')

        # Get form data
        subject1 = request.form['subject1']
        marks1 = int(request.form['marks1'])
        subject2 = request.form['subject2']
        marks2 = int(request.form['marks2'])
        subject3 = request.form['subject3']
        marks3 = int(request.form['marks3'])
        max_marks = int(request.form['max_marks'])
        exam_type = request.form['exam_type']

        # Calculate total and percentage
        total_marks = marks1 + marks2 + marks3
        percentage = (total_marks / (max_marks * 3)) * 100

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO student_marks (user_id, subject1, marks1, subject2, marks2, subject3, marks3, total_marks, max_marks, percentage, exam_type) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, subject1, marks1, subject2, marks2, subject3, marks3, total_marks, max_marks, percentage, exam_type))
            
            conn.commit()
            conn.close()
            flash("Student marks added successfully!", "success")
            return redirect('/add_student')

        except Exception as e:
            flash("This student marks has already uploaded", "danger")

    return render_template('add_student.html')

# Route to display student marks page
@app.route('/view_marks')
@login_required
def view_marks():
    return render_template('view_marks.html')

# API Route to fetch marks for the logged-in user
@app.route('/get_student_marks', methods=['GET'])
@login_required
def get_student_marks():
    user_id = current_user.id  # Get the logged-in user ID

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch marks for the logged-in user
    cursor.execute("""
        SELECT subject1, marks1, subject2, marks2, subject3, marks3, total_marks, percentage, exam_type 
        FROM student_marks WHERE user_id = ?
    """, (user_id,))
    marks = cursor.fetchall()
    
    conn.close()

    if not marks:
        return jsonify({"error": "No marks found for your account"}), 404

    results = {
        "name": current_user.name,
        "rollno": current_user.rollno,
        "marks": [dict(row) for row in marks]
    }
    return jsonify(results)

# Function to fetch student marks by class and section
def get_students_by_class_section(class_name, section):
    conn = sqlite3.connect("ams.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT users.name, users.rollno, student_marks.subject1, student_marks.marks1, 
               student_marks.subject2, student_marks.marks2, student_marks.subject3, student_marks.marks3,
               student_marks.total_marks, student_marks.percentage, student_marks.exam_type
        FROM student_marks
        JOIN users ON student_marks.user_id = users.id
        WHERE users.class = ? AND users.section = ?
    ''', (class_name, section))

    students = cursor.fetchall()
    conn.close()
    
    return students

@app.route('/display_marks_by_class_and_section')
def display_marks_by_class_and_section():
    return render_template('display_marks.html')

@app.route('/get_students', methods=['POST'])
def get_students():
    data = request.json
    class_name = data.get('class')
    section = data.get('section')

    students = get_students_by_class_section(class_name, section)
    
    return jsonify(students)

def get_login_data():
    conn = sqlite3.connect("ams.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT users.name, users.rollno, users.class, users.section, admins.login_time, admins.date 
        FROM admins 
        JOIN users ON admins.user_id = users.id
    ''')
    
    data = cursor.fetchall()
    conn.close()
    
    return [{
        "name": row[0], 
        "rollno": row[1], 
        "class": row[2], 
        "section": row[3], 
        "login_time": row[4], 
        "login_date": row[5]  # Added login_date
    } for row in data]

@app.route('/get_login_data')
def login_data():
    return jsonify(get_login_data())

@app.route('/late')
def late():
    return render_template('late.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    data = request.json
    name, email, message = data["name"], data["email"], data["message"]

    try:
        conn = sqlite3.connect("ams.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO feedback (name, email, message) VALUES (?, ?, ?)", (name, email, message))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        print("Error:", e)
        return jsonify({"success": False})

@app.route("/get_feedback", methods=["GET"])
def get_feedback():
    try:
        conn = sqlite3.connect("ams.db")
        cursor = conn.cursor()
        # Fetch feedback in descending order (latest first)
        cursor.execute("SELECT name, email, message FROM feedback ORDER BY id DESC")
        feedback_data = cursor.fetchall()
        conn.close()

        feedback_list = [{"name": row[0], "email": row[1], "message": row[2]} for row in feedback_data]
        return jsonify(feedback_list)

    except Exception as e:
        print("Error:", e)
        return jsonify([])

@app.route("/feedback_list")
def feedback_list():
    return render_template("feedback_list.html")

# Fetch user data from SQLite database
def get_users():
    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, rollno, regno, class, section, phone, gmail FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

# API route to return user data as JSON
@app.route('/get_users')
def get_users_api():
    users = get_users()
    return jsonify(users)

# API route to update user data
@app.route('/update_user', methods=['POST'])
def update_user():
    data = request.json
    user_id = data['id']
    name = data['name']
    rollno = data['rollno']
    regno = data['regno']
    class_name = data['class']
    section = data['section']
    phone = data['phone']
    gmail = data['gmail']

    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET name=?, rollno=?, regno=?, class=?, section=?, phone=?, gmail=?
        WHERE id=?
    """, (name, rollno, regno, class_name, section, phone, gmail, user_id))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "User updated successfully!"})

# API route to delete user data
@app.route('/delete_user', methods=['POST'])
def delete_user():
    data = request.json
    user_id = data['id']

    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "User deleted successfully!"})

# Route to render the HTML page
@app.route('/update_delete')
def update_delete():
    return render_template('update_delete.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

def fetch_all_users():
    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, rollno, regno, class, section, phone, gmail, password FROM users")  # Include password
    users = cursor.fetchall()
    conn.close()

    user_list = [
        {
            "id": row[0],
            "name": row[1],
            "rollno": row[2],
            "regno": row[3],
            "class": row[4],
            "section": row[5],
            "phone": row[6],
            "gmail": row[7],
            "password": row[8]  # Include password
        }
        for row in users
    ]
    return user_list

@app.route('/users')
def users():
    return jsonify(fetch_all_users())

@app.route('/view_users_data')
def view_users_data():
    return render_template('all_users_data.html')

def get_email(rollno):
    """Fetch email based on roll number"""
    conn = sqlite3.connect("ams.db")
    cursor = conn.cursor()

    cursor.execute("SELECT gmail FROM users WHERE rollno = ?", (rollno,))
    result = cursor.fetchone()

    conn.close()
    
    return result[0] if result else None  # Return the email

def has_message_been_sent(rollno):
    """Check if a message has already been sent today to this roll number."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect("ams.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM late WHERE rollno = ? AND date_sent = ?", (rollno, today))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def store_message(rollno, email, message):
    """Store sent email details in 'late' table."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect("ams.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO late (rollno, phone, message, date_sent) 
        VALUES (?, ?, ?, ?)
    """, (rollno, email, message, today))
    conn.commit()
    conn.close()

def send_email_function(email, message):
    """Function to send an email"""
    try:
        msg = Message("Late Arrival Notification", recipients=[email])
        msg.body = message
        mail.send(msg)
        return True
    except Exception as e:
        return str(e)

@app.route('/send_email', methods=['POST'])
def send_email():
    """API endpoint to send email"""
    data = request.json
    rollno = data.get('rollno')
    message = data.get('message')

    email = get_email(rollno)

    if email is None:
        return jsonify({"success": False, "error": "No email found for this roll number"})

    if has_message_been_sent(rollno):
        return jsonify({"success": False, "error": "Email already sent today!"})

    result = send_email_function(email, message)

    if result is True:
        store_message(rollno, email, message)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": result})

@app.route('/get_sent_messages', methods=['GET'])
def get_sent_messages():
    """Fetch list of roll numbers who have received an email today"""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect("ams.db")
    cursor = conn.cursor()
    cursor.execute("SELECT rollno FROM late WHERE date_sent = ?", (today,))
    sent_messages = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(sent_messages)

@app.route('/faculty_index')
def faculty_index():
    return render_template('faculty_index.html')

@app.route('/faculty')
def faculty():
    return render_template('add_faculty.html')

@app.route('/add_faculty', methods=['POST'])
def add_faculty():
    data = request.json
    name = data.get('name')
    profession = data.get('profession')
    department = data.get('department')
    password = data.get('password')

    if not name or not profession or not department or not password:
        return jsonify({'error': 'Missing fields'}), 400

    # Hash password before storing

    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO faculty (name, profession, department, password) VALUES (?, ?, ?, ?)",
                   (name, profession, department, password))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Faculty added successfully'}), 200

@app.route('/get_faculty', methods=['GET'])
def get_faculty():
    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, profession, department, password FROM faculty")
    faculty_data = cursor.fetchall()
    conn.close()

    faculty_list = []
    for faculty in faculty_data:
        faculty_list.append({
            'id': faculty[0],
            'name': faculty[1],
            'profession': faculty[2],
            'department': faculty[3],
            'password': faculty[4]  # Hashed password
        })

    return jsonify(faculty_list)

@app.route('/update_faculty', methods=['POST'])
def update_faculty():
    try:
        data = request.json
        faculty_id = data.get('id')
        name = data.get('name')
        profession = data.get('profession')
        department = data.get('department')

        print("Received Data:", data)  # Debugging Line

        if not faculty_id or not name or not profession or not department:
            return jsonify({'error': 'Missing required fields'}), 400

        conn = sqlite3.connect('ams.db')
        cursor = conn.cursor()
        
        cursor.execute('''UPDATE faculty 
                          SET name = ?, profession = ?, department = ? 
                          WHERE id = ?''', 
                       (name, profession, department, faculty_id))
        
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'No faculty member found with this ID'}), 404

        conn.close()

        return jsonify({'message': 'Faculty updated successfully'}), 200

    except sqlite3.Error as e:
        print("SQLite Error:", str(e))  # Debugging Line
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

    except Exception as e:
        print("General Error:", str(e))  # Debugging Line
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500
    
@app.route('/delete_faculty', methods=['POST'])
def delete_faculty():
    try:
        data = request.json
        faculty_id = data.get('id')

        if not faculty_id:
            return jsonify({'error': 'Faculty ID is required'}), 400

        conn = sqlite3.connect('ams.db')
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM faculty WHERE id = ?", (faculty_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Faculty ID not found'}), 404

        conn.close()

        return jsonify({'message': 'Faculty deleted successfully'}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    










@app.route('/att_detail')
@login_required
def att_detail():
    return render_template('att_detail.html', user_id=current_user.id)




def fetch_attendance(user_id):
    conn = sqlite3.connect("ams.db")
    cursor = conn.cursor()

    # Get all dates class was conducted
    cursor.execute("SELECT date FROM total")
    total_dates = set(row[0] for row in cursor.fetchall())

    # Get all dates student was present
    cursor.execute("SELECT date FROM admins WHERE user_id = ?", (user_id,))
    present_dates = set(row[0] for row in cursor.fetchall())

    all_dates = total_dates.union(present_dates)

    attendance = {}
    for date in all_dates:
        if date in total_dates and date in present_dates:
            attendance[date] = "present"
        elif date in total_dates and date not in present_dates:
            attendance[date] = "absent"
        else:
            attendance[date] = "no-class"

    conn.close()
    return attendance


@app.route('/calendar/<int:user_id>')
def calendar(user_id):
    attendance_data = fetch_attendance(user_id)
    return render_template("att_detail.html", attendance_json=json.dumps(attendance_data))



@app.route('/api/attendance/<int:user_id>')
def attendance_api(user_id):
    from datetime import datetime
    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()

    # Get all class dates
    cursor.execute("SELECT date FROM total")
    all_dates = [row[0] for row in cursor.fetchall()]

    # Get attended dates for the user
    cursor.execute("SELECT date FROM admins WHERE user_id = ?", (user_id,))
    present_dates = set(row[0] for row in cursor.fetchall())

    attendance = {}
    for d in all_dates:
        if d in present_dates:
            attendance[d] = 'present'
        else:
            attendance[d] = 'absent'

    return jsonify(attendance)









@app.route('/api/attendance_table/<int:user_id>')
def get_attendance_table(user_id):
    conn = sqlite3.connect('ams.db')
    cursor = conn.cursor()

    # Only fetch name (no roll column used)
    cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        return jsonify([])

    name = user[0]

    # Get all total class days
    cursor.execute("SELECT date FROM total")
    total_dates = [row[0] for row in cursor.fetchall()]

    # Get present dates for this user
    cursor.execute("SELECT date FROM admins WHERE user_id = ?", (user_id,))
    present_dates = {row[0] for row in cursor.fetchall()}

    result = []
    for date in total_dates:
        status = "Present" if date in present_dates else "Absent"
        result.append({
            "name": name,
            "date": date,
            "status": status
        })

    conn.close()
    return jsonify(result)


@app.route('/terms')
def terms():
    return render_template('terms.html')

print("Welcome to SAMS website. click here to more information http://127.0.0.1:5000/")

if __name__ == '__main__': 
    init_db()
    app.run(debug=True)




