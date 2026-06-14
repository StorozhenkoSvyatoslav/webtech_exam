import os
import markdown
from flask import Flask
from flask_login import LoginManager
from sqlalchemy import event
from sqlalchemy.engine import Engine
from models import db, User

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '123123123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'covers')

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Для выполнения данного действия необходимо пройти процедуру аутентификации'
    login_manager.login_message_category = 'warning'

    @event.listens_for(Engine, 'connect')
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.template_filter('markdown')
    def render_markdown(text):
        return markdown.markdown(text or '')

    from auth import auth_bp
    from main import main_bp
    from books import books_bp
    from reviews import reviews_bp
    from book_collections import collections_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(collections_bp)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
