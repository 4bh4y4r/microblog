from app import app
from flask import render_template, request, redirect, url_for,flash
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user
from app.models import User, Post


@app.route('/index')
def index():

    return render_template('index.html')


@app.route('/login', methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.html'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid credentials")
            return redirect(url_for('login'))
        
        login_user(user, remember_me = form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', form = form, title = "Log In")


@app.route('/logout')
def logout():
    logout_user
    return redirect(url_for('login'))