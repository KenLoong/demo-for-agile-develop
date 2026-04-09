import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Post, Comment, Interest
from forms import RegistrationForm, LoginForm, PostForm, CommentForm

load_dotenv()
app = Flask(__name__)

# --- 配置：敏感项优先来自环境变量（见 README） ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-only-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
csrf = CSRFProtect(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # 未登录时跳转的路由
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
            # 处理 "next" 参数（如果用户是从受保护页面跳转过来的）
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- 2. 首页与 AJAX 过滤 (Discovery) ---

@app.route('/')
def index():
    # 默认显示最新发布的 12 个帖子
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/api/filter')
def filter_posts():
    """供前端 JQuery AJAX 调用的接口"""
    category = request.args.get('category')
    search_query = request.args.get('query', '')

    query = Post.query
    if category and category != 'All':
        query = query.filter_by(category=category)
    if search_query:
        query = query.filter(Post.title.contains(search_query) | Post.description.contains(search_query))
    
    posts = query.order_by(Post.timestamp.desc()).all()

    def snippet(text, max_len=100):
        text = text or ''
        if len(text) <= max_len:
            return text
        return text[:max_len].rstrip() + '…'

    return jsonify([{
        'id': p.id,
        'title': p.title,
        'category': p.category,
        'author': p.author.username,
        'snippet': snippet(p.description),
        'timestamp': p.timestamp.strftime('%Y-%m-%d')
    } for p in posts])

# --- 3. 帖子管理 (Skill CRUD) ---

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, 
                    description=form.description.data, 
                    category=form.category.data, 
                    author=current_user)
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
    if current_user.is_authenticated:
        already_interested = (
            Interest.query.filter_by(sender_id=current_user.id, post_id=post_id).first()
            is not None
        )
    return render_template(
        'post_detail.html',
        title=post.title,
        post=post,
        form=form,
        interest_count=interest_count,
        already_interested=already_interested,
    )

@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403) # 只有作者本人能修改
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.description = form.description.data
        post.category = form.category.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post_detail', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.description.data = post.description
        form.category.data = post.category
    return render_template('create_post.html', title='Update Skill', form=form, editing=True, post=post)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('index'))

# --- 4. 互动逻辑 (Interactions) ---

@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def post_comment(post_id):
    form = CommentForm()
    wants_json = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, user_id=current_user.id, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
        if wants_json:
            return jsonify({
                'ok': True,
                'username': current_user.username,
                'timestamp': comment.timestamp.strftime('%Y-%m-%d %H:%M'),
                'content': comment.content,
            })
        flash('Your comment has been added!', 'success')
    else:
        if wants_json:
            msg = form.content.errors[0] if form.content.errors else 'Could not post comment.'
            return jsonify({'ok': False, 'message': msg}), 400
        for err in form.content.errors:
            flash(err, 'danger')
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/interest/<int:post_id>', methods=['POST'])
@login_required
def express_interest(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author == current_user:
        return jsonify({'status': 'error', 'message': 'You cannot request your own skill.'}), 400
    
    # 检查是否已存在申请
    existing = Interest.query.filter_by(sender_id=current_user.id, post_id=post_id).first()
    if existing:
        return jsonify({'status': 'error', 'message': 'Already sent a request.'}), 400
    
    new_interest = Interest(sender_id=current_user.id, post_id=post_id)
    db.session.add(new_interest)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Request sent successfully!'})

# --- 5. 个人仪表盘 (Dashboard) ---

@app.route('/dashboard')
@login_required
def dashboard():
    # 1. 我发布的技能
    my_posts = Post.query.filter_by(user_id=current_user.id).all()
    
    # 2. 谁对我的技能感兴趣 (Incoming Requests)
    # 逻辑：查询 Interest 表，关联 Post 表，筛选出作者是当前用户的记录
    incoming_interests = (
        Interest.query.join(Post)
        .filter(Post.user_id == current_user.id)
        .order_by(Interest.timestamp.desc())
        .all()
    )
    
    # 3. 我发出的申请 (Sent Requests)
    my_sent_requests = (
        Interest.query.filter_by(sender_id=current_user.id)
        .order_by(Interest.timestamp.desc())
        .all()
    )
    
    return render_template('dashboard.html', 
                           title='Dashboard', 
                           my_posts=my_posts, 
                           incoming=incoming_interests, 
                           sent=my_sent_requests)

# --- 启动程序 ---
# 数据库表请使用 Flask-Migrate：`flask db upgrade`（见 README）

if __name__ == '__main__':
    app.run(debug=True)