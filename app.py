from flask import Flask,render_template,redirect,url_for,flash,abort
from extensions import db, login_manager, csrf
from models import User,Question,Answer
from forms import RegistrationForm,LoginForm,EditProfileForm,QuestionForm,AnswerForm
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user,login_required, current_user,LoginManager,logout_user
import os,uuid
from flask_migrate import Migrate
from markdown2 import markdown



app = Flask(__name__)
app.config['SECRET_KEY'] = 'hello123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost/quizz'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app, db)
# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)


# Create tables
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from markdown2 import markdown

@app.template_filter('markdown')
def markdown_filter(text):
    return markdown(text)

@app.route('/')
def home():
    user = current_user 
    questions = Question.query.order_by(Question.created.desc()).all()
    return render_template('pages/homepage.html',user=user,questions=questions)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(" Logged in successfully!", "success")
            return redirect(url_for('home')) 
        else:
            flash(" Invalid email or password", "danger")

    return render_template('authentication/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Removes user session
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # 1. Hash the password
        hashed_password = generate_password_hash(form.password.data)

        # 2. Create new user
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )

        # 3. Save to DB
        db.session.add(new_user)
        db.session.commit()

        # 4. Flash + redirect
        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for('home'))  

    return render_template('authentication/register.html', form=form)

@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != current_user.id:
        abort(403)

    form = EditProfileForm(obj=user)
    return render_template('pages/profile.html', user=user, form=form)


@app.route('/profile/<int:user_id>/edit', methods=['POST'])
@login_required
def edit_profile(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != current_user.id:
        abort(403)

    form = EditProfileForm()

    if form.validate_on_submit():
        user.username = form.username.data

        # ✅ Handle new avatar upload
        if form.avatar.data:
            file = form.avatar.data
            ext = os.path.splitext(file.filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            avatar_folder = os.path.join('static', 'uploads', 'avatars')
            os.makedirs(avatar_folder, exist_ok=True)
            new_avatar_path = os.path.join(avatar_folder, filename)
            file.save(new_avatar_path)

            # ✅ Delete old avatar if it's not default
            if user.avatar != 'uploads/avatars/default.png':
                old_avatar_path = os.path.join('static', user.avatar)
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
                    print("🧹 Deleted old avatar:", old_avatar_path)

            # ✅ Save new avatar path
            user.avatar = f"uploads/avatars/{filename}"

        db.session.commit()
        flash("✅ Profile updated!", "success")
        return redirect(url_for('profile', user_id=user.id))


@app.route('/postquestion', methods=['POST', 'GET'])
@login_required
def post_question():
    form = QuestionForm()

    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        tags = form.tags.data
        image_path = None

        # ✅ Handle image upload
        if form.image.data:
            file = form.image.data
            ext = os.path.splitext(file.filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"  # generate unique name
            upload_folder = os.path.join('static', 'uploads', 'questions')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            image_path = f"uploads/questions/{filename}"  # relative path

        # ✅ Create and save question
        question = Question(
            title=title,
            body=body,
            tags=tags,
            image=image_path,
            user_id=current_user.id
        )
        db.session.add(question)
        db.session.commit()

        flash("✅ Question posted successfully!", "success")
        return redirect(url_for('home', user_id=current_user.id))  # or your question view

    return render_template('pages/postquestion.html', form=form)


@app.route('/detail_question/<int:question_id>', methods=['GET', 'POST'])
def detail_question(question_id):
    question = Question.query.get_or_404(question_id)
    answers = Answer.query.filter_by(question_id=question.id).order_by(Answer.created_on.asc()).all()
    form = AnswerForm()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Please log in to post an answer.", "warning")
            return redirect(url_for('login'))

        new_answer = Answer(
            answer=form.answer.data,
            question_id=question.id,
            user_id=current_user.id
        )
        db.session.add(new_answer)
        db.session.commit()
        flash("✅ Your answer has been posted.", "success")
        return redirect(url_for('home', question_id=question.id))

    return render_template('pages/detail_question.html', question=question, answers=answers, form=form)


if __name__ == '__main__':
    app.run(debug=True)
