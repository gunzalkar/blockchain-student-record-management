from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import Email, EqualTo, DataRequired, Length

class BasicForm(FlaskForm):
	f_name = StringField('First Name', validators=[DataRequired()])
	l_name = StringField('Last Name', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	address = StringField('Address', validators=[DataRequired()])
	batch = StringField('Batch', validators=[DataRequired()])
	roll_no = StringField('Roll No', validators=[DataRequired()])
	enrollment_no = StringField('Enrollment No', validators=[DataRequired()])
	submit = SubmitField('Register')

class SearchForm(FlaskForm):
	enrollment = StringField('Enrollment No', validators=[DataRequired()])
	submit = SubmitField('Search')

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Login', validators=[DataRequired()])




