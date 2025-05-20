from flask import Flask,render_template,redirect,url_for,flash
from extensions import db, login_manager, csrf
from models import User
from forms import RegistrationForm,LoginForm
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user

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
            flash("✅ Logged in successfully!", "success")
            return redirect(url_for('home')) 
        else:
            flash("❌ Invalid email or password", "danger")

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
        return redirect(url_for(''))  

    return render_template('authentication/register.html', form=form)










if __name__ == '__main__':
    app.run(debug=True)
