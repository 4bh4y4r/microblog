from app import app
from flask import render_template, request, redirect, url_for,flash
from app.forms import LoginForm


@app.route('/index')
def index():

    return render_template('index.html')


@app.route('/login', methods = ["GET", "POST"])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        flash(f"login requested for {form.username.data}, remember_me = {form.remember_me.data}")
        return redirect(url_for('index'))
    return render_template('login.html', form = form, title = "Log In")