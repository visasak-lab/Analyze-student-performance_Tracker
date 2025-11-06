# Add these routes to the existing app.py

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