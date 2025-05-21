from flask import Flask,render_template,redirect,url_for,flash,abort,request,current_app
from extensions import db, login_manager, csrf
from models import User
from forms import RegistrationForm,LoginForm,EditProfileForm
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user,login_required, current_user,LoginManager,logout_user
import os
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hello123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost/quizz'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

@app.route('/')
def home():
    return render_template('pages/homepage.html')

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
    form = EditProfileForm(obj=user_id) 
    return render_template('pages/profile.html', user=user,form=form)

import os
from werkzeug.utils import secure_filename

@app.route('/profile/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != current_user.id:
        abort(403)

    form = EditProfileForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data

        # Handle avatar upload
        if form.avatar.data:
            file = form.avatar.data
            filename = secure_filename(file.filename)
            avatar_folder = os.path.join('static', 'uploads', 'avatars')
            os.makedirs(avatar_folder, exist_ok=True)
            avatar_path = os.path.join(avatar_folder, filename)
            file.save(avatar_path)

            # Save path to user record
            user.avatar_url = f"/static/uploads/avatars/{filename}"

        db.session.commit()
        flash("✅ Profile updated!", "success")
        return redirect(url_for('profile', user_id=user.id))

    return render_template('pages/profile.html', user=user, form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()  # Removes user session
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))






if __name__ == '__main__':
    app.run(debug=True)
