from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    total_pages = db.Column(db.Integer, nullable=False)
    read_pages = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default='Okunacak')
    rating = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    reading_start_date = db.Column(db.DateTime, nullable=True)
    reading_end_date = db.Column(db.DateTime, nullable=True)
    is_archived = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def progress_percentage(self):
        """Okuma ilerleme yüzdesini hesapla"""
        if self.total_pages == 0:
            return 0
        return round((self.read_pages / self.total_pages) * 100, 1)

    def to_dict(self):
        """Kitabı JSON formatına dönüştür"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'genre': self.genre,
            'total_pages': self.total_pages,
            'read_pages': self.read_pages,
            'status': self.status,
            'rating': self.rating,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'reading_start_date': self.reading_start_date.isoformat() if self.reading_start_date else None,
            'reading_end_date': self.reading_end_date.isoformat() if self.reading_end_date else None,
            'is_archived': self.is_archived,
            'progress_percentage': self.progress_percentage
        }

    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'
