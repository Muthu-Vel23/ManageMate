from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime, timedelta
import json
import uuid
from flask_mail import Mail, Message


app = Flask(__name__)


app.secret_key = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'muthu2311vel@gmail.com'
app.config['MAIL_PASSWORD'] = 'oref dqrj gndc xwcn'

mail = Mail(app)


def send_due_mail(project_name, email, user_id):
    # Check if user has email notifications enabled
    conn = get_db_connection()
    settings = conn.execute('SELECT email_notifications FROM user_settings WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    
    # If no settings found or email notifications are disabled, don't send email
    if not settings or not settings['email_notifications']:
        return False
    
    try:
        msg = Message(subject='Project Due Time Exceeded - ManagerMate',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.body = f"""
        Hello,
        
        Your due time for project '{project_name}' has been exceeded. Please take necessary action.
        
        You can manage your notification preferences in the Settings page of ManagerMate.
        
        Best regards,
        ManagerMate Team
        """
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def check_due_dates():
    current_time = datetime.now()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get projects with user_id for notification checking
    cursor.execute("""
        SELECT p.id, p.name, p.due_date, p.employee_email, p.user_id 
        FROM projects p 
        WHERE p.completed = 0 AND p.due_date < ?
    """, (current_time,))
    projects = cursor.fetchall()

    for project in projects:
        due_time = project["due_date"]
        if isinstance(due_time, str):
            due_time = datetime.strptime(due_time, "%Y-%m-%dT%H:%M")
        
        if current_time > due_time:
            # Pass user_id to check notification preferences
            send_due_mail(project["name"], project["employee_email"], project["user_id"])

    conn.close()


# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/uploads/profiles', exist_ok=True)
os.makedirs('static/uploads/projects', exist_ok=True)
os.makedirs('static/uploads/achievements', exist_ok=True)

def init_db():
    conn = sqlite3.connect('managemate.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT,
            password_hash TEXT NOT NULL,
            profile_picture TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            start_date TIMESTAMP,
            due_date TIMESTAMP,
            file_path TEXT,
            completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            employee_email TEXT,  -- ✅ newly added
            FOREIGN KEY (user_id) REFERENCES users (id)
        )

        
    ''')
    
    # Tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            start_date TIMESTAMP,
            due_date TIMESTAMP,
            completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Goals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            deadline TIMESTAMP,
            completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Achievements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Rewards table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            points INTEGER DEFAULT 0,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Notes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Add this to init_db()

# User Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            email_notifications BOOLEAN DEFAULT TRUE,
            deadline_reminders BOOLEAN DEFAULT TRUE,
            achievement_alerts BOOLEAN DEFAULT TRUE,
            language TEXT DEFAULT 'en',
            theme TEXT DEFAULT 'light',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('managemate.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_motivational_quote():
    quotes = [
        "The way to get started is to quit talking and begin doing. - Walt Disney",
        "Innovation distinguishes between a leader and a follower. - Steve Jobs",
        "Your limitation—it's only your imagination.",
        "Push yourself, because no one else is going to do it for you.",
        "Great things never come from comfort zones.",
        "Dream it. Wish it. Do it.",
        "Success doesn't just find you. You have to go out and get it.",
        "The harder you work for something, the greater you'll feel when you achieve it.",
        "Dream bigger. Do bigger.",
        "Don't stop when you're tired. Stop when you're done."
    ]
    import random
    return random.choice(quotes)

def award_points(user_id, activity_type, points=10):
    conn = get_db_connection()
    
    reward_titles = {
        'project': 'Project Completed!',
        'task': 'Task Accomplished!',
        'goal': 'Goal Achieved!'
    }
    
    conn.execute('''
        INSERT INTO rewards (user_id, type, title, description, points)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, activity_type, reward_titles.get(activity_type, 'Achievement Unlocked!'), 
          f'You earned {points} points for completing a {activity_type}!', points))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = f"{user['first_name']} {user['last_name']}"
            session['user_email'] = user['email']  #  Add this line

            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('login.html')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Validate passwords match
        if new_password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('change_password.html')
        
        # Validate password length
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return render_template('change_password.html')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if user:
            # Update password
            new_password_hash = generate_password_hash(new_password)
            conn.execute('''
                UPDATE users SET password_hash = ? WHERE email = ?
            ''', (new_password_hash, email))
            conn.commit()
            conn.close()
            
            flash('Password changed successfully! Please login with your new password.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email address not found!', 'error')
            conn.close()
    
    return render_template('change_password.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']
        
        conn = get_db_connection()
        
        # Check if user already exists
        existing_user = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing_user:
            flash('Email already registered!', 'error')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        conn.execute('''
            INSERT INTO users (first_name, last_name, email, mobile, password_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (first_name, last_name, email, mobile, password_hash))
        
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    check_due_dates()  # Check and send overdue mails
    conn = get_db_connection()
    user_id = session['user_id']
    
    # Get user stats
    projects_count = conn.execute('SELECT COUNT(*) as count FROM projects WHERE user_id = ?', (user_id,)).fetchone()['count']
    completed_projects = conn.execute('SELECT COUNT(*) as count FROM projects WHERE user_id = ? AND completed = 1', (user_id,)).fetchone()['count']
    
    tasks_count = conn.execute('SELECT COUNT(*) as count FROM tasks WHERE user_id = ?', (user_id,)).fetchone()['count']
    completed_tasks = conn.execute('SELECT COUNT(*) as count FROM tasks WHERE user_id = ? AND completed = 1', (user_id,)).fetchone()['count']
    
    goals_count = conn.execute('SELECT COUNT(*) as count FROM goals WHERE user_id = ?', (user_id,)).fetchone()['count']
    completed_goals = conn.execute('SELECT COUNT(*) as count FROM goals WHERE user_id = ? AND completed = 1', (user_id,)).fetchone()['count']
    
    # Get overdue items
    current_time = datetime.now()
    overdue_projects = conn.execute('''
        SELECT name FROM projects 
        WHERE user_id = ? AND completed = 0 AND due_date < ?
        LIMIT 3
    ''', (user_id, current_time)).fetchall()
    
    overdue_tasks = conn.execute('''
        SELECT name FROM tasks 
        WHERE user_id = ? AND completed = 0 AND due_date < ?
        LIMIT 3
    ''', (user_id, current_time)).fetchall()
    
    # Get total points
    total_points = conn.execute('SELECT SUM(points) as total FROM rewards WHERE user_id = ?', (user_id,)).fetchone()['total'] or 0
    
    conn.close()
    
    stats = {
        'projects': {'total': projects_count, 'completed': completed_projects},
        'tasks': {'total': tasks_count, 'completed': completed_tasks},
        'goals': {'total': goals_count, 'completed': completed_goals},
        'total_points': total_points
    }
    
    quote = get_motivational_quote()
    
    return render_template('dashboard.html', stats=stats, quote=quote, 
                         overdue_projects=overdue_projects, overdue_tasks=overdue_tasks)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    conn = get_db_connection()
    user_id = session['user_id']
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        mobile = request.form['mobile']
        
        # Handle profile picture upload
        profile_picture = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                filename = secure_filename(f"profile_{user_id}_{file.filename}")
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'profiles', filename)
                file.save(file_path)
                profile_picture = f"uploads/profiles/{filename}"
        
        # Update user profile
        if profile_picture:
            conn.execute('''
                UPDATE users SET first_name = ?, last_name = ?, mobile = ?, profile_picture = ?
                WHERE id = ?
            ''', (first_name, last_name, mobile, profile_picture, user_id))
        else:
            conn.execute('''
                UPDATE users SET first_name = ?, last_name = ?, mobile = ?
                WHERE id = ?
            ''', (first_name, last_name, mobile, user_id))
        
        conn.commit()
        session['user_name'] = f"{first_name} {last_name}"
        flash('Profile updated successfully!', 'success')
    
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    return render_template('profile.html', user=user)

@app.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    conn = get_db_connection()
    user_id = session['user_id']
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date = request.form['start_date']
        due_date = request.form['due_date']
        employee_email = session['user_email']  # get email from the logged-in user


        # Handle file upload
        file_path = None
        if 'project_file' in request.files:
            file = request.files['project_file']
            if file and file.filename:
                filename = secure_filename(f"project_{uuid.uuid4()}_{file.filename}")
                file_path_full = os.path.join(app.config['UPLOAD_FOLDER'], 'projects', filename)
                file.save(file_path_full)
                file_path = f"uploads/projects/{filename}"
        
        conn.execute('''
            INSERT INTO projects (user_id, name, description, start_date, due_date, file_path,employee_email)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, description, start_date, due_date, file_path, employee_email))
        
        conn.commit()
        flash('Project added successfully!', 'success')
        return redirect(url_for('projects'))
    
    projects_list = conn.execute('''
        SELECT * FROM projects WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,)).fetchall()
    
    conn.close()
    return render_template('projects.html', projects=projects_list)

@app.route('/complete_project/<int:project_id>')
@login_required
def complete_project(project_id):
    conn = get_db_connection()
    user_id = session['user_id']
    
    conn.execute('''
        UPDATE projects SET completed = 1, completed_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
    ''', (project_id, user_id))
    
    conn.commit()
    conn.close()
    
    # Award points for completing project
    award_points(user_id, 'project', 20)
    
    flash('Project completed! You earned 20 points!', 'success')
    return redirect(url_for('projects'))

@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    conn = get_db_connection()
    user_id = session['user_id']
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date = request.form['start_date']
        due_date = request.form['due_date']
        
        conn.execute('''
            INSERT INTO tasks (user_id, name, description, start_date, due_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, name, description, start_date, due_date))
        
        conn.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('tasks'))
    
    tasks_list = conn.execute('''
        SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,)).fetchall()
    
    conn.close()
    return render_template('tasks.html', tasks=tasks_list)

@app.route('/complete_task/<int:task_id>')
@login_required
def complete_task(task_id):
    conn = get_db_connection()
    user_id = session['user_id']
    
    conn.execute('''
        UPDATE tasks SET completed = 1, completed_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
    ''', (task_id, user_id))
    
    conn.commit()
    conn.close()
    
    # Award points for completing task
    award_points(user_id, 'task', 10)
    
    flash('Task completed! You earned 10 points!', 'success')
    return redirect(url_for('tasks'))

@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    conn = get_db_connection()
    user_id = session['user_id']
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']
        
        conn.execute('''
            INSERT INTO goals (user_id, title, description, deadline)
            VALUES (?, ?, ?, ?)
        ''', (user_id, title, description, deadline))
        
        conn.commit()
        flash('Goal added successfully!', 'success')
        return redirect(url_for('goals'))
    
    goals_list = conn.execute('''
        SELECT * FROM goals WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,)).fetchall()
    
    conn.close()
    return render_template('goals.html', goals=goals_list)

@app.route('/complete_goal/<int:goal_id>')
@login_required
def complete_goal(goal_id):
    conn = get_db_connection()
    user_id = session['user_id']
    
    conn.execute('''
        UPDATE goals SET completed = 1, completed_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
    ''', (goal_id, user_id))
    
    conn.commit()
    conn.close()
    
    # Award points for completing goal
    award_points(user_id, 'goal', 30)
    
    flash('Goal achieved! You earned 30 points!', 'success')
    return redirect(url_for('goals'))

@app.route('/achievements', methods=['GET', 'POST'])
@login_required
def achievements():
    conn = get_db_connection()
    user_id = session['user_id']
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        # Handle file upload
        file_path = None
        if 'achievement_file' in request.files:
            file = request.files['achievement_file']
            if file and file.filename:
                filename = secure_filename(f"achievement_{uuid.uuid4()}_{file.filename}")
                file_path_full = os.path.join(app.config['UPLOAD_FOLDER'], 'achievements', filename)
                file.save(file_path_full)
                file_path = f"uploads/achievements/{filename}"
        
        conn.execute('''
            INSERT INTO achievements (user_id, title, description, file_path)
            VALUES (?, ?, ?, ?)
        ''', (user_id, title, description, file_path))
        
        conn.commit()
        flash('Achievement added successfully!', 'success')
        return redirect(url_for('achievements'))
    
    achievements_list = conn.execute('''
        SELECT * FROM achievements WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,)).fetchall()
    
    conn.close()
    return render_template('achievements.html', achievements=achievements_list)

@app.route('/gamification')
@login_required
def gamification():
    conn = get_db_connection()
    user_id = session['user_id']
    
    # Get user rewards
    rewards = conn.execute('''
        SELECT * FROM rewards WHERE user_id = ? ORDER BY earned_at DESC
    ''', (user_id,)).fetchall()
    
    # Calculate total points
    total_points = conn.execute('SELECT SUM(points) as total FROM rewards WHERE user_id = ?', (user_id,)).fetchone()['total'] or 0
    
    # Determine user level based on points
    level = min(total_points // 100 + 1, 10)  # Max level 10
    points_to_next_level = (level * 100) - total_points
    
    conn.close()
    
    return render_template('gamification.html', rewards=rewards, total_points=total_points, 
                         level=level, points_to_next_level=points_to_next_level)

@app.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    conn = get_db_connection()
    user_id = session['user_id']
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        conn.execute('''
            INSERT INTO notes (user_id, title, content)
            VALUES (?, ?, ?)
        ''', (user_id, title, content))
        
        conn.commit()
        flash('Note saved successfully!', 'success')
        return redirect(url_for('notes'))
    
    notes_list = conn.execute('''
        SELECT * FROM notes WHERE user_id = ? ORDER BY updated_at DESC
    ''', (user_id,)).fetchall()
    
    conn.close()
    return render_template('notes.html', notes=notes_list)

@app.route('/settings', methods=['GET'])
@login_required
def settings():
    conn = get_db_connection()
    user_id = session['user_id']
    
    # Get current settings
    settings = conn.execute('SELECT * FROM user_settings WHERE user_id = ?', (user_id,)).fetchone()
    
    # Default settings if none exist
    if not settings:
        settings = {
            'email_notifications': True,
            'deadline_reminders': True,
            'achievement_alerts': True,
            'language': 'en',
            'theme': 'light'
        }
    
    conn.close()
    return render_template('settings.html', settings=settings)

@app.route('/update_settings', methods=['POST'])
@login_required
def update_settings():
    conn = get_db_connection()
    user_id = session['user_id']
    
    # Get form data
    email_notifications = 'email_notifications' in request.form
    deadline_reminders = 'deadline_reminders' in request.form
    achievement_alerts = 'achievement_alerts' in request.form
    theme = request.form.get('theme', 'light')
    
    # Insert or update settings
    conn.execute('''
        INSERT OR REPLACE INTO user_settings 
        (user_id, email_notifications, deadline_reminders, achievement_alerts, theme, updated_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (user_id, email_notifications, deadline_reminders, achievement_alerts, theme))
    
    conn.commit()
    conn.close()
    
    # Update session theme
    session['theme'] = theme
    
    flash('Settings updated successfully!', 'success')
    return redirect(url_for('settings', saved='true'))

@app.route('/export_data')
@login_required
def export_data():
    import csv
    import io
    from flask import make_response
    
    conn = get_db_connection()
    user_id = session['user_id']
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # User information
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    writer.writerow(['=== USER INFORMATION ==='])
    writer.writerow(['Field', 'Value'])
    writer.writerow(['Name', f"{user['first_name']} {user['last_name']}"])
    writer.writerow(['Email', user['email']])
    writer.writerow(['Mobile', user['mobile'] or 'Not provided'])
    writer.writerow(['Created At', user['created_at']])
    writer.writerow([])
    
    # Projects
    projects = conn.execute('SELECT * FROM projects WHERE user_id = ?', (user_id,)).fetchall()
    writer.writerow(['=== PROJECTS ==='])
    writer.writerow(['Name', 'Description', 'Start Date', 'Due Date', 'Completed', 'Created At'])
    for project in projects:
        writer.writerow([
            project['name'],
            project['description'] or '',
            project['start_date'] or '',
            project['due_date'] or '',
            'Yes' if project['completed'] else 'No',
            project['created_at']
        ])
    writer.writerow([])
    
    # Tasks
    tasks = conn.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,)).fetchall()
    writer.writerow(['=== TASKS ==='])
    writer.writerow(['Name', 'Description', 'Start Date', 'Due Date', 'Completed', 'Created At'])
    for task in tasks:
        writer.writerow([
            task['name'],
            task['description'] or '',
            task['start_date'] or '',
            task['due_date'] or '',
            'Yes' if task['completed'] else 'No',
            task['created_at']
        ])
    writer.writerow([])
    
    # Goals
    goals = conn.execute('SELECT * FROM goals WHERE user_id = ?', (user_id,)).fetchall()
    writer.writerow(['=== GOALS ==='])
    writer.writerow(['Title', 'Description', 'Deadline', 'Completed', 'Created At'])
    for goal in goals:
        writer.writerow([
            goal['title'],
            goal['description'] or '',
            goal['deadline'] or '',
            'Yes' if goal['completed'] else 'No',
            goal['created_at']
        ])
    writer.writerow([])
    
    # Achievements
    achievements = conn.execute('SELECT * FROM achievements WHERE user_id = ?', (user_id,)).fetchall()
    writer.writerow(['=== ACHIEVEMENTS ==='])
    writer.writerow(['Title', 'Description', 'Created At'])
    for achievement in achievements:
        writer.writerow([
            achievement['title'],
            achievement['description'] or '',
            achievement['created_at']
        ])
    writer.writerow([])
    
    # Notes
    notes = conn.execute('SELECT * FROM notes WHERE user_id = ?', (user_id,)).fetchall()
    writer.writerow(['=== NOTES ==='])
    writer.writerow(['Title', 'Content', 'Created At'])
    for note in notes:
        writer.writerow([
            note['title'],
            note['content'] or '',
            note['created_at']
        ])
    writer.writerow([])
    
    # Rewards
    rewards = conn.execute('SELECT * FROM rewards WHERE user_id = ?', (user_id,)).fetchall()
    writer.writerow(['=== REWARDS ==='])
    writer.writerow(['Type', 'Title', 'Description', 'Points', 'Earned At'])
    for reward in rewards:
        writer.writerow([
            reward['type'],
            reward['title'],
            reward['description'] or '',
            reward['points'],
            reward['earned_at']
        ])
    
    conn.close()
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=managermate_data_{user["first_name"]}_{user["last_name"]}.csv'
    
    return response

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
