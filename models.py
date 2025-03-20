from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), nullable = False, unique = True)
    password = db.Column(db.String(100), nullable = False)
    name = db.Column(db.String(100), nullable = False)
    qualification = db.Column(db.String(120))
    dob = db.Column(db.Date, nullable = False)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), nullable = False, unique = True)
    description = db.Column(db.String(120))
    chapters = db.relationship('Chapter', backref='subject')

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), nullable = False, unique = True)
    description = db.Column(db.String(120))
    sub_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable = False)
    quizzes = db.Relationship('Quiz', backref = 'chapter')
    chapt_questions = db.Relationship('Questions', backref = 'chapter')

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable = False)
    date_of_quiz = db.Column(db.Date, nullable = False)
    time_duration = db.Column(db.Time, nullable = False)
    quiz_attempted = db.Column(db.Integer())
    questions = db.Relationship('Questions', backref = 'quiz')

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable = False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable = False)
    question_title = db.Column(db.Text, nullable = False)
    question_statement = db.Column(db.Text, nullable = False)
    option_1 = db.Column(db.String(120), nullable = False)
    option_2 = db.Column(db.String(120), nullable = False)
    option_3 = db.Column(db.String(120), nullable = False)
    option_4 = db.Column(db.String(120), nullable = False)
    correct_option = db.Column(db.String(120), nullable = False)

class Scores(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    time_stamp_of_attempt = db.Column(db.DateTime, nullable = False)
    total_scored = db.Column(db.Integer, nullable = False)
    remarks = db.Column(db.String(120))



    