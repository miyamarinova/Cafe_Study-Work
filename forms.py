from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, SelectField, PasswordField
from wtforms.validators import DataRequired,URL

class NewCafeForm(FlaskForm):

    cafe = StringField('Cafe name', validators=[DataRequired()])
    location_url = URLField('Cafe Location on Google Maps (URL)', validators=[URL(), DataRequired()])
    image = URLField('Cafe Image (URL)', validators=[URL(), DataRequired()])
    location = StringField('Location:: ', validators=[DataRequired()])
    wifi = SelectField('Wifi Availability',
                       choices=[("✘"), ("💪️"),("💪️💪️"),("💪️💪️💪️"),("💪️💪️💪️💪️")])
    power = SelectField('Power Socket Availability: ',
                        choices=[("✘"), ("🔌"), ("🔌🔌"), ("🔌🔌🔌"), ("🔌🔌🔌🔌")])
    wc = SelectField('Toilet Availability: ',choices=[("0", "Nope"), ("1", "Yes")])
    calls = SelectField('Can take calls:',
                        choices=[("0", "Nope"), ("1", "Yes")])
    seats = StringField('Number of seats:',
                        validators=[DataRequired()])
    coffee_price = StringField('Coffee Price', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    sign_up = SubmitField("SIGN ME UP!")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    sign_up = SubmitField('Submit')