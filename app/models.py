from datetime import datetime, timezone
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    school_name = db.Column(db.String(150), nullable=False)
    grade = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    otp = db.Column(db.String(6), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    points = db.Column(db.Integer, default=0)
    submissions = db.relationship('Submission', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.full_name}', '{self.email}')"

class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    statement = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    end_time = db.Column(db.DateTime, nullable=True)
    scheduled_for = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=False)
    submissions = db.relationship('Submission', backref='problem', lazy=True)

    def __repr__(self):
        return f"Problem('{self.title}', Active: '{self.is_active}')"

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
    answer = db.Column(db.String(200), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    submission_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"Submission('{self.user_id}', '{self.problem_id}', Correct: '{self.is_correct}')"
