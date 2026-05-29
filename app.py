from flask import Flask,render_template,request,redirect,url_for,session,send_from_directory
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# SECRET KEY

app.secret_key = 'secret123'

# DATABASE CONFIGURATION

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'lms_db'

# UPLOAD FOLDER

UPLOAD_FOLDER = 'uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)

# HOME PAGE

@app.route('/')

def home():

    return redirect(url_for('login'))

# REGISTER

@app.route('/register',methods=['GET','POST'])

def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        cur = mysql.connection.cursor()

        cur.execute(
        """
        INSERT INTO users(name,email,password,role)
        VALUES(%s,%s,%s,%s)
        """,
        (name,email,password,role)
        )

        mysql.connection.commit()

        cur.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# LOGIN

@app.route('/login',methods=['GET','POST'])

def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
        """
        SELECT * FROM users
        WHERE email=%s AND password=%s
        """,
        (email,password)
        )

        user = cur.fetchone()

        cur.close()

        if user:

            session['name'] = user[1]
            session['email'] = user[2]

            return redirect(url_for('dashboard'))

        else:

            return "Invalid Email or Password"

    return render_template('login.html')

# DASHBOARD

@app.route('/dashboard')

def dashboard():

    if 'name' in session:

        return render_template(
            'dashboard.html',
            name=session['name']
        )

    return redirect(url_for('login'))

# LOGOUT

@app.route('/logout')

def logout():

    session.clear()

    return redirect(url_for('login'))

# ADD COURSE

@app.route('/add_course',methods=['GET','POST'])

def add_course():

    if request.method == 'POST':

        course_name = request.form['course_name']
        course_duration = request.form['course_duration']
        course_fee = request.form['course_fee']

        cur = mysql.connection.cursor()

        cur.execute(
        """
        INSERT INTO courses
        (course_name,course_duration,course_fee)
        VALUES(%s,%s,%s)
        """,
        (course_name,course_duration,course_fee)
        )

        mysql.connection.commit()

        cur.close()

        return redirect(url_for('view_courses'))

    return render_template('add_course.html')

# VIEW COURSES

@app.route('/view_courses')

def view_courses():

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM courses")

    courses = cur.fetchall()

    cur.close()

    return render_template(
        'view_courses.html',
        courses=courses
    )

# DELETE COURSE

@app.route('/delete_course/<int:id>')

def delete_course(id):

    cur = mysql.connection.cursor()

    cur.execute(
    "DELETE FROM courses WHERE id=%s",
    (id,)
    )

    mysql.connection.commit()

    cur.close()

    return redirect(url_for('view_courses'))

# UPDATE COURSE

@app.route('/update_course/<int:id>',methods=['GET','POST'])

def update_course(id):

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        course_name = request.form['course_name']
        course_duration = request.form['course_duration']
        course_fee = request.form['course_fee']

        cur.execute(
        """
        UPDATE courses
        SET course_name=%s,
        course_duration=%s,
        course_fee=%s
        WHERE id=%s
        """,
        (course_name,course_duration,course_fee,id)
        )

        mysql.connection.commit()

        cur.close()

        return redirect(url_for('view_courses'))

    cur.execute(
    "SELECT * FROM courses WHERE id=%s",
    (id,)
    )

    course = cur.fetchone()

    cur.close()

    return render_template(
        'update_course.html',
        course=course
    )

# SMART STUDY PLANNER

@app.route('/planner',methods=['GET','POST'])

def planner():

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        task_name = request.form['task_name']
        task_date = request.form['task_date']

        cur.execute(
        """
        INSERT INTO planner
        (task_name,task_date,task_status)
        VALUES(%s,%s,%s)
        """,
        (task_name,task_date,'Pending')
        )

        mysql.connection.commit()

    cur.execute("SELECT * FROM planner")

    tasks = cur.fetchall()

    cur.close()

    return render_template(
        'planner.html',
        tasks=tasks
    )

# COMPLETE TASK

@app.route('/complete_task/<int:id>')

def complete_task(id):

    cur = mysql.connection.cursor()

    cur.execute(
    """
    UPDATE planner
    SET task_status=%s
    WHERE id=%s
    """,
    ('Completed',id)
    )

    mysql.connection.commit()

    cur.close()

    return redirect(url_for('planner'))

# STUDENT ENROLLMENT

@app.route('/enrollment',methods=['GET','POST'])

def enrollment():

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM courses")

    courses = cur.fetchall()

    if request.method == 'POST':

        student_name = request.form['student_name']
        student_email = request.form['student_email']
        course_name = request.form['course_name']

        cur.execute(
        """
        INSERT INTO enrollments
        (student_name,student_email,course_name)
        VALUES(%s,%s,%s)
        """,
        (student_name,student_email,course_name)
        )

        mysql.connection.commit()

    cur.execute("SELECT * FROM enrollments")

    students = cur.fetchall()

    cur.close()

    return render_template(
        'enrollment.html',
        courses=courses,
        students=students
    )

# QUIZ MODULE

@app.route('/quiz',methods=['GET','POST'])

def quiz():

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM quiz")

    questions = cur.fetchall()

    score = None

    if request.method == 'POST':

        score = 0

        for q in questions:

            selected = request.form.get(
            f'question_{q[0]}'
            )

            correct = q[6]

            if selected == correct:

                score += 1

    cur.close()

    return render_template(
        'quiz.html',
        questions=questions,
        score=score
    )

# ATTENDANCE SYSTEM

@app.route('/attendance',methods=['GET','POST'])

def attendance():

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        student_name = request.form['student_name']
        course_name = request.form['course_name']
        attendance_date = request.form['attendance_date']
        status = request.form['status']

        cur.execute(
        """
        INSERT INTO attendance
        (student_name,course_name,attendance_date,status)
        VALUES(%s,%s,%s,%s)
        """,
        (student_name,course_name,attendance_date,status)
        )

        mysql.connection.commit()

    cur.execute("SELECT * FROM attendance")

    attendance_data = cur.fetchall()

    cur.close()

    return render_template(
        'attendance.html',
        attendance=attendance_data
    )

# NOTES UPLOAD SYSTEM

@app.route('/notes',methods=['GET','POST'])

def notes():

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        title = request.form['title']

        file = request.files['file']

        filename = secure_filename(file.filename)

        file.save(
        os.path.join(
        app.config['UPLOAD_FOLDER'],
        filename
        )
        )

        cur.execute(
        """
        INSERT INTO notes(title,filename)
        VALUES(%s,%s)
        """,
        (title,filename)
        )

        mysql.connection.commit()

    cur.execute("SELECT * FROM notes")

    notes_data = cur.fetchall()

    cur.close()

    return render_template(
        'notes.html',
        notes=notes_data
    )

# DOWNLOAD NOTES

@app.route('/uploads/<filename>')

def uploaded_file(filename):

    return send_from_directory(
    app.config['UPLOAD_FOLDER'],
    filename
    )

# RUN SERVER

if __name__ == '__main__':

    app.run(debug=True)