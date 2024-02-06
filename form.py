from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms.validators import  EqualTo, Email, DataRequired

class RegisterForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired(), EqualTo('password_2')])
    password_2 = PasswordField('repassword', validators=[DataRequired()])


class CommentForm(FlaskForm):
    content = StringField('comment', validators=[DataRequired()])
    
    
# 참고 WTForms를 가지고 폼 유효성 확인하기(https://flask-docs-kr.readthedocs.io/ko/latest/patterns/wtforms.html)