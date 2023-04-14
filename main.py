from flask import Flask, render_template, request, redirect, url_for, abort, flash
from flask_bootstrap import Bootstrap
from flask_login import UserMixin
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms import StringField, SubmitField, SelectField, URLField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy
from forms import NewCafeForm, LoginForm, RegisterForm
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

ADMIN_EMAIL = 'admin123@abv.bg'
ADMIN_PASSWORD = '12345678'

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class CafeForm(FlaskForm):
    cafe = StringField('Cafe name', validators=[DataRequired()])
    location = StringField('Cafe Location on Google Maps(URL)', validators=[DataRequired(),URL()])
    open_hour = StringField('Opening Time e.g.8AM', validators=[DataRequired()])
    close_hour = StringField('Closing Time e.g.5:30PM', validators=[DataRequired()])
    rating = StringField('Coffee Rating', validators=[DataRequired()])
    web_rating = StringField('Wifi Strenght Rating', validators=[DataRequired()])
    power_rating = StringField('Power Socket Rating', validators=[DataRequired()])
    submit = SubmitField('Submit')

class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.String, nullable=False)
    has_sockets = db.Column(db.String, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    name = db.Column(db.String)
db.create_all()

def admin_only(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if current_user.id != 1:
            abort(404, description="You don't have the permission to access the requested resource.")
        return f(*args, **kwargs)
    return wrapped

@app.route('/')
def home():
    all_cafes = db.session.query(Cafe).all()
    cafes = [cafe.to_dict() for cafe in all_cafes]
    return render_template('index.html', cafe_list=cafes,current_user=current_user)

def boolean_convert(to_convert):
    if to_convert == "1":
        return bool(to_convert)
    else:
        return 0

@app.route("/add", methods=['GET', 'POST'])
def add_cafe():
    form = NewCafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=request.form['cafe'],
            map_url=request.form["location_url"],
            img_url=request.form["image"],
            location=request.form["location"],
            seats=request.form["seats"],
            has_toilet=boolean_convert(request.form["wc"]),
            has_wifi=request.form["wifi"],
            has_sockets=request.form["power"],
            can_take_calls=boolean_convert(request.form["calls"]),
            coffee_price=f"£{request.form['coffee_price']}"
        )
        db.session.add(new_cafe)
    # db.session.rollback()
        db.session.commit()
        return redirect(url_for('home', success_msg = 'Yay!Thank you for adding one more nice spot to our selection!'))
    return render_template('add_cafe.html',form=form)

@app.route("/delete/<int:cafe_id>")
@admin_only
def delete_cafe(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Register new user, take the information that is inputted in register.html and create a new object User to save into the users databas
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash_salt_password = generate_password_hash(form.password.data, method='pbkdf2:sha256',salt_length=8)
        new_user = User(
            email=form.email.data,
            password=hash_salt_password,
            name=form.name.data
        )
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash("You've already signed up with this email, log in instead.")
            return redirect("login")
        else:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("home"))
    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data,
        password = form.password.data
        user = User.query.filter_by(email=form.email.data).first()

        if not email == ADMIN_EMAIL:
            flash("Wrong email. Please, try again!")
            return redirect(url_for('login'))
        elif not check_password_hash(ADMIN_PASSWORD, password):
            flash("Password incorrect, please try again!")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", form=form, current_user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
