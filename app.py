from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Subject, Chapter, Quiz, Questions, Scores
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quizmaster.sqlite3"

db.init_app(app)

app.app_context().push() 

app.config['SECRET_KEY'] = 'ck0703907'

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    users = User.query.all()
    if request.method == 'POST':
        username = request.form.get('username').strip().lower()
        password = request.form.get('password')
        if username == 'admin123@gmail.com':
            if password == '1020304050':
                return redirect('/admin')
            else:
                return render_template('message1.html')
        
        user = User.query.filter_by(username = username).first()
        if user:
            if user.password == password:
                session['user_id'] = user.id
                return redirect('/user_dashboard')
            else:
                return render_template('message1.html')
        else:
            return render_template('message.html')
    return render_template('login.html')


@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        qualification = request.form.get('qualification')
        dob_str = request.form.get('dob')
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        new_user = User(username=username, password=password, name=name, qualification=qualification, dob=dob)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/')    
    return render_template('registration.html')


@app.route('/admin', methods = ['GET', 'POST'])
def admin():
    sub_obj_list = Subject.query.all()
    return render_template('admin_dashboard.html', sub_obj_list = sub_obj_list)  
    

@app.route('/subject', methods = ['GET', 'POST'])
def subject():
    if request.method == 'POST':
        sub_name = request.form.get('sub_name')
        descrip = request.form.get('descrip')
        action = request.form.get('action')
        if action == 'cancel':
            return redirect('/admin')
        if action == 'save':
            new_sub = Subject(name=sub_name, description=descrip)
            db.session.add(new_sub)
            db.session.commit()
        return redirect(f"/chapter/{new_sub.id}")
    return render_template('subject.html')


@app.route('/chapter/<int:subject_id>', methods = ['GET', 'POST'])
def chapter(subject_id):
    if request.method == 'POST':
        chapt_name = request.form.get('chapt_name')
        descrip = request.form.get('descrip')
        action = request.form.get('action')
        print(chapt_name, descrip)
        if action == 'cancel':
            return redirect('/admin')
        if action == 'save':
            new_chapt = Chapter(name=chapt_name, description=descrip, sub_id = subject_id)
            db.session.add(new_chapt)
            db.session.commit()
            return redirect('/admin')
    return render_template('chapter.html', subject_id=subject_id)


@app.route('/quiz_management', methods = ['POST', 'GET'])
def quiz_management():
    quiz_to_chapter = {}
    quizzes = Quiz.query.all()
    question_objs = Questions.query.all()
    quiz_questions = {quiz.id: quiz.questions for quiz in quizzes}
    for quiz in quizzes:
        chapter_obj = Chapter.query.filter_by(id = quiz.chapter_id).first()
        quiz_to_chapter[quiz.id] = chapter_obj.name
    return render_template('quiz_management.html', quizzes=quizzes, quiz_questions=quiz_questions, quiz_to_chapter = quiz_to_chapter)


@app.route('/add_quiz', methods = ['GET', 'POST'])
def add_quiz():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'cancel':
            return redirect('/quiz_management')
        if action == 'save':
            chapter_id = request.form.get('chapter_id')
            date = request.form.get('exam_date')
            date_of_quiz = datetime.strptime(date, '%Y-%m-%d').date()
            duration = request.form.get('duration')
            time_duration = datetime.strptime(duration, '%H:%M').time()
            quiz_attempted = 0
            new_quiz = Quiz(chapter_id = chapter_id, date_of_quiz = date_of_quiz, time_duration = time_duration, quiz_attempted = quiz_attempted)
            db.session.add(new_quiz)
            db.session.commit()
        return redirect(f'/add_question/{new_quiz.id}') 
    return render_template('add_quiz.html')


@app.route('/add_question/<int:quiz_id>', methods = ['GET', 'POST'])
def add_question(quiz_id):
    quiz_obj = Quiz.query.get(quiz_id)
    chapter_id = quiz_obj.chapter_id
    if request.method == 'POST':
        question_title = request.form.get('question_title')
        question_statement = request.form.get('question_statement')
        option_1 = request.form.get('option_1')
        option_2 = request.form.get('option_2')
        option_3 = request.form.get('option_3')
        option_4 = request.form.get('option_4')
        correct_opt = request.form.get('correct_option')
        new_quest = Questions(quiz_id = quiz_id, chapter_id = chapter_id, question_title = question_title, 
                              question_statement = question_statement, 
                              option_1 = option_1, option_2 = option_2, 
                              option_3 = option_3, option_4 = option_4, 
                              correct_option = correct_opt)
        db.session.add(new_quest)
        db.session.commit()
        return redirect('/quiz_management')
    return render_template('add_question.html', quiz_id = quiz_id)


@app.route('/user_dashboard')
def user_dashboard():
    quizzes = Quiz.query.all()
    user_id = session.get('user_id')
    user_obj = User.query.get(user_id)
    for quiz in quizzes:
        score = Scores.query.filter_by(user_id=user_id, quiz_id=quiz.id).first()
        if not score:
            quiz.quiz_attempted = 0
            db.session.commit()  
        else:
            quiz.quiz_attempted = 1
            db.session.commit()  

    return render_template('user_dashboard.html', quizzes = quizzes, user_obj = user_obj)


@app.route('/view/<int:quiz_id>')
def view(quiz_id):
    user_id = session.get('user_id')
    user_obj = User.query.get(user_id)
    quiz = Quiz.query.filter_by(id = quiz_id).first()
    chapter_id = quiz.chapter_id 
    chapter_obj = Chapter.query.filter_by(id = chapter_id).first()
    chapter_name = chapter_obj.name
    sub_id = chapter_obj.sub_id
    sub_obj = Subject.query.filter_by(id = sub_id).first()
    sub_name = sub_obj.name
    return render_template('view.html', quiz = quiz, chapter_name = chapter_name, sub_name = sub_name, user_obj = user_obj)


@app.route('/start_Exam/<int:quiz_id>')
def start_Exam(quiz_id):
    quiz = Quiz.query.filter_by(id = quiz_id).first()
    questions = quiz.questions
    chapter_id = quiz.chapter_id 
    chapter_obj = Chapter.query.filter_by(id = chapter_id).first()
    chapter_name = chapter_obj.name
    sub_id = chapter_obj.sub_id
    sub_obj = Subject.query.filter_by(id = sub_id).first()
    sub_name = sub_obj.name
    return render_template('start_Exam.html', questions = questions, chapter_name = chapter_name, sub_name = sub_name, quiz_id = quiz.id)


@app.route('/edit_question/<int:question_id>', methods = ['GET', 'POST'])
def edit(question_id):
    question_obj = Questions.query.filter_by(id = question_id).first()
    quiz_id = question_obj.quiz_id
    quiz_obj = Quiz.query.filter_by(id = quiz_id).first()
    chapter_id = quiz_obj.chapter_id
    if request.method == 'POST':
        question_obj.question_title = request.form.get('question_title')
        question_obj.question_statement = request.form.get('question_statement')
        question_obj.option_1 = request.form.get('option_1')
        question_obj.option_2 = request.form.get('option_2')
        question_obj.option_3 = request.form.get('option_3')
        question_obj.option_4 = request.form.get('option_4')
        question_obj.correct_option = request.form.get('correct_option')
        db.session.commit()
        return redirect('/quiz_management')
    return render_template('edit_question.html', chapter_id = chapter_id, question = question_obj)


@app.route('/delete_question/<int:question_id>')
def delete(question_id):
    question_obj = Questions.query.filter_by(id = question_id).first()
    db.session.delete(question_obj)
    db.session.commit()
    return redirect('/quiz_management')


@app.route('/submit/<int:quiz_id>', methods = ['GET', 'POST'])
def submit(quiz_id):
    quiz_obj = Quiz.query.filter_by(id = quiz_id).first()
    user_id = session.get('user_id')
    quiz_obj.quiz_attempted = 1
    score_obj = Scores.query.filter_by(user_id = user_id, quiz_id = quiz_obj.id).first()
    questions = quiz_obj.questions
    total_scored = 0
    if request.method == 'POST':
        for question in questions:
            answer = request.form.get(f"question_{question.id}")
            if answer == question.correct_option:
                total_scored+=1
        if total_scored < 5:
            remarks = "Work a little harder"
        else:
            remarks = "Good going"
        submission_time = request.form.get('submit_time')  
        if submission_time:
            time_stamp_of_attempt = datetime.fromisoformat(submission_time)
        else:
            time_stamp_of_attempt = datetime.now()
        if score_obj:
            score_obj.quiz_id = quiz_obj.id
            score_obj.time_stamp_of_attempt = time_stamp_of_attempt
            score_obj.total_scored = total_scored
            score_obj.remarks = remarks 
            db.session.commit()
        else:
            score_obj = Scores(quiz_id = quiz_obj.id, user_id = user_id, time_stamp_of_attempt = time_stamp_of_attempt, total_scored = total_scored, remarks = remarks)
            db.session.add(score_obj)
            db.session.commit()
        return redirect('/user_dashboard')


@app.route('/edit_chapter/<int:chapter_id>', methods = ['GET', 'POST'])
def edit_chapter(chapter_id):
    chapt_obj = Chapter.query.get(chapter_id)
    if request.method == 'POST':
        action = request.form.get('action')
        print(action)
        if action == 'cancel':
            return redirect('/admin')
        elif action == 'save':
            chapt_obj.name = request.form.get('chapt_name')
            chapt_obj.description = request.form.get('descrip')
            db.session.commit()
            return redirect('/admin')
    return render_template('edit_chapt.html', chapt_obj = chapt_obj)


@app.route('/delete_chapter/<int:chapter_id>')
def delete_chapter(chapter_id):
    chapt_obj = Chapter.query.get(chapter_id)
    question_objs = chapt_obj.chapt_questions 
    quiz_objs = chapt_obj.quizzes
    for quiz in quiz_objs:
        question_objs = quiz.questions
        for question in question_objs:
            db.session.delete(question)
        db.session.delete(quiz)
    db.session.delete(chapt_obj)
    db.session.commit()
    return redirect('/admin')

@app.route('/edit_quiz/<int:quiz_id>', methods = ['GET', 'POST'])
def edit_quiz(quiz_id):
    quiz_obj = Quiz.query.get(quiz_id)
    if request.method == "POST":
        action = request.form.get('action')
        if action == 'save':
            quiz_obj.chapter_id = request.form.get('chapter_id')
            date = request.form.get('exam_date')
            date_of_quiz = datetime.strptime(date, '%Y-%m-%d').date()
            quiz_obj.date_of_quiz = date_of_quiz
            duration = request.form.get('duration')
            time_duration = datetime.strptime(duration[:5], '%H:%M').time()
            quiz_obj.time_duration = time_duration
            db.session.commit()
            return redirect('/quiz_management')
        if action == 'cancel':
            return redirect('/quiz_management')
    return render_template('edit_quiz.html', quiz_obj = quiz_obj)


@app.route('/delete_quiz/<int:quiz_id>')
def delete_quiz(quiz_id):
    quiz_obj = Quiz.query.get(quiz_id)
    question_objs = quiz_obj.questions
    for question in question_objs:
        db.session.delete(question)
    db.session.delete(quiz_obj)
    db.session.commit()
    return redirect('/quiz_management')

@app.route('/edit_subject/<int:subject_id>', methods = ['GET', 'POST'])
def edit_subject(subject_id):
    subject_obj = Subject.query.get(subject_id)
    if request.method == "POST":
        action = request.form.get('action')
        if action == 'cancel':
            return redirect('/admin')
        elif action == 'save':
            subject_obj.name = request.form.get('sub_name')
            subject_obj.description = request.form.get('descrip')
            db.session.commit()
            return redirect('/admin')
    return render_template('edit_subject.html', subject_obj = subject_obj)

@app.route('/delete_subject/<int:subject_id>')
def delete_subject(subject_id):
    subject_obj = Subject.query.get(subject_id)
    chapter_objs = subject_obj.chapters
    for chapter in chapter_objs:
        quiz_objs = chapter.quizzes
        for quiz in quiz_objs:
            question_objs = quiz.questions 
            for question in question_objs:
                db.session.delete(question)
            db.session.delete(quiz)
        db.session.delete(chapter)
    db.session.delete(subject_obj)
    db.session.commit()
    return redirect('/admin')
@app.route('/scores')
def scores():
    quizzes = Quiz.query.all()
    user_id = session.get('user_id')
    user_obj = User.query.get(user_id)
    user_scores = Scores.query.filter_by(user_id = user_id).all()
    score_dict = {}
    for score in user_scores:
        l = [] 
        if score.total_scored <= 5:
            remarks = 'Work a little harder!!'
            l.append(score.total_scored)
            l.append(remarks)
        elif score.total_scored >5:
            remarks = 'Good Going!!'
            l.append(score.total_scored)
            l.append(remarks)
        score_dict[score.quiz_id] = l
    return render_template('scores.html', quizzes = quizzes, score_dict = score_dict, user_obj = user_obj)


@app.route('/summary_user')
def summary():
    # For bar chart
    user_id = session.get('user_id')
    user_obj = User.query.get(user_id)
    sub_objs = Subject.query.all()
    subject_counts = []
    for sub in sub_objs:
        sub_count = {} 
        count = 0
        chapt_objs = sub.chapters 
        for chapt in chapt_objs:
                quiz_objs = chapt.quizzes
                for quiz in quiz_objs:
                    score_obj = Scores.query.filter_by(quiz_id = quiz.id, user_id = user_id).first()
                    if score_obj:
                        count += 1
                if sub.name not in sub_count:
                    sub_count['subject'] = sub.name 
                    sub_count['count'] = count
        subject_counts.append(sub_count)
    print(subject_counts)
    
    #For pie chart
    month_dict = {"01": "Jan", "02":"Feb", "03":"Mar", "04":"Apr", 
                  "05":"May", "06":"June", "07":"July", "08":"Aug", 
                  "09":"Sept", "10":"Oct", "11":"Nov", "12":"Dec"}
    month_attempts = []
    month_attempts_dict = {}

    for quiz in Quiz.query.all():
    # Extracting the month part from the quiz date
       month_key = str(quiz.date_of_quiz)[5:7]
    
    # Initialising the entry for this month if it doesn't exist.
       if month_key not in month_attempts_dict:
           month_attempts_dict[month_key] = {"month": month_dict[month_key], "count": 0}
    
    # Checking if the user has a score for this quiz.
       score = Scores.query.filter_by(quiz_id=quiz.id, user_id=user_id).first()
       if score:
           month_attempts_dict[month_key]["count"] += 1
    month_attempts = list(month_attempts_dict.values())
    return render_template('summary_user.html', subject_counts=subject_counts, month_attempts=month_attempts, user_obj = user_obj)


@app.route("/logout")
def logout():
    session.clear()  
    return redirect('/login')

@app.route('/search_admin')
def search():
    search_word = request.args.get('search').strip()
    key = request.args.get('key').strip()
    if key == 'user':
        user_objs = User.query.filter_by(name = search_word).all()
        return render_template('search_admin.html', user_objs = user_objs, key = key)
    elif key == 'subject':
        sub = Subject.query.filter_by(name = search_word).first()
        return render_template('search_admin.html', sub = sub, key = key)
    elif key == 'quiz':
        quizzes = Quiz.query.all()
        return render_template('search_admin.html', quizzes = quizzes, key = key)

@app.route('/summary_admin')
def summary_admin():
    #Subject-wise top scores
    user_id = session.get('user_id')
    subject_scores = []
    for sub in Subject.query.all():
        max_marks_list_across_chapters = []
        subject_score_dict = {}
        for chapt in sub.chapters:
            allquizzes_marks = []
            for quiz in chapt.quizzes:
                score_obj_list = Scores.query.filter_by(quiz_id = quiz.id).all()
                for score in score_obj_list:
                    allquizzes_marks.append(score.total_scored)
            if allquizzes_marks != []:
                max_marks_list_across_chapters.append(max(allquizzes_marks))
        if max_marks_list_across_chapters != []:
             subject_score_dict['subject'] = sub.name
             subject_score_dict['score'] = int(sum(max_marks_list_across_chapters)/len(max_marks_list_across_chapters))
        subject_scores.append(subject_score_dict)

    #Subject-wise users attempt   
    subject_attempts = []
    for sub in Subject.query.all():
        attempts = 0 
        subject_attempts_dict = {}
        for chapt in sub.chapters:
            quizzes_attempts = []
            for quiz in chapt.quizzes:
                score_obj_list = Scores.query.filter_by(quiz_id = quiz.id).all()
                quizzes_attempts.append(len(score_obj_list))
            if quizzes_attempts != []:
                attempts = max(quizzes_attempts)
        subject_attempts_dict['subject'] = sub.name 
        subject_attempts_dict['attempts'] = attempts 
        subject_attempts.append(subject_attempts_dict) 
    return render_template(
        'summary_admin.html',  
        subject_scores=subject_scores,
        subject_attempts=subject_attempts
    )


app.run(debug=True)
