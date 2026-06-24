from app import db 
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


followers = db.Table(
    "followers",

    db.Column("follower_id",
              db.Integer,
              db.ForeignKey("user.id"),
              primary_key = True
              
              
              ),
    db.Column("followed_id",
              db.Integer,
              db.ForeignKey("user.id"),
              primary_key = True
              
              
              )
    



)



class User(UserMixin,db.Model):

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), nullable = False, unique = True)
    password_hash = db.Column(db.String(200), nullable = False)
    email = db.Column(db.String(50), nullable = False, unique = True)
    about_me = db.Column(db.String(300))

    following = db.relationship(
        "User",
        secondary = followers,
        primaryjoin = (followers.c.follower_id == id
                       ),
        secondaryjoin = (followers.c.followed_id == id
                         ),
        back_populates = "followers"





    )

    followers = db.relationship(
    "User",

    secondary=followers,

    primaryjoin=(
        followers.c.followed_id == id
    ),

    secondaryjoin=(
        followers.c.follower_id == id
    ),

    back_populates="following"
    )





    last_seen = db.Column(db.DateTime, default = lambda:datetime.now(timezone.utc))

    posts = db.relationship("Post", backref = "author")

    def __repr__(self):
        return f"User {self.username}"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(
            self.email.lower().encode("utf-8")
        ).hexdigest()

        return (
            f"https://www.gravatar.com/avatar/"
            f"{digest}?d=identicon&s={size}"
        )
    
    def follow(self,user):
        if not self.is_following(user):
            self.following.append(user)

    def unfollow(self,user):

        if self.is_following(user):
            self.following.remove(user)

    def is_following(self,user):

        return user in self.following 
    

    



class Post(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(400), nullable = False)
    timestamp = db.Column(db.DateTime, default = lambda : datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    def __repr__(self):
        return f"Post {self.body[:20]}"
    



