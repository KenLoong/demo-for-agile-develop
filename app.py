import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Post, Comment, Interest, Category, Bookmark, PostLike
from forms import RegistrationForm, LoginForm, PostForm, CommentForm
from uploads_util import save_post_image, delete_post_image
from md_format import render_post_markdown, markdown_plain_snippet

load_dotenv()
app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-only-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Total request body limit (file uploads)
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024

db.init_app(app)
csrf = CSRFProtect(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


@app.template_filter('post_markdown')
def post_markdown_filter(text):
    return render_post_markdown(text)


@app.template_filter('markdown_snippet')
def markdown_snippet_filter(text, max_len=120):
    try:
        n = int(max_len)
    except (TypeError, ValueError):
        n = 120
    return markdown_plain_snippet(text, n)


def post_upload_dir():
    return os.path.join(app.root_path, 'static', 'uploads', 'posts')


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def fill_post_category_choices(form):
    form.category_id.choices = [
        (c.id, c.label) for c in Category.query.order_by(Category.sort_order, Category.id).all()
    ]


def post_list_base_query(sort):
    if sort == 'popular':
        return (
            Post.query.outerjoin(Interest)
            .group_by(Post.id)
            .order_by(func.count(Interest.id).desc(), Post.timestamp.desc())
        )
    if sort == 'likes':
        return Post.query.order_by(Post.like_count.desc(), Post.timestamp.desc())
    return Post.query.order_by(Post.timestamp.desc())


def post_to_json(p):
    return {
        'id': p.id,
        'title': p.title,
        'category_slug': p.category.slug,
        'category_label': p.category.label,
        'author': p.author.username,
        'author_profile': url_for('user_profile', username=p.author.username),
        'snippet': markdown_plain_snippet(p.description, 120),
        'timestamp': p.timestamp.strftime('%Y-%m-%d'),
        'comment_count': p.comment_count,
        'like_count': p.like_count,
        'image_url': (
            url_for('static', filename=f'uploads/posts/{p.image_filename}')
            if p.image_filename
            else None
        ),
    }


def recommended_posts_for_user(user, limit=6):
    """Categories inferred from the user's listings + posts they clicked *Interested* on."""
    if not user.is_authenticated:
        return []
    owned_cats = {
        r[0]
        for r in db.session.query(Post.category_id).filter(Post.user_id == user.id).distinct()
    }
    interest_cats = {
        r[0]
        for r in db.session.query(Post.category_id)
        .join(Interest, Interest.post_id == Post.id)
        .filter(Interest.sender_id == user.id)
        .distinct()
    }
    category_ids = list(owned_cats | interest_cats)
    if not category_ids:
        return []

    interested_post_ids = [
        r[0]
        for r in db.session.query(Interest.post_id).filter(Interest.sender_id == user.id).all()
    ]
    q = Post.query.filter(Post.category_id.in_(category_ids), Post.user_id != user.id)
    if interested_post_ids:
        q = q.filter(~Post.id.in_(interested_post_ids))
    return q.order_by(Post.timestamp.desc()).limit(limit).all()


# --- 1. 用户认证路由 (Authentication) ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# --- 2. 发现页、筛选 API、用户公开主页 ---

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'newest')
    if sort not in ('newest', 'popular', 'likes'):
        sort = 'newest'
    per_page = 9
    q = request.args.get('q', '').strip()
    categories = Category.query.order_by(Category.sort_order, Category.id).all()

    query = post_list_base_query(sort)
    if q:
        query = query.filter(Post.title.contains(q) | Post.description.contains(q))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    recommended = recommended_posts_for_user(current_user, limit=6) if current_user.is_authenticated else []
    return render_template(
        'index.html',
        posts=pagination.items,
        pagination=pagination,
        categories=categories,
        sort=sort,
        recommended_posts=recommended,
    )


@app.route('/api/filter')
def filter_posts():
    category_slug = request.args.get('category')
    search_query = request.args.get('query', '')
    sort = request.args.get('sort', 'newest')
    if sort not in ('newest', 'popular', 'likes'):
        sort = 'newest'
    page = request.args.get('page', 1, type=int)
    per_page = 9

    query = post_list_base_query(sort)
    if category_slug and category_slug != 'all':
        query = query.join(Category).filter(Category.slug == category_slug)
    if search_query:
        query = query.filter(
            Post.title.contains(search_query) | Post.description.contains(search_query)
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(
        {
            'posts': [post_to_json(p) for p in pagination.items],
            'page': pagination.page,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        }
    )


@app.route('/user/<username>')
def user_profile(username):
    profile_user = User.query.filter_by(username=username).first_or_404()
    posts = (
        Post.query.filter_by(user_id=profile_user.id)
        .order_by(Post.timestamp.desc())
        .all()
    )
    return render_template(
        'user_profile.html',
        profile_user=profile_user,
        posts=posts,
    )


# --- 3. 帖子管理 (Skill CRUD) ---

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    fill_post_category_choices(form)
    if form.validate_on_submit():
        up_dir = post_upload_dir()
        try:
            image_name = save_post_image(form.image.data, up_dir)
        except ValueError as exc:
            flash(str(exc), 'danger')
            return render_template('create_post.html', title='New Skill', form=form, editing=False, post=None)
        post = Post(
            title=form.title.data,
            description=form.description.data,
            category_id=form.category_id.data,
            user_id=current_user.id,
            image_filename=image_name,
        )
        db.session.add(post)
        db.session.commit()
        flash('Your skill has been posted!', 'success')
        return redirect(url_for('index'))
    return render_template('create_post.html', title='New Skill', form=form, editing=False, post=None)


@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    interest_count = Interest.query.filter_by(post_id=post_id).count()
    already_interested = False
    is_saved = False
    liked = False
    if current_user.is_authenticated:
        already_interested = (
            Interest.query.filter_by(sender_id=current_user.id, post_id=post_id).first()
            is not None
        )
        is_saved = (
            Bookmark.query.filter_by(user_id=current_user.id, post_id=post_id).first()
            is not None
        )
        if post.user_id != current_user.id:
            liked = (
                PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first()
                is not None
            )
    return render_template(
        'post_detail.html',
        title=post.title,
        post=post,
        form=form,
        interest_count=interest_count,
        already_interested=already_interested,
        is_saved=is_saved,
        liked=liked,
    )


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    fill_post_category_choices(form)
    if form.validate_on_submit():
        up_dir = post_upload_dir()
        if form.remove_image.data:
            delete_post_image(up_dir, post.image_filename)
            post.image_filename = None
        try:
            if form.image.data and getattr(form.image.data, 'filename', None):
                delete_post_image(up_dir, post.image_filename)
                post.image_filename = save_post_image(form.image.data, up_dir)
        except ValueError as exc:
            flash(str(exc), 'danger')
            return render_template('create_post.html', title='Update Skill', form=form, editing=True, post=post)
        post.title = form.title.data
        post.description = form.description.data
        post.category_id = form.category_id.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post_detail', post_id=post.id))
    if request.method == 'GET':
        form.title.data = post.title
        form.description.data = post.description
        form.category_id.data = post.category_id
    return render_template('create_post.html', title='Update Skill', form=form, editing=True, post=post)


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    delete_post_image(post_upload_dir(), post.image_filename)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('index'))


# --- 4. 互动逻辑 (Interactions) ---

@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def post_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    wants_json = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, user_id=current_user.id, post_id=post_id)
        db.session.add(comment)
        post.comment_count = (post.comment_count or 0) + 1
        db.session.commit()
        if wants_json:
            return jsonify({
                'ok': True,
                'username': current_user.username,
                'timestamp': comment.timestamp.strftime('%Y-%m-%d %H:%M'),
                'content': comment.content,
                'comment_count': post.comment_count,
            })
        flash('Your comment has been added!', 'success')
    else:
        if wants_json:
            msg = form.content.errors[0] if form.content.errors else 'Could not post comment.'
            return jsonify({'ok': False, 'message': msg}), 400
        for err in form.content.errors:
            flash(err, 'danger')
    return redirect(url_for('post_detail', post_id=post_id))


@app.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_post_like(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id == current_user.id:
        return jsonify({'ok': False, 'message': 'You cannot like your own skill.'}), 400
    existing = PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing:
        db.session.delete(existing)
        post.like_count = max(0, (post.like_count or 0) - 1)
        db.session.commit()
        return jsonify({'ok': True, 'liked': False, 'like_count': post.like_count})
    db.session.add(PostLike(user_id=current_user.id, post_id=post_id))
    post.like_count = (post.like_count or 0) + 1
    db.session.commit()
    return jsonify({'ok': True, 'liked': True, 'like_count': post.like_count})


@app.route('/interest/<int:post_id>', methods=['POST'])
@login_required
def express_interest(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author == current_user:
        return jsonify({'status': 'error', 'message': 'You cannot request your own skill.'}), 400

    existing = Interest.query.filter_by(sender_id=current_user.id, post_id=post_id).first()
    if existing:
        return jsonify({'status': 'error', 'message': 'Already sent a request.'}), 400

    new_interest = Interest(sender_id=current_user.id, post_id=post_id)
    db.session.add(new_interest)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Request sent successfully!'})


@app.route('/post/<int:post_id>/bookmark', methods=['POST'])
@login_required
def toggle_bookmark(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id == current_user.id:
        return jsonify({'ok': False, 'message': 'You cannot bookmark your own skill.'}), 400
    existing = Bookmark.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'ok': True, 'saved': False})
    db.session.add(Bookmark(user_id=current_user.id, post_id=post_id))
    db.session.commit()
    return jsonify({'ok': True, 'saved': True})


# --- 5. 个人仪表盘 (Dashboard) ---

@app.route('/dashboard')
@login_required
def dashboard():
    my_posts = Post.query.filter_by(user_id=current_user.id).all()
    incoming_interests = (
        Interest.query.join(Post)
        .filter(Post.user_id == current_user.id)
        .order_by(Interest.timestamp.desc())
        .all()
    )
    my_sent_requests = (
        Interest.query.filter_by(sender_id=current_user.id)
        .order_by(Interest.timestamp.desc())
        .all()
    )
    saved = (
        Bookmark.query.filter_by(user_id=current_user.id)
        .order_by(Bookmark.timestamp.desc())
        .all()
    )
    return render_template(
        'dashboard.html',
        title='Dashboard',
        my_posts=my_posts,
        incoming=incoming_interests,
        sent=my_sent_requests,
        saved=saved,
    )


if __name__ == '__main__':
    app.run(debug=True)
