# Add these routes to the existing app.py

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

@app.route('/add-student', methods=['GET', 'POST'])
def add_student():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get all form data
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        student_class = request.form.get('class')
        gender = request.form.get('gender')
        email = request.form.get('email')
        
        # Score data
        term = request.form.get('term')
        quiz = request.form.get('quiz')
        homework = request.form.get('homework')
        midterm = request.form.get('midterm')
        final = request.form.get('final')
        average = request.form.get('average')
        performance_level = request.form.get('performance_level')
        
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
            
            # Insert score data if provided
            if term and (quiz or homework or midterm or final):
                # Use calculated average if provided, otherwise calculate it
                if not average:
                    scores = []
                    if quiz: scores.append(float(quiz))
                    if homework: scores.append(float(homework))
                    if midterm: scores.append(float(midterm))
                    if final: scores.append(float(final))
                    if scores:
                        average = sum(scores) / len(scores)
                
                # Determine performance level if not provided
                if not performance_level and average:
                    avg_float = float(average)
                    if avg_float >= 85:
                        performance_level = 'Excellent'
                    elif avg_float >= 70:
                        performance_level = 'Good'
                    elif avg_float >= 50:
                        performance_level = 'Average'
                    else:
                        performance_level = 'Poor'
                
                cursor.execute("""
                    INSERT INTO scores 
                    (student_id, term, quiz, homework, midterm, final, average, performance_level)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    student_id, term, 
                    float(quiz) if quiz else None,
                    float(homework) if homework else None,
                    float(midterm) if midterm else None,
                    float(final) if final else None,
                    float(average) if average else None,
                    performance_level
                ))
            
            # Create user account if email is provided
            if email:
                # Check if user already exists
                cursor.execute("SELECT id FROM users WHERE student_id = %s", (student_id,))
                existing_user = cursor.fetchone()
                
                if not existing_user:
                    # Create a default password
                    default_password = 'student123'
                    cursor.execute("""
                        INSERT INTO users (username, password, role, student_id, email) 
                        VALUES (%s, %s, 'student', %s, %s)
                    """, (student_id, default_password, student_id, email))
            
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