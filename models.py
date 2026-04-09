from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(40), unique=True, nullable=False)
    label = db.Column(db.String(80), nullable=False)
    sort_order = db.Column(db.Integer, default=0)

    posts = db.relationship('Post', back_populates='category', lazy=True)


class Interest(db.Model):
    """Express interest in a post (sender + post + timestamp)."""
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class PostLike(db.Model):
    """Per-user like on a post (one like per user per post)."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='uq_post_like_user_post'),)


class Bookmark(db.Model):
    """Saved post / read-later for the current user."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='uq_bookmark_user_post'),)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    posts = db.relationship('Post', back_populates='author', lazy=True)
    interests_sent = db.relationship('Interest', backref='sender', lazy=True)
    saved_bookmarks = db.relationship('Bookmark', backref='user', lazy=True, cascade='all, delete-orphan')
    post_likes = db.relationship('PostLike', backref='user', lazy=True, cascade='all, delete-orphan')


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    # Relative to static/: uploads/posts/<filename>
    image_filename = db.Column(db.String(120), nullable=True)
    comment_count = db.Column(db.Integer, nullable=False, default=0)
    like_count = db.Column(db.Integer, nullable=False, default=0)

    author = db.relationship('User', back_populates='posts')
    category = db.relationship('Category', back_populates='posts')
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    interested_users = db.relationship('Interest', backref='post_ref', lazy=True)
    bookmarks = db.relationship('Bookmark', backref='post', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('PostLike', backref='post', lazy=True, cascade='all, delete-orphan')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    user = db.relationship('User', backref='comments')
