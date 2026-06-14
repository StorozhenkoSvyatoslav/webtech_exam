from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from models import db, Collection, Book
from auth import check_rights

collections_bp = Blueprint('collections', __name__, url_prefix='/collections')

_USER_ONLY = ['Пользователь']


@collections_bp.route('/')
@check_rights(_USER_ONLY)
def index():
    collections = (Collection.query
                   .filter_by(user_id=current_user.id)
                   .order_by(Collection.name)
                   .all())
    return render_template('collections/index.html', collections=collections)


@collections_bp.route('/add', methods=['POST'])
@check_rights(_USER_ONLY)
def add_collection():
    name = request.form.get('name', '').strip()
    if not name:
        flash('Название подборки не может быть пустым', 'danger')
        return redirect(url_for('collections.index'))
    try:
        col = Collection(name=name, user_id=current_user.id)
        db.session.add(col)
        db.session.commit()
        flash(f'Подборка «{name}» успешно создана', 'success')
    except Exception:
        db.session.rollback()
        flash('При создании подборки возникла ошибка', 'danger')
    return redirect(url_for('collections.index'))


@collections_bp.route('/<int:collection_id>')
@check_rights(_USER_ONLY)
def view_collection(collection_id):
    col = db.session.get(Collection, collection_id)
    if col is None or col.user_id != current_user.id:
        flash('У вас недостаточно прав для выполнения данного действия', 'danger')
        return redirect(url_for('main.index'))
    return render_template('collections/view.html', collection=col)


@collections_bp.route('/add_book', methods=['POST'])
@check_rights(_USER_ONLY)
def add_book_to_collection():
    book_id = request.form.get('book_id', type=int)
    collection_id = request.form.get('collection_id', type=int)

    book = db.session.get(Book, book_id)
    col = db.session.get(Collection, collection_id)

    if book is None or col is None or col.user_id != current_user.id:
        flash('У вас недостаточно прав для выполнения данного действия', 'danger')
        return redirect(url_for('main.index'))

    try:
        if book not in col.books:
            col.books.append(book)
            db.session.commit()
            flash(f'Книга «{book.title}» добавлена в подборку «{col.name}»', 'success')
        else:
            flash('Эта книга уже есть в выбранной подборке', 'warning')
    except Exception:
        db.session.rollback()
        flash('При добавлении книги в подборку возникла ошибка', 'danger')

    return redirect(url_for('books.view_book', book_id=book_id))
