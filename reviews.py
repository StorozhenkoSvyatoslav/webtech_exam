from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Book, Review
from utils import sanitize

reviews_bp = Blueprint('reviews', __name__)

RATING_CHOICES = [
    (5, 'Отлично'),
    (4, 'Хорошо'),
    (3, 'Удовлетворительно'),
    (2, 'Неудовлетворительно'),
    (1, 'Плохо'),
    (0, 'Ужасно'),
]


@reviews_bp.route('/books/<int:book_id>/review', methods=['GET', 'POST'])
@login_required
def add_review(book_id):
    book = db.session.get(Book, book_id)
    if book is None:
        flash('Книга не найдена', 'danger')
        return redirect(url_for('main.index'))

    existing = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first()
    if existing:
        flash('Вы уже оставили рецензию на эту книгу', 'warning')
        return redirect(url_for('books.view_book', book_id=book_id))

    if request.method == 'POST':
        try:
            rating = int(request.form['rating'])
            text = sanitize(request.form.get('text', ''))

            review = Review(
                book_id=book_id,
                user_id=current_user.id,
                rating=rating,
                text=text,
            )
            db.session.add(review)
            db.session.commit()
            flash('Рецензия успешно добавлена', 'success')
            return redirect(url_for('books.view_book', book_id=book_id))
        except Exception:
            db.session.rollback()
            flash('При сохранении рецензии возникла ошибка', 'danger')

    return render_template('books/review.html', book=book, rating_choices=RATING_CHOICES)
