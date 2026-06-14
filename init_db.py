from werkzeug.security import generate_password_hash
from app import app
from models import db, Role, User, Genre


def init_db():
    with app.app_context():
        db.create_all()

        if not Role.query.first():
            roles = [
                Role(name='Администратор',
                     description='Суперпользователь, имеет полный доступ к системе, '
                                 'в том числе к созданию и удалению книг'),
                Role(name='Модератор',
                     description='Может редактировать данные книг и производить модерацию рецензий'),
                Role(name='Пользователь',
                     description='Может оставлять рецензии'),
            ]
            db.session.add_all(roles)
            db.session.commit()
            print('Roles created.')

        if not Genre.query.first():
            genres = [
                Genre(name='Фантастика'),
                Genre(name='Фэнтези'),
                Genre(name='Детектив'),
                Genre(name='Роман'),
                Genre(name='Приключения'),
                Genre(name='Научная литература'),
                Genre(name='История'),
                Genre(name='Биография'),
                Genre(name='Психология'),
                Genre(name='Классика'),
            ]
            db.session.add_all(genres)
            db.session.commit()
            print('Genres created.')

        if not User.query.first():
            admin_role = Role.query.filter_by(name='Администратор').first()
            moder_role = Role.query.filter_by(name='Модератор').first()
            user_role = Role.query.filter_by(name='Пользователь').first()

            users = [
                User(login='admin123',
                     password_hash=generate_password_hash('123123'),
                     last_name='Админов', first_name='Админ', middle_name='Иванович',
                     role_id=admin_role.id),
                User(login='moder123',
                     password_hash=generate_password_hash('123123'),
                     last_name='Петров', first_name='Пётр', middle_name='Модератович',
                     role_id=moder_role.id),
                User(login='user1',
                     password_hash=generate_password_hash('123123'),
                     last_name='Даниленко', first_name='Денис', middle_name='Андреевич',
                     role_id=user_role.id),
                User(login='user2',
                     password_hash=generate_password_hash('123123'),
                     last_name=' ', first_name='семквак2',
                     role_id=user_role.id),
                User(login='user3',
                     password_hash=generate_password_hash('123123'),
                     last_name='Новиков', first_name='Новик',
                     role_id=user_role.id),
            ]
            db.session.add_all(users)
            db.session.commit()
            print('Test users created.')

        print('Database initialized successfully!')


if __name__ == '__main__':
    init_db()
