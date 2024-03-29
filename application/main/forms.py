from flask import Flask
from flask_wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import Required, Length, Email, Regexp, ValidationError
from ..models import Role, User

class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    name = StringField('Real name', validotors=[Length(0,64)])
    location = StringField('Location', validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('submit')

class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    username = StringField('Username', validators=[Required(), Length(1,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0, 'Usernames must have only letters,''numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = StringField('Role', coerce=int) 
    name = StringField('Real name', validators=[Length(0,64)])
    location = StringField('Location', validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


    def __init__(self,user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user
    
    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')


class PostForm(Form):
    body = TextAreaField("What's on your mind?", validators=[Required()])
    submit = SubmitField('Submit')

class SmsForm(Form):
    phone_number = StringField('Phone Number', validators=[Required(),  Length(0,12), Regexp('^[0-9]{1,45}$')])
    new_message = TextAreaField('Message')
    submit = SubmitField('Send')

class ReceiveSmsForm(Form):
    From = StringField('From')
    Body = TextAreaField('Message')

class CallerForm(Form):
    phone_number = StringField('Phone Number', validators=[Required(),  Length(0,12), Regexp('^[0-9]{1,45}$')])
    submit = SubmitField('Call')