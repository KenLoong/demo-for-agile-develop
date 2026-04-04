from app import app, db
from models import User, Post, Comment, Interest
from werkzeug.security import generate_password_hash

def seed_data():
    with app.app_context():
        # 1. 清空并重建表
        db.drop_all()
        db.create_all()

        # 2. 创建几个测试用户 (密码统一为 password123)
        pw = generate_password_hash('password123')
        u1 = User(username='MemberA', email='a@student.uwa.edu.au', password_hash=pw)
        u2 = User(username='MemberB', email='b@student.uwa.edu.au', password_hash=pw)
        db.session.add_all([u1, u2])
        db.session.commit()

        # 3. 创建几个技能帖子
        p1 = Post(title='Python Tutoring', description='I can help with CITS1401 logic.', 
                  category='Coding', user_id=u1.id)
        p2 = Post(title='Guitar Basics', description='Teaching acoustic guitar for beginners.', 
                  category='Music', user_id=u2.id)
        db.session.add_all([p1, p2])
        db.session.commit()

        # 4. 模拟一个“兴趣申请” (u1 对 u2 的吉他课感兴趣)
        interest = Interest(sender_id=u1.id, post_id=p2.id)
        db.session.add(interest)
        db.session.commit()

        print("Database initialized with seed data!")

if __name__ == '__main__':
    seed_data()