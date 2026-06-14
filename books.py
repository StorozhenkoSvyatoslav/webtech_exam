import os
import uuid
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename
from models import db, Book, Cover, Genre, Review
from auth import check_rights
from utils import sanitize

books_bp = Blueprint('books', __name__, url_prefix='/books')


def _save_cover(file, book_id):
    file_content = file.read()
    md5_hash = hashlib.md5(file_content).hexdigest()
    mime_type = file.content_type or 'application/octet-stream'

    existing = Cover.query.filter_by(md5_hash=md5_hash).first()
    if existing:
        file_name = existing.file_name
    else:
        ext = os.path.splitext(secure_filename(file.filename))[1] or '.jpg'
        file_name = uuid.uuid4().hex + ext
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_name)
        with open(save_path, 'wb') as f:
            f.write(file_content)

    cover = Cover(file_name=file_name, mime_type=mime_type, md5_hash=md5_hash, book_id=book_id)
    db.session.add(cover)
    return cover


@books_bp.route('/<int:book_id>')
def view_book(book_id):
    book = db.session.get(Book, book_id)
    if book is None:
        flash('Книга не найдена', 'danger')
        return redirect(url_for('main.index'))

    user_review = None
    user_collections = []

    if current_user.is_authenticated:
        user_review = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first()
        if current_user.role.name == 'Пользователь':
            user_collections = current_user.collections

    return render_template('books/view.html', book=book,
                           user_review=user_review, user_collections=user_collections)


@books_bp.route('/add', methods=['GET', 'POST'])
@check_rights(['Администратор'])
def add_book():
    genres = Genre.query.order_by(Genre.name).all()

    if request.method == 'POST':
        cover_file = request.files.get('cover')
        selected_genre_ids = request.form.getlist('genres')

        if not cover_file or not cover_file.filename:
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return render_template('books/add.html', genres=genres, book=None)

        if not selected_genre_ids:
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return render_template('books/add.html', genres=genres, book=None)

        try:
            book = Book(
                title=request.form['title'],
                short_description=sanitize(request.form.get('short_description', '')),
                year=int(request.form['year']),
                publisher=request.form['publisher'],
                author=request.form['author'],
                pages=int(request.form['pages']),
            )
            for gid in selected_genre_ids:
                genre = db.session.get(Genre, int(gid))
                if genre:
                    book.genres.append(genre)

            db.session.add(book)
            db.session.flush()

            _save_cover(cover_file, book.id)
            db.session.commit()
            flash('Книга успешно добавлена', 'success')
            return redirect(url_for('books.view_book', book_id=book.id))
        except Exception:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')

    return render_template('books/add.html', genres=genres, book=None)


@books_bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
@check_rights(['Администратор', 'Модератор'])
def edit_book(book_id):
    book = db.session.get(Book, book_id)
    if book is None:
        flash('Книга не найдена', 'danger')
        return redirect(url_for('main.index'))

    genres = Genre.query.order_by(Genre.name).all()

    if request.method == 'POST':
        selected_genre_ids = request.form.getlist('genres')
        try:
            book.title = request.form['title']
            book.short_description = sanitize(request.form.get('short_description', ''))
            book.year = int(request.form['year'])
            book.publisher = request.form['publisher']
            book.author = request.form['author']
            book.pages = int(request.form['pages'])

            book.genres = []
            for gid in selected_genre_ids:
                genre = db.session.get(Genre, int(gid))
                if genre:
                    book.genres.append(genre)

            db.session.commit()
            flash('Книга успешно обновлена', 'success')
            return redirect(url_for('books.view_book', book_id=book.id))
        except Exception:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')

    return render_template('books/edit.html', book=book, genres=genres)


@books_bp.route('/<int:book_id>/delete', methods=['POST'])
@check_rights(['Администратор'])
def delete_book(book_id):
    book = db.session.get(Book, book_id)
    if book is None:
        flash('Книга не найдена', 'danger')
        return redirect(url_for('main.index'))

    title = book.title
    try:
        if book.cover:
            same_file_count = Cover.query.filter_by(file_name=book.cover.file_name).count()
            if same_file_count <= 1:
                cover_path = os.path.join(current_app.config['UPLOAD_FOLDER'], book.cover.file_name)
                if os.path.exists(cover_path):
                    os.remove(cover_path)

        db.session.delete(book)
        db.session.commit()
        flash(f'Книга «{title}» успешно удалена', 'success')
    except Exception:
        db.session.rollback()
        flash('При удалении книги возникла ошибка', 'danger')

    return redirect(url_for('main.index'))
