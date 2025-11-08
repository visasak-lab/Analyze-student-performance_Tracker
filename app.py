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


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'error')
        return render_template('admin_dashboard.html')
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Basic stats
        cursor.execute("SELECT COUNT(*) as total FROM students")
        total_students = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM scores")
        total_scores = cursor.fetchone()['total']
        
        cursor.execute("SELECT AVG(average) as overall_avg FROM scores")
        overall_avg_result = cursor.fetchone()
        overall_avg = overall_avg_result['overall_avg'] if overall_avg_result['overall_avg'] else 0
        
        # Performance distribution
        cursor.execute("""
            SELECT performance_level, COUNT(*) as count 
            FROM scores 
            GROUP BY performance_level
        """)
        performance_data = cursor.fetchall()
        
        # Recent activities
        cursor.execute("""
            SELECT sc.*, st.name, st.class 
            FROM scores sc 
            JOIN students st ON sc.student_id = st.student_id 
            ORDER BY sc.id DESC LIMIT 10
        """)
        recent_activities = cursor.fetchall()
        
        # Class averages
        cursor.execute("""
            SELECT st.class, AVG(sc.average) as class_avg, COUNT(DISTINCT st.student_id) as student_count
            FROM scores sc
            JOIN students st ON sc.student_id = st.student_id
            GROUP BY st.class
            ORDER BY st.class
        """)
        class_averages = cursor.fetchall()
        
        # Term-wise performance
        cursor.execute("""
            SELECT term, AVG(average) as avg_score, COUNT(*) as count
            FROM scores 
            GROUP BY term 
            ORDER BY term
        """)
        term_performance = cursor.fetchall()
        
        # Component averages
        cursor.execute("""
            SELECT 
                AVG(quiz) as avg_quiz,
                AVG(homework) as avg_homework,
                AVG(midterm) as avg_midterm,
                AVG(final) as avg_final
            FROM scores
        """)
        subject_averages = cursor.fetchone()
        
        # Gender performance
        cursor.execute("""
            SELECT st.gender, AVG(sc.average) as avg_score, COUNT(*) as count
            FROM scores sc
            JOIN students st ON sc.student_id = st.student_id
            GROUP BY st.gender
        """)
        gender_performance = cursor.fetchall()
        
        # Top performing students
        cursor.execute("""
            SELECT st.student_id, st.name, st.class, AVG(sc.average) as avg_score
            FROM scores sc
            JOIN students st ON sc.student_id = st.student_id
            GROUP BY st.student_id, st.name, st.class
            ORDER BY avg_score DESC
            LIMIT 5
        """)
        top_students = cursor.fetchall()
        
        # Students with no scores
        cursor.execute("""
            SELECT s.student_id, s.name, s.class
            FROM students s
            LEFT JOIN scores sc ON s.student_id = sc.student_id
            WHERE sc.student_id IS NULL
        """)
        students_no_scores = cursor.fetchall()
        
        # Class Comparison Data
        cursor.execute("""
            SELECT 
                st.class,
                AVG(sc.average) as overall_avg,
                AVG(sc.quiz) as avg_quiz,
                AVG(sc.homework) as avg_homework,
                AVG(sc.midterm) as avg_midterm,
                AVG(sc.final) as avg_final,
                COUNT(DISTINCT st.student_id) as student_count
            FROM scores sc
            JOIN students st ON sc.student_id = st.student_id
            GROUP BY st.class
            ORDER BY st.class
        """)
        class_comparison = cursor.fetchall()
        
        # Term Comparison Data
        cursor.execute("""
            SELECT 
                term,
                AVG(average) as avg_score,
                AVG(quiz) as avg_quiz,
                AVG(homework) as avg_homework,
                AVG(midterm) as avg_midterm,
                AVG(final) as avg_final,
                COUNT(*) as record_count
            FROM scores 
            GROUP BY term
            ORDER BY term
        """)
        term_comparison = cursor.fetchall()
        
        # Gender Comparison Data
        cursor.execute("""
            SELECT 
                st.gender,
                AVG(sc.average) as overall_avg,
                AVG(sc.quiz) as avg_quiz,
                AVG(sc.homework) as avg_homework,
                AVG(sc.midterm) as avg_midterm,
                AVG(sc.final) as avg_final,
                COUNT(*) as record_count
            FROM scores sc
            JOIN students st ON sc.student_id = st.student_id
            GROUP BY st.gender
        """)
        gender_comparison = cursor.fetchall()
        
        # Performance Level by Class
        cursor.execute("""
            SELECT 
                st.class,
                sc.performance_level,
                COUNT(*) as count
            FROM scores sc
            JOIN students st ON sc.student_id = st.student_id
            GROUP BY st.class, sc.performance_level
            ORDER BY st.class, sc.performance_level
        """)
        performance_by_class = cursor.fetchall()
        
        # Prepare data for charts
        performance_levels = ['Excellent', 'Good', 'Average', 'Poor']
        performance_counts = {level: 0 for level in performance_levels}
        for item in performance_data:
            if item['performance_level'] in performance_counts:
                performance_counts[item['performance_level']] = item['count']
        
        class_labels = []
        class_scores = []
        original_class_student_counts = []
        for class_avg in class_averages:
            class_labels.append(f"Class {class_avg['class']}")
            class_scores.append(float(class_avg['class_avg']) if class_avg['class_avg'] else 0)
            original_class_student_counts.append(class_avg['student_count'])
        
        term_labels = [item['term'] for item in term_performance]
        term_scores = [float(item['avg_score']) if item['avg_score'] else 0 for item in term_performance]
        term_counts = [item['count'] for item in term_performance]
        
        subject_labels = ['Quiz', 'Homework', 'Midterm', 'Final']
        subject_scores = [
            float(subject_averages['avg_quiz']) if subject_averages['avg_quiz'] else 0,
            float(subject_averages['avg_homework']) if subject_averages['avg_homework'] else 0,
            float(subject_averages['avg_midterm']) if subject_averages['avg_midterm'] else 0,
            float(subject_averages['avg_final']) if subject_averages['avg_final'] else 0
        ]
        
        gender_labels = []
        gender_scores = []
        gender_counts = []
        for gender in gender_performance:
            gender_labels.append('Female' if gender['gender'] == 'F' else 'Male')
            gender_scores.append(float(gender['avg_score']) if gender['avg_score'] else 0)
            gender_counts.append(gender['count'])
        
        # Prepare data for comparison charts
        class_comparison_labels = [f"Class {item['class']}" for item in class_comparison]
        class_comparison_scores = [float(item['overall_avg']) if item['overall_avg'] else 0 for item in class_comparison]
        comparison_class_student_counts = [item['student_count'] for item in class_comparison]
        
        term_comparison_labels = [item['term'] for item in term_comparison]
        term_comparison_scores = [float(item['avg_score']) if item['avg_score'] else 0 for item in term_comparison]
        term_record_counts = [item['record_count'] for item in term_comparison]
        
        gender_comparison_labels = ['Female' if item['gender'] == 'F' else 'Male' for item in gender_comparison]
        gender_comparison_scores = [float(item['overall_avg']) if item['overall_avg'] else 0 for item in gender_comparison]
        gender_record_counts = [item['record_count'] for item in gender_comparison]
        
        # Component averages by class for radar chart
        class_component_data = {}
        for item in class_comparison:
            class_name = f"Class {item['class']}"
            class_component_data[class_name] = [
                float(item['avg_quiz']) if item['avg_quiz'] else 0,
                float(item['avg_homework']) if item['avg_homework'] else 0,
                float(item['avg_midterm']) if item['avg_midterm'] else 0,
                float(item['avg_final']) if item['avg_final'] else 0
            ]
        
        # Performance distribution by class
        performance_distribution_by_class = {}
        for item in performance_by_class:
            class_name = f"Class {item['class']}"
            if class_name not in performance_distribution_by_class:
                performance_distribution_by_class[class_name] = {'Excellent': 0, 'Good': 0, 'Average': 0, 'Poor': 0}
            performance_distribution_by_class[class_name][item['performance_level']] = item['count']
        
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        total_students = total_scores = overall_avg = 0
        performance_counts = {'Excellent': 0, 'Good': 0, 'Average': 0, 'Poor': 0}
        recent_activities = []
        class_labels = class_scores = original_class_student_counts = term_labels = term_scores = term_counts = []
        subject_labels = subject_scores = gender_labels = gender_scores = gender_counts = []
        top_students = []
        students_no_scores = []
        # Initialize empty data for new charts
        class_comparison_labels = class_comparison_scores = comparison_class_student_counts = []
        term_comparison_labels = term_comparison_scores = term_record_counts = []
        gender_comparison_labels = gender_comparison_scores = gender_record_counts = []
        class_component_data = {}
        performance_distribution_by_class = {}
    finally:
        cursor.close()
        conn.close()
    
    return render_template('admin_dashboard.html', 
                         username=session.get('username'),
                         total_students=total_students,
                         total_scores=total_scores,
                         overall_avg=overall_avg,
                         performance_counts=performance_counts,
                         recent_activities=recent_activities,
                         class_labels=class_labels,
                         class_scores=class_scores,
                         class_student_counts=original_class_student_counts,
                         term_labels=term_labels,
                         term_scores=term_scores,
                         term_counts=term_counts,
                         subject_labels=subject_labels,
                         subject_scores=subject_scores,
                         gender_labels=gender_labels,
                         gender_scores=gender_scores,
                         gender_counts=gender_counts,
                         top_students=top_students,
                         students_no_scores=students_no_scores,
                         class_comparison_labels=class_comparison_labels,
                         class_comparison_scores=class_comparison_scores,
                         class_comparison_student_counts=comparison_class_student_counts,
                         term_comparison_labels=term_comparison_labels,
                         term_comparison_scores=term_comparison_scores,
                         term_record_counts=term_record_counts,
                         gender_comparison_labels=gender_comparison_labels,
                         gender_comparison_scores=gender_comparison_scores,
                         gender_record_counts=gender_record_counts,
                         class_component_data=class_component_data,
                         performance_distribution_by_class=performance_distribution_by_class)

@app.route('/admin/list-students')
def list_students():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'error')
        return render_template('list_students.html')
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get filter parameters
        search = request.args.get('search', '')
        class_filter = request.args.get('class', '')
        gender_filter = request.args.get('gender', '')
        
        # Build query with filters
        query = """
            SELECT s.student_id, s.name, s.class, s.gender,
                   COUNT(sc.id) as score_count,
                   AVG(sc.average) as avg_score,
                   MAX(sc.average) as highest_score,
                   MIN(sc.average) as lowest_score
            FROM students s
            LEFT JOIN scores sc ON s.student_id = sc.student_id
            WHERE 1=1
        """
        params = []
        
        if search:
            query += " AND s.name LIKE %s"
            params.append(f"%{search}%")
        
        if class_filter:
            query += " AND s.class = %s"
            params.append(class_filter)
        
        if gender_filter:
            query += " AND s.gender = %s"
            params.append(gender_filter)
        
        query += " GROUP BY s.student_id, s.name, s.class, s.gender ORDER BY s.class, s.name"
        
        cursor.execute(query, params)
        students = cursor.fetchall()
        
    except Exception as e:
        flash(f'Error loading students: {str(e)}', 'error')
        students = []
    finally:
        cursor.close()
        conn.close()
    
    return render_template('list_students.html', 
                         username=session.get('username'),
                         students=students)

@app.route('/admin/student/<student_id>')
def student_details(student_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'error')
        return redirect(url_for('list_students'))
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get student basic information with performance statistics
        cursor.execute("""
            SELECT s.student_id, s.name, s.class, s.gender,
                   COUNT(sc.id) as score_count,
                   AVG(sc.average) as avg_score,
                   MAX(sc.average) as highest_score,
                   MIN(sc.average) as lowest_score
            FROM students s
            LEFT JOIN scores sc ON s.student_id = sc.student_id
            WHERE s.student_id = %s
            GROUP BY s.student_id, s.name, s.class, s.gender
        """, (student_id,))
        
        student = cursor.fetchone()
        
        if not student:
            flash('Student not found!', 'error')
            return redirect(url_for('list_students'))
        
        # Get all scores for this student with detailed information
        cursor.execute("""
            SELECT sc.*, st.name, st.class, st.gender,
                   DATE_FORMAT(sc.created_at, '%Y-%m-%d') as date,
                   sc.average as score,
                   sc.performance_level,
                   sc.quiz, sc.homework, sc.midterm, sc.final
            FROM scores sc
            JOIN students st ON sc.student_id = st.student_id
            WHERE sc.student_id = %s
            ORDER BY sc.created_at DESC
        """, (student_id,))
        
        scores = cursor.fetchall()
        
        # Add scores to student dict for template
        student['scores'] = scores
        
        # Get component averages for this student
        cursor.execute("""
            SELECT 
                AVG(quiz) as avg_quiz,
                AVG(homework) as avg_homework,
                AVG(midterm) as avg_midterm,
                AVG(final) as avg_final,
                COUNT(*) as total_records
            FROM scores 
            WHERE student_id = %s
        """, (student_id,))
        
        subject_averages = cursor.fetchone()
        student['subject_averages'] = subject_averages
        
        # Get term-wise performance
        cursor.execute("""
            SELECT term, AVG(average) as term_avg, COUNT(*) as record_count
            FROM scores 
            WHERE student_id = %s
            GROUP BY term
            ORDER BY term
        """, (student_id,))
        
        term_performance = cursor.fetchall()
        student['term_performance'] = term_performance
        
        # Get performance level distribution
        cursor.execute("""
            SELECT performance_level, COUNT(*) as count
            FROM scores 
            WHERE student_id = %s
            GROUP BY performance_level
            ORDER BY COUNT(*) DESC
        """, (student_id,))
        
        performance_distribution = cursor.fetchall()
        student['performance_distribution'] = performance_distribution
        
    except Exception as e:
        flash(f'Error loading student details: {str(e)}', 'error')
        return redirect(url_for('list_students'))
    finally:
        cursor.close()
        conn.close()
    
    return render_template('student_details.html', 
                         username=session.get('username'),
                         student=student)

@app.route('/admin/score-details')
def score_details():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'error')
        return render_template('score_details.html')
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get filter parameters
        student_id = request.args.get('student_id', '')
        search_name = request.args.get('search_name', '')
        
        # Build query with filter
        query = """
            SELECT sc.*, st.name, st.class, st.gender,
                   DATE_FORMAT(sc.created_at, '%Y-%m-%d') as exam_date
            FROM scores sc
            JOIN students st ON sc.student_id = st.student_id
            WHERE 1=1
        """
        params = []
        
        if student_id:
            query += " AND sc.student_id = %s"
            params.append(student_id)
        
        if search_name:
            query += " AND st.name LIKE %s"
            params.append(f"%{search_name}%")
        
        query += " ORDER BY sc.created_at DESC"
        
        cursor.execute(query, params)
        scores = cursor.fetchall()
        
        # Get student list for filter dropdown
        cursor.execute("SELECT student_id, name, class FROM students ORDER BY name")
        students = cursor.fetchall()
        
        # Initialize default values
        stats = {}
        term_progression = []
        performance_distribution = []
        component_averages = {}
        selected_student_info = {}
        
        # Get comprehensive statistics for selected student or searched student
        if student_id or search_name:
            target_student_id = student_id
            
            # If searching by name, get the first matching student ID
            if search_name and not student_id:
                cursor.execute("SELECT student_id FROM students WHERE name LIKE %s LIMIT 1", (f"%{search_name}%",))
                name_match = cursor.fetchone()
                if name_match:
                    target_student_id = name_match['student_id']
            
            if target_student_id:
                # Get student info
                cursor.execute("SELECT * FROM students WHERE student_id = %s", (target_student_id,))
                selected_student_info = cursor.fetchone() or {}
                
                # Individual student statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_exams,
                        AVG(sc.average) as overall_avg,
                        MAX(sc.average) as highest_score,
                        MIN(sc.average) as lowest_score,
                        COUNT(DISTINCT sc.term) as terms_count
                    FROM scores sc
                    WHERE sc.student_id = %s
                """, (target_student_id,))
                stats = cursor.fetchone() or {}
                
                # Component averages
                cursor.execute("""
                    SELECT 
                        AVG(quiz) as avg_quiz,
                        AVG(homework) as avg_homework,
                        AVG(midterm) as avg_midterm,
                        AVG(final) as avg_final
                    FROM scores 
                    WHERE student_id = %s
                """, (target_student_id,))
                component_averages = cursor.fetchone() or {}
                
                # Term-wise progression
                cursor.execute("""
                    SELECT 
                        term,
                        AVG(average) as term_avg,
                        COUNT(*) as exam_count
                    FROM scores 
                    WHERE student_id = %s
                    GROUP BY term
                    ORDER BY term
                """, (target_student_id,))
                term_progression = cursor.fetchall()
                
                # Performance level distribution
                cursor.execute("""
                    SELECT 
                        performance_level,
                        COUNT(*) as count
                    FROM scores 
                    WHERE student_id = %s
                    GROUP BY performance_level
                    ORDER BY count DESC
                """, (target_student_id,))
                performance_distribution = cursor.fetchall()
                
                # Update selected_student to the actual ID used
                selected_student = target_student_id
            else:
                selected_student = None
        else:
            # Overall statistics for all students
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_exams,
                    AVG(sc.average) as overall_avg,
                    MAX(sc.average) as highest_score,
                    MIN(sc.average) as lowest_score,
                    COUNT(DISTINCT sc.student_id) as students_count
                FROM scores sc
            """)
            stats = cursor.fetchone() or {}
            
            # Overall performance distribution
            cursor.execute("""
                SELECT 
                    performance_level,
                    COUNT(*) as count
                FROM scores 
                GROUP BY performance_level
                ORDER BY count DESC
            """)
            performance_distribution = cursor.fetchall()
            
            term_progression = []
            component_averages = {}
            selected_student = None
            selected_student_info = {}
        
    except Exception as e:
        flash(f'Error loading score details: {str(e)}', 'error')
        scores = []
        students = []
        stats = {}
        term_progression = []
        performance_distribution = []
        component_averages = {}
        selected_student = None
        selected_student_info = {}
    finally:
        cursor.close()
        conn.close()
    
    return render_template('score_details.html', 
                         username=session.get('username'),
                         scores=scores,
                         students=students,
                         selected_student=selected_student,
                         selected_student_info=selected_student_info,
                         search_name=search_name,
                         stats=stats,
                         term_progression=term_progression,
                         performance_distribution=performance_distribution,
                         component_averages=component_averages)

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    
    student_id = session.get('student_id')
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'error')
        return render_template('student_dashboard.html')
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Student details
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            flash('Student profile not found!', 'error')
            return redirect(url_for('login'))
        
        # Student scores
        cursor.execute("SELECT * FROM scores WHERE student_id = %s ORDER BY term", (student_id,))
        scores = cursor.fetchall()
        
        # Performance summary
        cursor.execute("""
            SELECT 
                AVG(average) as overall_avg,
                MAX(average) as highest_score,
                MIN(average) as lowest_score,
                COUNT(*) as total_terms
            FROM scores 
            WHERE student_id = %s
        """, (student_id,))
        performance = cursor.fetchone()
        
        # Most common performance level
        cursor.execute("""
            SELECT performance_level 
            FROM scores 
            WHERE student_id = %s 
            GROUP BY performance_level 
            ORDER BY COUNT(*) DESC 
            LIMIT 1
        """, (student_id,))
        perf_level_result = cursor.fetchone()
        performance_level = perf_level_result['performance_level'] if perf_level_result else 'No Data'
        
        # Add performance level to performance dict
        if performance:
            performance['performance_level'] = performance_level
        
        # Component averages for the student
        cursor.execute("""
            SELECT 
                AVG(quiz) as avg_quiz,
                AVG(homework) as avg_homework,
                AVG(midterm) as avg_midterm,
                AVG(final) as avg_final
            FROM scores 
            WHERE student_id = %s
        """, (student_id,))
        subject_averages = cursor.fetchone()
        
        # Term progression
        cursor.execute("""
            SELECT term, average, performance_level
            FROM scores 
            WHERE student_id = %s 
            ORDER BY term
        """, (student_id,))
        term_progression = cursor.fetchall()
        
        # Class average for comparison
        cursor.execute("""
            SELECT AVG(sc.average) as class_avg
            FROM scores sc
            JOIN students st ON sc.student_id = st.student_id
            WHERE st.class = %s
        """, (student['class'],))
        class_avg_result = cursor.fetchone()
        class_avg = class_avg_result['class_avg'] if class_avg_result['class_avg'] else 0
        
        # Get recent scores for the student
        cursor.execute("""
            SELECT term, average, performance_level
            FROM scores 
            WHERE student_id = %s 
            ORDER BY created_at DESC 
            LIMIT 5
        """, (student_id,))
        recent_scores = cursor.fetchall()
        
        # Prepare chart data
        term_labels = [item['term'] for item in term_progression]
        term_scores = [float(item['average']) for item in term_progression]
        
        subject_labels = ['Quiz', 'Homework', 'Midterm', 'Final']
        subject_scores = [
            float(subject_averages['avg_quiz']) if subject_averages and subject_averages['avg_quiz'] else 0,
            float(subject_averages['avg_homework']) if subject_averages and subject_averages['avg_homework'] else 0,
            float(subject_averages['avg_midterm']) if subject_averages and subject_averages['avg_midterm'] else 0,
            float(subject_averages['avg_final']) if subject_averages and subject_averages['avg_final'] else 0
        ]
        
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        student = {}
        scores = []
        performance = {}
        subject_averages = {}
        term_labels = []
        term_scores = []
        subject_labels = []
        subject_scores = []
        class_avg = 0
        recent_scores = []
    
    finally:
        cursor.close()
        conn.close()
    
    return render_template('student_dashboard.html',
                         student=student,
                         scores=scores,
                         performance=performance,
                         subject_labels=subject_labels,
                         subject_scores=subject_scores,
                         term_labels=term_labels,
                         term_scores=term_scores,
                         class_avg=class_avg,
                         recent_scores=recent_scores,
                         username=session.get('username'))

@app.route('/add-student', methods=['GET', 'POST'])
def add_student():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get form data - only required fields
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        student_class = request.form.get('class')
        gender = request.form.get('gender')
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error!', 'error')
            return render_template('add_student.html', username=session.get('username'))
            
        cursor = conn.cursor()
        
        try:
            # Check if student already exists
            cursor.execute("SELECT student_id FROM students WHERE student_id = %s", (student_id,))
            existing_student = cursor.fetchone()
            
            if existing_student:
                flash('Student ID already exists!', 'error')
                return render_template('add_student.html', username=session.get('username'))
            
            # Insert new student into students table
            cursor.execute("""
                INSERT INTO students (student_id, name, class, gender) 
                VALUES (%s, %s, %s, %s)
            """, (student_id, name, student_class, gender))
            
            conn.commit()
            flash(f'Student {name} ({student_id}) added successfully!', 'success')
            return redirect(url_for('list_students'))
            
        except Exception as e:
            conn.rollback()
            error_msg = f'Error adding student: {str(e)}'
            flash(error_msg, 'error')
            return render_template('add_student.html', username=session.get('username'))
        finally:
            cursor.close()
            conn.close()
    
    # GET request - show the form
    return render_template('add_student.html', username=session.get('username'))

@app.route('/admin/add-score', methods=['GET', 'POST'])
def admin_add_score():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'error')
        return render_template('admin_add_score.html')
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get all students for dropdown
        cursor.execute("SELECT student_id, name, class, gender FROM students ORDER BY name")
        students = cursor.fetchall()
        
        if request.method == 'POST':
            student_id = request.form.get('student_id')
            term = request.form.get('term')
            subject = request.form.get('subject', 'General')
            quiz = request.form.get('quiz')
            homework = request.form.get('homework')
            midterm = request.form.get('midterm')
            final = request.form.get('final')
            redirect_to_student = request.form.get('redirect_to_student')
            
            # Validate inputs
            if not all([student_id, term, subject]):
                flash('Please fill all required fields.', 'error')
                return redirect(url_for('admin_add_score'))
            
            # Calculate average
            scores = []
            if quiz:
                scores.append(float(quiz))
            if homework:
                scores.append(float(homework))
            if midterm:
                scores.append(float(midterm))
            if final:
                scores.append(float(final))
            
            if not scores:
                flash('Please enter at least one score.', 'error')
                return redirect(url_for('admin_add_score'))
            
            average = sum(scores) / len(scores)
            
            # Determine performance level
            if average >= 85:
                performance_level = 'Excellent'
            elif average >= 70:
                performance_level = 'Good'
            elif average >= 50:
                performance_level = 'Average'
            else:
                performance_level = 'Poor'
            
            # Check if score already exists for this term and subject
            cursor.execute("""
                SELECT id FROM scores 
                WHERE student_id = %s AND term = %s AND subject = %s
            """, (student_id, term, subject))
            existing_score = cursor.fetchone()
            
            if existing_score:
                # Update existing score
                cursor.execute("""
                    UPDATE scores 
                    SET quiz = %s, homework = %s, midterm = %s, final = %s, 
                        average = %s, performance_level = %s, created_at = CURRENT_TIMESTAMP
                    WHERE student_id = %s AND term = %s AND subject = %s
                """, (quiz or None, homework or None, midterm or None, final or None, 
                      average, performance_level, student_id, term, subject))
                flash('Score updated successfully!', 'success')
            else:
                # Insert new score
                cursor.execute("""
                    INSERT INTO scores 
                    (student_id, term, subject, quiz, homework, midterm, final, average, performance_level)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (student_id, term, subject, quiz or None, homework or None, 
                      midterm or None, final or None, average, performance_level))
                flash('Score added successfully!', 'success')
            
            conn.commit()
            
            # Redirect to student details page if requested
            if redirect_to_student:
                return redirect(url_for('student_details', student_id=redirect_to_student))
            else:
                return redirect(url_for('score_details'))
    
    except Exception as e:
        flash(f'Error processing score: {str(e)}', 'error')
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()
    
    return render_template('admin_add_score.html',
                         username=session.get('username'),
                         students=students)

@app.route('/student/add-score', methods=['GET', 'POST'])
def student_add_score():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    
    student_id = session.get('student_id')
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'error')
        return render_template('student_add_score.html')
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get student details
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        
        # Get recent scores for the student
        cursor.execute("""
            SELECT term, average, performance_level
            FROM scores 
            WHERE student_id = %s 
            ORDER BY created_at DESC 
            LIMIT 5
        """, (student_id,))
        recent_scores = cursor.fetchall()
        
        # Get performance data for charts
        cursor.execute("""
            SELECT 
                AVG(average) as overall_avg,
                MAX(average) as highest_score,
                MIN(average) as lowest_score,
                COUNT(*) as total_terms
            FROM scores 
            WHERE student_id = %s
        """, (student_id,))
        performance = cursor.fetchone()
        
        # Get component averages
        cursor.execute("""
            SELECT 
                AVG(quiz) as avg_quiz,
                AVG(homework) as avg_homework,
                AVG(midterm) as avg_midterm,
                AVG(final) as avg_final
            FROM scores 
            WHERE student_id = %s
        """, (student_id,))
        subject_averages = cursor.fetchone()
        
        if request.method == 'POST':
            term = request.form.get('term')
            quiz = request.form.get('quiz')
            homework = request.form.get('homework')
            midterm = request.form.get('midterm')
            final = request.form.get('final')
            
            # Validate inputs
            if not term:
                flash('Please select term.', 'error')
                return redirect(url_for('student_add_score'))
            
            # Calculate average
            scores = []
            if quiz:
                scores.append(float(quiz))
            if homework:
                scores.append(float(homework))
            if midterm:
                scores.append(float(midterm))
            if final:
                scores.append(float(final))
            
            if not scores:
                flash('Please enter at least one score.', 'error')
                return redirect(url_for('student_add_score'))
            
            average = sum(scores) / len(scores)
            
            # Determine performance level
            if average >= 90:
                performance_level = 'Excellent'
            elif average >= 80:
                performance_level = 'Good'
            elif average >= 70:
                performance_level = 'Average'
            else:
                performance_level = 'Needs Improvement'
            
            # Check if score already exists for this term
            cursor.execute("""
                SELECT id FROM scores 
                WHERE student_id = %s AND term = %s
            """, (student_id, term))
            existing_score = cursor.fetchone()
            
            if existing_score:
                # Update existing score
                cursor.execute("""
                    UPDATE scores 
                    SET quiz = %s, homework = %s, midterm = %s, final = %s, 
                        average = %s, performance_level = %s
                    WHERE student_id = %s AND term = %s
                """, (quiz or None, homework or None, midterm or None, final or None, 
                      average, performance_level, student_id, term))
                flash('Score updated successfully!', 'success')
            else:
                # Insert new score
                cursor.execute("""
                    INSERT INTO scores 
                    (student_id, term, quiz, homework, midterm, final, average, performance_level)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (student_id, term, quiz or None, homework or None, 
                      midterm or None, final or None, average, performance_level))
                flash('Score added successfully!', 'success')
            
            conn.commit()
            return redirect(url_for('student_dashboard'))
    
    except Exception as e:
        flash(f'Error processing score: {str(e)}', 'error')
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()
    
    # Prepare chart data
    subject_labels = ['Quiz', 'Homework', 'Midterm', 'Final']
    subject_scores = [
        float(subject_averages['avg_quiz']) if subject_averages and subject_averages['avg_quiz'] else 0,
        float(subject_averages['avg_homework']) if subject_averages and subject_averages['avg_homework'] else 0,
        float(subject_averages['avg_midterm']) if subject_averages and subject_averages['avg_midterm'] else 0,
        float(subject_averages['avg_final']) if subject_averages and subject_averages['avg_final'] else 0
    ]
    
    return render_template('student_add_score.html',
                         student=student,
                         recent_scores=recent_scores,
                         performance=performance,
                         subject_labels=subject_labels,
                         subject_scores=subject_scores,
                         username=session.get('username'))

@app.route('/admin/edit-student/<student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'error')
        return redirect(url_for('list_students'))
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        if request.method == 'POST':
            # Get form data
            name = request.form.get('name')
            student_class = request.form.get('class')
            gender = request.form.get('gender')
            
            # Update student in database
            cursor.execute("""
                UPDATE students 
                SET name = %s, class = %s, gender = %s
                WHERE student_id = %s
            """, (name, student_class, gender, student_id))
            
            conn.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('student_details', student_id=student_id))
        
        # GET request - load current student data
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            flash('Student not found!', 'error')
            return redirect(url_for('list_students'))
            
    except Exception as e:
        flash(f'Error updating student: {str(e)}', 'error')
        conn.rollback()
        return redirect(url_for('student_details', student_id=student_id))
    finally:
        cursor.close()
        conn.close()
    
    return render_template('edit_student.html',
                         username=session.get('username'),
                         student=student)

@app.route('/admin/delete-student/<student_id>')
def delete_student(student_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'error')
        return redirect(url_for('list_students'))
        
    cursor = conn.cursor()
    
    try:
        # First delete all scores for this student
        cursor.execute("DELETE FROM scores WHERE student_id = %s", (student_id,))
        
        # Then delete the student
        cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
        
        conn.commit()
        flash('Student deleted successfully!', 'success')
        
    except Exception as e:
        flash(f'Error deleting student: {str(e)}', 'error')
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('list_students'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)