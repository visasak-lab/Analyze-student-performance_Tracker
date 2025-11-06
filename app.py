# Add these routes to the existing app.py from branch 2

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
        
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        total_students = total_scores = overall_avg = 0
        performance_counts = {'Excellent': 0, 'Good': 0, 'Average': 0, 'Poor': 0}
        recent_activities = []
        class_labels = class_scores = original_class_student_counts = term_labels = term_scores = term_counts = []
        subject_labels = subject_scores = gender_labels = gender_scores = gender_counts = []
        top_students = []
        students_no_scores = []
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
                         students_no_scores=students_no_scores)

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