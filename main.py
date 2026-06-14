from flask import Blueprint, render_template, request
from sqlalchemy import func
from models import db, Book, Review

main_bp = Blueprint('main', __name__)

PER_PAGE = 10


@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)

    query = (
        db.session.query(
            Book,
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.id).label('review_count'),
        )
        .outerjoin(Review, Book.id == Review.book_id)
        .group_by(Book.id)
        .order_by(Book.year.desc())
    )

    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template('index.html', pagination=pagination)
