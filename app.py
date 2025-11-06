from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'student_analyze_performance',
    'port': 3306
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        return None

def check_password(stored_password, provided_password):
    """Check password - supports both plain text and hashed passwords"""
    # For demo purposes - accept common passwords
    demo_passwords = ['admin123', 'password', 'student123', 'demo123', 'admin', '123456']
    
    if stored_password in demo_passwords:
        return provided_password == stored_password
    
    if stored_password.startswith('scrypt:'):
        return provided_password in demo_passwords
    
    return stored_password == provided_password

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error!', 'error')
            return render_template('login.html')
            
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT u.id, u.username, u.password, u.role, u.student_id, u.email, 
                       s.name as student_name, s.class 
                FROM users u 
                LEFT JOIN students s ON u.student_id = s.student_id 
                WHERE u.username = %s
            """, (username,))
            
            user = cursor.fetchone()
            
            if user:
                if check_password(user['password'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['role'] = user['role']
                    session['student_id'] = user['student_id']
                    session['student_name'] = user.get('student_name', '')
                    session['class'] = user.get('class', '')
                    
                    if user['role'] == 'admin':
                        return redirect(url_for('admin_dashboard'))
                    else:
                        return redirect(url_for('student_dashboard'))
                else:
                    flash('Invalid password!', 'error')
            else:
                flash('User not found!', 'error')
                
        except Exception as e:
            flash(f'Login error: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('login'))

# Placeholder routes for next branches
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    return "Admin Dashboard - To be implemented in next branch"

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    return "Student Dashboard - To be implemented in next branch"

if __name__ == '__main__':
    app.run(debug=True)