from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User, Problem, Submission
from app.utils import generate_otp, send_otp_email
import re
from datetime import datetime, timezone

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        school = request.form.get('school')
        grade = request.form.get('grade')
        password = request.form.get('password')
        
        # Simple email validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email address.', 'danger')
            return redirect(url_for('main.register'))
            
        user = User.query.filter_by(email=email).first()
        if user:
            if user.is_verified:
                flash('Email already registered. Please login.', 'danger')
                return redirect(url_for('main.login'))
            else:
                # Resend OTP for unverified existing user
                otp = generate_otp()
                user.otp = otp
                # update password and details if they tried to register again
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                user.password_hash = hashed_password
                user.full_name = full_name
                user.phone_number = phone
                user.school_name = school
                user.grade = grade
                db.session.commit()
                send_otp_email(user.email, otp)
                session['verification_email'] = user.email
                flash('Email already registered but not verified. A new OTP has been sent.', 'info')
                return redirect(url_for('main.verify'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        otp = generate_otp()
        
        import os
        is_admin = (email.lower() == os.environ.get('ADMIN_EMAIL', '').lower())
        
        new_user = User(
            full_name=full_name,
            email=email,
            phone_number=phone,
            school_name=school,
            grade=grade,
            password_hash=hashed_password,
            otp=otp,
            is_admin=is_admin
        )
        db.session.add(new_user)
        db.session.commit()
        
        send_otp_email(email, otp)
        session['verification_email'] = email
        
        flash('Account created! Please check your email for the OTP.', 'success')
        return redirect(url_for('main.verify'))
        
    return render_template('register.html')

@main.route('/verify', methods=['GET', 'POST'])
def verify():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    email = session.get('verification_email')
    if not email:
        flash('Please register first.', 'warning')
        return redirect(url_for('main.register'))
        
    if request.method == 'POST':
        otp_input = request.form.get('otp')
        user = User.query.filter_by(email=email).first()
        
        if user and user.otp == otp_input:
            user.is_verified = True
            user.otp = None # Clear OTP
            db.session.commit()
            
            # Remove from session
            session.pop('verification_email', None)
            
            flash('Email verified successfully! You can now login.', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
            
    return render_template('verify.html', email=email)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            if not user.is_verified:
                session['verification_email'] = user.email
                flash('Please verify your email first. A new OTP has been sent.', 'warning')
                otp = generate_otp()
                user.otp = otp
                db.session.commit()
                send_otp_email(user.email, otp)
                return redirect(url_for('main.verify'))
                
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            
    return render_template('login.html')

@main.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            otp = generate_otp()
            user.otp = otp
            db.session.commit()
            send_otp_email(user.email, otp)
            session['reset_email'] = user.email
            flash('If an account with that email exists, an OTP has been sent.', 'info')
            return redirect(url_for('main.reset_password'))
        else:
            # We still show success for security reasons (don't leak registered emails)
            flash('If an account with that email exists, an OTP has been sent.', 'info')
            
    return render_template('forgot_password.html')

@main.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    email = session.get('reset_email')
    if not email:
        flash('Please request a password reset first.', 'warning')
        return redirect(url_for('main.forgot_password'))
        
    if request.method == 'POST':
        otp_input = request.form.get('otp')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.otp == otp_input:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user.password_hash = hashed_password
            user.otp = None # Clear OTP
            db.session.commit()
            
            # Remove from session
            session.pop('reset_email', None)
            
            flash('Password reset successfully! You can now login.', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
            
    return render_template('reset_password.html', email=email)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    now = datetime.now(timezone.utc)
    
    # Lazy activation check: Are there any problems scheduled for the past that aren't active yet?
    past_scheduled = Problem.query.filter(Problem.scheduled_for <= now, Problem.is_active == False).order_by(Problem.scheduled_for.desc()).first()
    if past_scheduled:
        Problem.query.update({Problem.is_active: False})
        past_scheduled.is_active = True
        past_scheduled.scheduled_for = None
        db.session.commit()
        
    active_problem = Problem.query.filter_by(is_active=True).first()
    scheduled_problem = None
    
    if not active_problem:
        scheduled_problem = Problem.query.filter(Problem.scheduled_for > now).order_by(Problem.scheduled_for.asc()).first()
    
    # Check if user already solved it
    already_solved = False
    if active_problem:
        correct_sub = Submission.query.filter_by(
            user_id=current_user.id, 
            problem_id=active_problem.id, 
            is_correct=True
        ).first()
        if correct_sub:
            already_solved = True

    if request.method == 'POST':
        if not active_problem:
            flash('No active problem available right now.', 'warning')
            return redirect(url_for('main.dashboard'))
            
        answer = request.form.get('answer', '').strip()
        
        # Check correctness (case-insensitive)
        is_correct = (answer.lower() == active_problem.correct_answer.lower().strip())
        
        submission = Submission(
            user_id=current_user.id,
            problem_id=active_problem.id,
            answer=answer,
            is_correct=is_correct
        )
        db.session.add(submission)
        
        if is_correct:
            if not already_solved:
                # First time solving, give points
                current_user.points += 100
                db.session.commit()
                flash('Correct answer! You earned 100 points.', 'success')
            else:
                db.session.commit()
                flash('Correct answer! But you have already solved this problem.', 'info')
        else:
            db.session.commit()
            flash('Incorrect answer. Try again!', 'danger')
            
        return redirect(url_for('main.dashboard'))
        
    # Get all past submissions for this user & problem
    user_submissions = []
    if active_problem:
        user_submissions = Submission.query.filter_by(
            user_id=current_user.id, 
            problem_id=active_problem.id
        ).order_by(Submission.submission_time.desc()).all()

    return render_template('dashboard.html', 
                           problem=active_problem, 
                           already_solved=already_solved,
                           submissions=user_submissions,
                           scheduled_problem=scheduled_problem)

@main.route('/leaderboard')
def leaderboard():
    active_problem = Problem.query.filter_by(is_active=True).first()
    
    leaderboard_data = []
    
    if active_problem:
        # Get users who have solved the problem
        # We need their first correct submission time
        
        # Raw query logic via SQLAlchemy
        # Join User and Submission
        correct_subs = Submission.query.filter_by(problem_id=active_problem.id, is_correct=True).all()
        
        # Build dictionary to find earliest submission time per user
        user_stats = {}
        for sub in correct_subs:
            if sub.user_id not in user_stats:
                user_stats[sub.user_id] = sub.submission_time
            else:
                if sub.submission_time < user_stats[sub.user_id]:
                    user_stats[sub.user_id] = sub.submission_time
                    
        # Get user details
        for uid, sub_time in user_stats.items():
            user = User.query.get(uid)
            if user:
                leaderboard_data.append({
                    'name': user.full_name,
                    'school': user.school_name,
                    'points': user.points,
                    'solve_time': sub_time
                })
                
        # Sort by points (descending), then by solve_time (ascending)
        leaderboard_data.sort(key=lambda x: (-x['points'], x['solve_time']))
        
    return render_template('leaderboard.html', leaderboard=leaderboard_data, problem=active_problem)

@main.route('/team')
def team():
    return render_template('team.html')

@main.route('/resources')
def resources():
    return render_template('resources.html')

@main.route('/archives')
def archives():
    now = datetime.now(timezone.utc)
    # Past problems are those that are not active and either have no schedule or a schedule in the past
    past_problems = Problem.query.filter(
        db.or_(Problem.scheduled_for == None, Problem.scheduled_for <= now),
        Problem.is_active == False
    ).order_by(Problem.id.desc()).all()
    
    return render_template('archives.html', problems=past_problems)

@main.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access the admin dashboard.', 'danger')
        return redirect(url_for('main.home'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        statement = request.form.get('statement')
        correct_answer = request.form.get('correct_answer')
        scheduled_for_str = request.form.get('scheduled_for')
        
        if title and statement and correct_answer:
            is_active = True
            scheduled_for = None
            
            if scheduled_for_str:
                is_active = False
                try:
                    scheduled_for = datetime.strptime(scheduled_for_str, '%Y-%m-%dT%H:%M')
                    scheduled_for = scheduled_for.replace(tzinfo=timezone.utc)
                except ValueError:
                    pass
                    
            if is_active:
                # Deactivate all other problems when a new one is made active
                Problem.query.update({Problem.is_active: False})
            
            new_problem = Problem(
                title=title,
                statement=statement,
                correct_answer=correct_answer,
                is_active=is_active,
                scheduled_for=scheduled_for
            )
            db.session.add(new_problem)
            db.session.commit()
            flash('New problem created and set as active!', 'success')
            return redirect(url_for('main.admin_dashboard'))
            
    import os
    problems = Problem.query.order_by(Problem.id.desc()).all()
    admins = User.query.filter_by(is_admin=True).all()
    primary_admin_email = os.environ.get('ADMIN_EMAIL', '').lower()
    return render_template('admin.html', problems=problems, admins=admins, primary_admin_email=primary_admin_email)

@main.route('/admin/toggle/<int:problem_id>', methods=['POST'])
@login_required
def toggle_problem(problem_id):
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
        
    problem = Problem.query.get_or_404(problem_id)
    if not problem.is_active:
        # Deactivate all others
        Problem.query.update({Problem.is_active: False})
        problem.is_active = True
        flash(f'Problem "{problem.title}" is now active.', 'success')
    else:
        problem.is_active = False
        flash(f'Problem "{problem.title}" deactivated.', 'info')
        
    db.session.commit()
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/grant', methods=['POST'])
@login_required
def grant_admin():
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
        
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    
    if user:
        if user.is_admin:
            flash(f'User {email} is already an admin.', 'info')
        else:
            user.is_admin = True
            db.session.commit()
            flash(f'Admin privileges successfully granted to {email}!', 'success')
    else:
        flash(f'No registered user found with email: {email}', 'danger')
        
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/revoke/<int:user_id>', methods=['POST'])
@login_required
def revoke_admin(user_id):
    if not current_user.is_admin:
        return redirect(url_for('main.home'))
        
    import os
    primary_admin_email = os.environ.get('ADMIN_EMAIL', '').lower()
    
    user_to_revoke = User.query.get_or_404(user_id)
    
    if user_to_revoke.email.lower() == primary_admin_email:
        flash('The Primary Admin cannot be revoked.', 'danger')
        return redirect(url_for('main.admin_dashboard'))
        
    user_to_revoke.is_admin = False
    db.session.commit()
    flash(f'Admin privileges revoked for {user_to_revoke.email}.', 'success')
    
    return redirect(url_for('main.admin_dashboard'))
