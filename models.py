from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import session

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database"""
    db.app = app
    db.init_app(app)


class User(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String(20), unique=True, primary_key=True)

    password = db.Column(db.Text, nullable=False)

    email = db.Column(db.String(50), nullable=False)

    first_name = db.Column(db.String(30), nullable=False)

    last_name = db.Column(db.String(30), nullable=False)

    @classmethod
    def sign_up(cls, u, pwd, eml, f_nm, l_nm):
        """Register user with hashed password and return new user"""
        hashed = bcrypt.generate_password_hash(pwd)

        hashed_utf8 = hashed.decode("utf8")

        return cls(username=u, password=hashed_utf8, email=eml, first_name=f_nm, last_name=l_nm)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate user exists & password is correct. Return user if valid"""
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else:
            return False

    @classmethod
    def is_logged_in(cls, username):
        if 'username' not in session or username != session['username']:
            return False
        return True

    @classmethod
    def delete_user(cls, username):
        user = User.query.filter_by(username=username).first()
        if user:
            Feedback.query.filter_by(username=username).delete()
            db.session.commit()
            db.session.delete(user)
            db.session.commit()
            session.pop('username')
            return f"{username} has been deleted"
        else:
            return f"{username} not found"


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.String(100), nullable=False)

    content = db.Column(db.Text, nullable=False)

    username = db.Column(db.String, db.ForeignKey('users.username'))

    user = db.relationship('User', backref="feedback")

    def delete(self):
        Feedback.query.filter_by(id=self.id).delete()
        db.session.commit()
