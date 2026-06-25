from app import app, db
from flask import render_template, request, redirect, url_for,flash, abort
from app.forms import LoginForm, RegisterForm, EditProfileForm, PostForm, CommentForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Comment
from urllib.parse import urlsplit 
from datetime import datetime, timezone
import requests

@app.route('/index', methods = ["POST", "GET"])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body = form.content.data, author = current_user)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('index'))
    
    page = request.args.get('page',1,type = int)
    postss = current_user.followed_posts().paginate(
        page = page,per_page = 5,error_out = False
    )
    next_url = url_for('index', page = postss.next_num) if postss.has_next else None 
    prev_url = url_for('index', page = postss.prev_num) if postss.has_prev else None 
    return render_template('index.html', form = form, posts = postss, next_url = next_url, prev_url = prev_url)


@app.route('/login', methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid credentials")
            return redirect(url_for('login'))
        
        login_user(user, remember = form.remember_me.data)
        next_page = request.args.get('next')
        
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', form = form, title = "Log In")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        token = request.form.get("cf-turnstile-response")
        response = requests.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",

                data={
                    "secret":
                    app.config["TURNSTILE_SECRET_KEY"],

                    "response":
                    token
                }
                )
        result = response.json()
        
        if not result["success"]:
            flash("Turnstile verification failed")
            return redirect(url_for(register))
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, site_key = app.config["TURNSTILE_SITE_KEY"])


@app.route("/user/<username>")
@login_required
def profile(username):
    user = User.query.filter_by(username = username).first()
    if not user:
        return 404
    page = request.args.get('page',1,type=int)
    posts = Post.query.filter_by(user_id =user.id).order_by(Post.timestamp.desc()).paginate(page=page,per_page =5, error_out = False)
    next_url = url_for('profile',username = user.username,  page = posts.next_num) if posts.has_next else None
    prev_url = url_for('profile', username = user.username, page = posts.prev_num) if posts.has_prev else None
    return render_template('profile.html', user = user, posts = posts, next_url = next_url, prev_url = prev_url)


@app.before_request
def before_request():

    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/editprofile', methods = ["GET", "POST"])
@login_required
def edit_profile():

    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me  = form.about_me.data
        db.session.commit()

        flash("Changes have been made successfully!")

        return redirect(url_for('profile', username = current_user.username))
    
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('editprofile.html',form = form)


@app.route("/follow/<username>", methods= ["GET", "POST"])
@login_required
def follow(username):
    user = User.query.filter_by(username = username).first()

    if not user:
        abort(404)

    if user == current_user:
        flash("You cannot follow yourself! ")
        return redirect(url_for('profile',username=username))
    
    current_user.follow(user)
    db.session.commit()
    flash(f"You are now following {username}")

    return redirect(url_for('profile',username = username))



@app.route("/unfollow/<username>", methods = ["GET", "POST"])
@login_required
def unfollow(username):
    user = User.query.filter_by(username = username).first()

    if not user:
        abort(404)

    if user == current_user:
        flash("You cannot unfollow yourself! ")
        return redirect(url_for('profile',username=username)) 
    
    current_user.unfollow(user)
    db.session.commit()
    flash("You have unfollowed {username}")

    return redirect(url_for('profile', username = username))


@app.route("/search")
@login_required
def search():

    query = request.args.get('q')

    users = User.query.filter(User.username.ilike(f"%{query}%")).all()


    return render_template(
        'search.html',query = query, users = users
    )


@app.route("/post/<id>", methods = ["GET", "POST"])
@login_required
def post(id):
    post = Post.query.get_or_404(id)
    

    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body = form.body.data, author = current_user, post = post)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('post',id=post.id))
    

    return render_template("post.html",post = post, form = form)

@app.route('/like/<id>', methods =["GET", "POST"])
@login_required
def like(id):
    post = Post.query.get_or_404(id)
    current_user.like_post(post)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/unlike/<id>', methods = ["GET", "POST"])
@login_required
def unlike(id):

    post = Post.query.get_or_404(id)
    current_user.unlike_post(post)
    db.session.commit()
    return redirect(url_for('index'))