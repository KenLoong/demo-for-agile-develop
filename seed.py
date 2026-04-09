from app import app, db
from models import User, Post, Comment, Interest, Category, Bookmark, PostLike
from werkzeug.security import generate_password_hash


def seed_data():
    with app.app_context():
        Comment.query.delete()
        PostLike.query.delete()
        Bookmark.query.delete()
        Interest.query.delete()
        Post.query.delete()
        User.query.delete()
        Category.query.delete()
        db.session.commit()

        categories_data = [
            ('coding', 'Coding / IT', 10),
            ('language', 'Languages', 20),
            ('music', 'Music / Arts', 30),
            ('sports', 'Sports / Fitness', 40),
            ('other', 'Other', 50),
        ]
        for slug, label, order in categories_data:
            db.session.add(Category(slug=slug, label=label, sort_order=order))
        db.session.commit()

        cat_coding = Category.query.filter_by(slug='coding').first()
        cat_music = Category.query.filter_by(slug='music').first()

        pw = generate_password_hash('password123')
        u1 = User(username='MemberA', email='a@student.uwa.edu.au', password_hash=pw)
        u2 = User(username='MemberB', email='b@student.uwa.edu.au', password_hash=pw)
        db.session.add_all([u1, u2])
        db.session.commit()

        p1 = Post(
            title='Python Tutoring',
            description=(
                'I can help with **CITS1401** logic and introductory Python.\n\n'
                '- Week 1–4 revision\n'
                '- Practice questions\n\n'
                'Contact me after you express interest!'
            ),
            user_id=u1.id,
            category_id=cat_coding.id,
        )
        p2 = Post(
            title='Guitar Basics',
            description=(
                'Teaching **acoustic guitar** for beginners.\n\n'
                '> Bring your own guitar if you have one.\n\n'
                'We can cover chords and simple songs.'
            ),
            user_id=u2.id,
            category_id=cat_music.id,
        )
        db.session.add_all([p1, p2])
        db.session.commit()

        interest = Interest(sender_id=u1.id, post_id=p2.id)
        db.session.add(interest)
        db.session.commit()

        print('Database initialized with seed data!')


if __name__ == '__main__':
    seed_data()
