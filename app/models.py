from app import db 
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))



class User(UserMixin,db.Model):

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), nullable = False, unique = True)
    password_hash = db.Column(db.String(200), nullable = False)
    email = db.Column(db.String(50), nullable = False, unique = True)

    posts = db.relationship("Post", backref = "author")

    def __repr__(self):
        return f"User {self.username}"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)
    



class Post(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(400), nullable = False)
    timestamp = db.Column(db.DateTime, default = lambda : datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    def __repr__(self):
        return f"Post {self.body[:20]}"
    



