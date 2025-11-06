# Add these routes to the existing app.py

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