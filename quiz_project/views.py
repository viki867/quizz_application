from django.shortcuts import render, redirect
import mysql.connector as mys
import csv
import io 

# ---------------- MySQL Connection ----------------
def get_db_connection():
    conn = mys.connect(
        host="localhost",
        user="root",
        password="root",  # change this
        database="quiz_db",
        charset="utf8mb4",
        collation="utf8mb4_unicode_ci"
    )
    return conn

# ---------------- Home Page ----------------
def index(request):
    return render(request, 'index.html')

# ---------------- User Signup ----------------
def signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'signup.html', {"error": "Passwords do not match."})

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)", (name, email, password))
        conn.commit()
        cursor.close(); conn.close()
        return redirect('user_login')
    return render(request, 'signup.html')

# ---------------- User Login ----------------
def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        cursor.close(); conn.close()

        if user:
            request.session['user_name'] = user['name']
            request.session['user_id'] = user['id']
            return redirect('user_dashboard')
        else:
            return render(request, 'login.html', {"error": "Invalid credentials."})

    return render(request, 'login.html')

# ---------------- Admin Login ----------------
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
        admin = cursor.fetchone()
        cursor.close(); conn.close()

        if admin:
            request.session['admin'] = True
            return redirect('admin_dashboard')
        else:
            return render(request, 'admin_login.html', {"error": "Invalid credentials."})

    return render(request, 'admin_login.html')

# ---------------- Logout ----------------
def user_logout(request):
    request.session.flush()
    return redirect('index')

# ---------------- User Dashboard ----------------
def user_dashboard(request):
    if 'user_name' not in request.session:
        return redirect('user_login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    cursor.close(); conn.close()

    return render(request, 'user_dashboard.html', {'user_name': request.session['user_name'], 'categories': categories})

# ---------------- Category Quizzes ----------------
def category_quiz(request, category_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories WHERE id=%s", (category_id,))
    category = cursor.fetchone()
    cursor.execute("SELECT * FROM quizzes WHERE category_id=%s", (category_id,))
    quizzes = cursor.fetchall()
    cursor.close(); conn.close()

    return render(request, 'category.html', {'category': category, 'quizzes': quizzes})

# ---------------- Start Quiz ----------------

# ---------------- Quiz Result ----------------
def quiz_result(request, quiz_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT score FROM scores WHERE quiz_id=%s AND user_id=%s ORDER BY id DESC LIMIT 1",
                   (quiz_id, request.session['user_id']))
    score_row = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) as total FROM questions WHERE quiz_id=%s", (quiz_id,))
    total_row = cursor.fetchone()
    cursor.close(); conn.close()

  
    review_data = request.session.get('quiz_review', [])
    

    if 'quiz_review' in request.session:
        del request.session['quiz_review']
        request.session.save()

    return render(request, 'result.html', {
        'score': score_row['score'] if score_row else 0, 
        'total_questions': total_row['total'] if total_row else 0,
        'review_data': review_data
    })

# ---------------- Admin Dashboard ----------------
def admin_dashboard(request):
    if 'admin' not in request.session:
        return redirect('admin_login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    cursor.execute("SELECT COUNT(*) as total FROM users")
    user_count = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM quizzes")
    quiz_count = cursor.fetchone()['total']

  
    cursor.execute("SELECT COUNT(*) as total FROM categories")
    category_count = cursor.fetchone()['total']


    cursor.execute("SELECT COUNT(*) as total FROM users WHERE DATE(registration_date) = CURDATE()")
    today_users_count = cursor.fetchone()['total']
    
    cursor.close()
    conn.close()

    context = {
        'user_count': user_count,
        'quiz_count': quiz_count,
        'category_count': category_count,
        'today_users_count': today_users_count,
    }

    return render(request, 'admin_dashboard.html', context)

# ---------------- Add Category ----------------
def add_category(request):
    if 'admin' not in request.session:
        return redirect('admin_login')
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (name, description) VALUES (%s,%s)", (name, description))
        conn.commit()
        cursor.close(); conn.close()
        return redirect('admin_dashboard')
    return render(request, 'add_category.html')

# ---------------- Add Quiz ----------------
def add_quiz(request):
    if 'admin' not in request.session:
        return redirect('admin_login')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == "POST":
        title = request.POST.get('title')
        category_id = request.POST.get('category_id')
       
        time_limit = request.POST.get('time_limit')

        
        cursor.execute("INSERT INTO quizzes (title, category_id, time_limit_minutes) VALUES (%s,%s,%s)", (title, category_id, time_limit))
        conn.commit()
        cursor.close(); conn.close()
        return redirect('admin_dashboard')

    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    cursor.close(); conn.close()
    return render(request, 'add_quiz.html', {'categories': categories})
# ---------------- Add Question ----------------
def add_question(request, quiz_id):
    if 'admin' not in request.session:
        return redirect('admin_login')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM quizzes WHERE id=%s", (quiz_id,))
    quiz = cursor.fetchone()
    if request.method == "POST":
        question_text = request.POST.get('question_text')
        option1 = request.POST.get('option1')
        option2 = request.POST.get('option2')
        option3 = request.POST.get('option3')
        option4 = request.POST.get('option4')
        answer = request.POST.get('answer')
        cursor.execute(
            "INSERT INTO questions (quiz_id, question_text, option1, option2, option3, option4, answer) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (quiz_id, question_text, option1, option2, option3, option4, answer))
        conn.commit()
        cursor.close(); conn.close()
        return redirect('admin_dashboard')
    cursor.close(); conn.close()
    return render(request, 'add_question.html', {'quiz': quiz})

# ---------------- View Users ----------------
def view_users(request):
    if 'admin' not in request.session:
        return redirect('admin_login')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close(); conn.close()
    return render(request, 'view_users.html', {'users': users})

# ---------------- View Scores ----------------
def view_scores(request):
    if 'admin' not in request.session:
        return redirect('admin_login')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id, u.name as user_name, q.title as quiz_title, s.score
        FROM scores s
        JOIN users u ON s.user_id = u.id
        JOIN quizzes q ON s.quiz_id = q.id
        ORDER BY s.id DESC
    """)
    scores = cursor.fetchall()
    cursor.close(); conn.close()
    return render(request, 'view_scores.html', {'scores': scores})

def view_quizzes(request):
    if 'admin' not in request.session:
        return redirect('admin_login')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM quizzes")
    quizzes = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render(request, 'view_quizzes.html', {'quizzes': quizzes})
    


def start_quiz(request, quiz_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
      
        cursor.execute("SELECT * FROM questions WHERE quiz_id=%s", (quiz_id,))
        questions = cursor.fetchall()
        
        score = 0
        review_data = []

        for q in questions:
            user_ans = request.POST.get(f"q{q['id']}")
            is_correct = (user_ans == q['answer'])
            if is_correct:
                score += 1
            review_data.append({
                'question_text': q['question_text'],
                'user_answer': user_ans if user_ans else "Not Answered",
                'correct_answer': q['answer'],
                'is_correct': is_correct
            })
        
      
        cursor.execute("INSERT INTO scores (user_id, quiz_id, score) VALUES (%s,%s,%s)",
                       (request.session['user_id'], quiz_id, score))
        conn.commit()
        
     
        request.session['quiz_review'] = review_data
        request.session.save() 

        cursor.close()
        conn.close()
        return redirect('quiz_result', quiz_id=quiz_id)

   
    cursor.execute("SELECT * FROM quizzes WHERE id=%s", (quiz_id,))
    quiz = cursor.fetchone()
    cursor.execute("SELECT * FROM questions WHERE quiz_id=%s", (quiz_id,))
    questions = cursor.fetchall()
    cursor.close()
    conn.close()
    return render(request, 'quiz.html', {'quiz': quiz, 'questions': questions})



def user_profile(request):
    if 'user_id' not in request.session:
        return redirect('user_login')

    user_id = request.session['user_id']
    user_name = request.session['user_name']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

   
    query = """
        SELECT q.title, s.score, s.taken_on
        FROM scores s
        JOIN quizzes q ON s.quiz_id = q.id
        WHERE s.user_id = %s
        ORDER BY s.taken_on DESC
    """
    cursor.execute(query, (user_id,))
    scores_history = cursor.fetchall()
    
    cursor.close()
    conn.close()

    context = {
        'user_name': user_name,
        'scores': scores_history
    }

    return render(request, 'profile.html', context)
    
    
def manage_categories(request):
    if 'admin' not in request.session:
        return redirect('admin_login')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories ORDER BY id DESC")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render(request, 'manage_categories.html', {'categories': categories})    
    
def edit_category(request, category_id):
    if 'admin' not in request.session:
        return redirect('admin_login')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        cursor.execute("UPDATE categories SET name=%s, description=%s WHERE id=%s", (name, description, category_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('manage_categories')

    cursor.execute("SELECT * FROM categories WHERE id=%s", (category_id,))
    category = cursor.fetchone()
    cursor.close()
    conn.close()
    return render(request, 'edit_category.html', {'category': category})    
    
def delete_category(request, category_id):
    if 'admin' not in request.session:
        return redirect('admin_login')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE id=%s", (category_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('manage_categories')    
    
def edit_quiz(request, quiz_id):
    if 'admin' not in request.session:
        return redirect('admin_login')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category_id')
        time_limit = request.POST.get('time_limit')
        cursor.execute("UPDATE quizzes SET title=%s, category_id=%s, time_limit_minutes=%s WHERE id=%s", (title, category_id, time_limit, quiz_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('view_quizzes')

    cursor.execute("SELECT * FROM quizzes WHERE id=%s", (quiz_id,))
    quiz = cursor.fetchone()
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return render(request, 'edit_quiz.html', {'quiz': quiz, 'categories': categories})

# ---------------- Delete Quiz ----------------
def delete_quiz(request, quiz_id):
    if 'admin' not in request.session:
        return redirect('admin_login')
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
       
        cursor.execute("DELETE FROM scores WHERE quiz_id=%s", (quiz_id,))
        
       
        cursor.execute("DELETE FROM questions WHERE quiz_id=%s", (quiz_id,))
        
      
        cursor.execute("DELETE FROM quizzes WHERE id=%s", (quiz_id,))
        
        conn.commit()
    except Exception as e:
        
        conn.rollback()
        print(f"Error deleting quiz: {e}") 
    finally:
     
        cursor.close()
        conn.close()
        
    return redirect('view_quizzes')    
    
def upload_questions(request, quiz_id):
    if 'admin' not in request.session:
        return redirect('admin_login')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            cursor.execute("SELECT * FROM quizzes WHERE id=%s", (quiz_id,))
            quiz = cursor.fetchone()
            cursor.close(); conn.close()
            return render(request, 'upload_questions.html', {'quiz': quiz, 'error': 'Please upload a valid .csv file.'})

        try:
           
            file_content = csv_file.read()
            decoded_file = None
        
            encodings_to_try = ['utf-8', 'utf-8-sig', 'cp1252']

            for encoding in encodings_to_try:
                try:
                    #
                    decoded_file = file_content.decode(encoding)
                    print(f"Successfully decoded with {encoding}")
                    break  
                except UnicodeDecodeError:
                    print(f"Failed to decode with {encoding}")
                    continue 
            
           
            if decoded_file is None:
                raise ValueError("Could not decode the file. Please save it as UTF-8.")

            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string)
            
            questions_to_insert = []
            for row in reader:
                if len(row) == 6:
                    questions_to_insert.append((quiz_id, row[0], row[1], row[2], row[3], row[4], row[5]))

            if questions_to_insert:
                sql = "INSERT INTO questions (quiz_id, question_text, option1, option2, option3, option4, answer) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.executemany(sql, questions_to_insert)
                conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"Error during CSV upload: {e}")
            cursor.execute("SELECT * FROM quizzes WHERE id=%s", (quiz_id,))
            quiz = cursor.fetchone()
            cursor.close(); conn.close()
           
            error_message = str(e) if isinstance(e, ValueError) else 'An error occurred while processing the file.'
            return render(request, 'upload_questions.html', {'quiz': quiz, 'error': error_message})

        cursor.close(); conn.close()
        return redirect('view_quizzes')

    cursor.execute("SELECT * FROM quizzes WHERE id=%s", (quiz_id,))
    quiz = cursor.fetchone()
    cursor.close(); conn.close()
    return render(request, 'upload_questions.html', {'quiz': quiz})
    
def analytics_dashboard(request):
    if 'admin' not in request.session:
        return redirect('admin_login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    

    cursor.execute("""
        SELECT q.title, COUNT(s.quiz_id) as attempts
        FROM scores s
        JOIN quizzes q ON s.quiz_id = q.id
        GROUP BY s.quiz_id
        ORDER BY attempts DESC
        LIMIT 5
    """)
    popular_quizzes = cursor.fetchall()

    cursor.execute("""
        SELECT u.name as user_name, q.title as quiz_title, s.score
        FROM scores s
        JOIN users u ON s.user_id = u.id
        JOIN quizzes q ON s.quiz_id = q.id
        ORDER BY s.score DESC
        LIMIT 5
    """)
    top_scores = cursor.fetchall()

    
    cursor.execute("""
        SELECT q.title, AVG(s.score) as avg_score, COUNT(s.quiz_id) as attempts
        FROM scores s
        JOIN quizzes q ON s.quiz_id = q.id
        GROUP BY s.quiz_id
        ORDER BY avg_score ASC
        LIMIT 5
    """)
    hardest_quizzes = cursor.fetchall()

    cursor.execute("""
        SELECT u.name, COUNT(s.user_id) as quizzes_taken
        FROM scores s
        JOIN users u ON s.user_id = u.id
        GROUP BY s.user_id
        ORDER BY quizzes_taken DESC
        LIMIT 5
    """)
    active_users = cursor.fetchall()

    cursor.close()
    conn.close()

    context = {
        'popular_quizzes': popular_quizzes,
        'top_scores': top_scores,
        'hardest_quizzes': hardest_quizzes,
        'active_users': active_users,
    }

    return render(request, 'analytics_dashboard.html', context)    
    