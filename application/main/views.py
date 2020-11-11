from datetime import datetime
from flask import render_template, request, session, redirect, url_for, flash, abort
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm, SmsForm, ReceiveSmsForm, CallerForm
from .. import db
from ..models import User, Role, Permission, Post
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required
from twilio.rest import Client
from twilio import twiml
import socket

@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data, 
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', form=form, name=session.get('name'), current_time=datetime.utcnow(), known=session.get('known', False))

@main.route('/mainview', methods=['GET', 'POST'])
@login_required
def main_view():
    form=SmsForm()
    if request.method == "POST":
        phone_number = request.form["phone_number"]
        new_message = request.form["new_message"]
        account_sid = 'AC5f94bbdfcd9e336375079205c2071cd7'
        auth_token = '0e7616807a9497d8a17c3abbe4b69d45'
        client = Client(account_sid, auth_token)
        message = client.messages \
            .create( 
                body=new_message,
                from_='+1 720 204 5702',
                to=phone_number
                )
        print(message.sid)
    return render_template('mainview.html', form=form)

@main.route('/call', methods=['GET', 'POST'])
@login_required
def make_call():
    form=CallerForm()
    if request.method == "POST":
        phone_number = request.form["phone_number"]
       # new_message = request.form["new_message"]
        account_sid = 'AC5f94bbdfcd9e336375079205c2071cd7'
        auth_token = '0e7616807a9497d8a17c3abbe4b69d45'
        client = Client(account_sid, auth_token)
        call = client.calls \
            .create( 
                url='http://demo.twilio.com/docs/voice.xml',
                from_='+1 720 204 5702',
                to=phone_number
                )
        print(call.sid)
    return render_template('call.html', form=form)


@main.route('/receive', methods=['GET','POST'])
@login_required
def receive_sms():
    HOST = '127.0.0.1/receive' 
    PORT = 5000      
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(5000)
                if not data:
                    break
            conn.sendall(data)
    #form=ReceiveSmsForm()
    return render_template('receivesms.html')


@main.route('/user/<username>')
def user(username):
    user = user.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
#admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


