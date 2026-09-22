from flask import Flask, render_template, request, jsonify
from models import db, Book
from datetime import datetime
import os
import sys

app = Flask(__name__)

# Konfigürasyon
db_path = os.path.abspath(os.environ.get('DATABASE_PATH', os.path.join('data', 'app.db')))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = os.environ.get('DEBUG', True)

# Veritabanını uygulamaya bağla
db.init_app(app)

# Geçerli tür listesi
VALID_GENRES = ['Roman', 'Bilim', 'Kişisel Gelişim', 'Felsefe', 'Tarih', 'Psikoloji']
VALID_STATUSES = ['Okunuyor', 'Okunacak', 'Bitti']


def init_db():
    """Veritabanını ve seed verisini başlat"""
    with app.app_context():
        # DB dosyasının bulunduğu klasörü ve Flask instance klasörünü oluştur
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        os.makedirs(app.instance_path, exist_ok=True)
        
        # Veritabanı tablolarını oluştur
        db.create_all()
        
        # Eğer tablo boşsa, seed verisi yükle
        if Book.query.first() is None:
            print("✓ Boş veritabanı tespit edildi. Seed verisi yükleniyor...")
            try:
                # Seed script'ini çalıştır
                from seed import populate_seed_data
                populate_seed_data()
                print("✓ Seed verisi başarıyla yüklendi!")
            except ImportError:
                print("⚠ Seed script bulunamadı. Manual olarak kitap ekleyebilirsiniz.")


# ============== API ENDPOINTS ==============

@app.route('/')
def dashboard():
    """Dashboard ana sayfası"""
    return render_template('index.html')


@app.route('/api/books', methods=['GET'])
def get_books():
    """Tüm kitapları listele (filtreleme destekli)"""
    try:
        status = request.args.get('status')
        genre = request.args.get('genre')
        search = request.args.get('search', '').lower()
        
        query = Book.query.filter_by(is_archived=False)
        
        if status and status in VALID_STATUSES:
            query = query.filter_by(status=status)
        
        if genre and genre in VALID_GENRES:
            query = query.filter_by(genre=genre)
        
        if search:
            query = query.filter(
                (Book.title.ilike(f'%{search}%')) |
                (Book.author.ilike(f'%{search}%'))
            )
        
        books = query.all()
        return jsonify([book.to_dict() for book in books]), 200
    except Exception as e:
        return jsonify({'error': True, 'message': 'Kitap listesi alınamadı', 'code': 'SERVER_ERROR'}), 500


@app.route('/api/books', methods=['POST'])
def create_book():
    """Yeni kitap ekleme"""
    try:
        data = request.get_json()
        
        # Validasyon
        errors = validate_book_data(data)
        if errors:
            return jsonify({'error': True, 'message': errors[0], 'code': 'VALIDATION_ERROR'}), 400
        
        # Yeni kitap oluştur
        book = Book(
            title=data['title'].strip(),
            author=data['author'].strip(),
            genre=data['genre'],
            total_pages=data['total_pages'],
            read_pages=data.get('read_pages', 0),
            status=data.get('status', 'Okunacak'),
            rating=data.get('rating'),
            notes=data.get('notes'),
            cover_url=data.get('cover_url')
        )
        
        db.session.add(book)
        db.session.commit()
        
        return jsonify(book.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Kitap eklenirken hata oluştu', 'code': 'SERVER_ERROR'}), 500


@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Spesifik kitap detayları"""
    try:
        book = Book.query.get(book_id)
        if not book or book.is_archived:
            return jsonify({'error': True, 'message': 'Kitap bulunamadı', 'code': 'NOT_FOUND'}), 404
        
        return jsonify(book.to_dict()), 200
    except Exception as e:
        return jsonify({'error': True, 'message': 'Kitap alınamadı', 'code': 'SERVER_ERROR'}), 500


@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Kitap tam güncelleme"""
    try:
        book = Book.query.get(book_id)
        if not book or book.is_archived:
            return jsonify({'error': True, 'message': 'Kitap bulunamadı', 'code': 'NOT_FOUND'}), 404
        
        data = request.get_json()
        
        # Validasyon
        errors = validate_book_data(data)
        if errors:
            return jsonify({'error': True, 'message': errors[0], 'code': 'VALIDATION_ERROR'}), 400
        
        # Alanları güncelle
        book.title = data['title'].strip()
        book.author = data['author'].strip()
        book.genre = data['genre']
        book.total_pages = data['total_pages']
        book.read_pages = data.get('read_pages', book.read_pages)
        book.status = data.get('status', book.status)
        book.rating = data.get('rating')
        book.notes = data.get('notes')
        book.cover_url = data.get('cover_url')
        book.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(book.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Kitap güncellenirken hata oluştu', 'code': 'SERVER_ERROR'}), 500


@app.route('/api/books/<int:book_id>/progress', methods=['PUT'])
def update_book_progress(book_id):
    """Okunan sayfa güncelleme (quick action)"""
    try:
        book = Book.query.get(book_id)
        if not book or book.is_archived:
            return jsonify({'error': True, 'message': 'Kitap bulunamadı', 'code': 'NOT_FOUND'}), 404
        
        data = request.get_json()
        read_pages = data.get('read_pages')
        
        if read_pages is None or not isinstance(read_pages, int):
            return jsonify({'error': True, 'message': 'Okunan sayfa geçersiz', 'code': 'VALIDATION_ERROR'}), 400
        
        if read_pages < 0 or read_pages > book.total_pages:
            return jsonify({
                'error': True,
                'message': 'Okunan sayfa toplam sayfadan fazla olamaz',
                'code': 'VALIDATION_ERROR'
            }), 400
        
        book.read_pages = read_pages
        book.updated_at = datetime.utcnow()
        
        # Eğer tüm sayfalar okunmuşsa, durumu "Bitti" yap
        if read_pages == book.total_pages and book.status != 'Bitti':
            book.status = 'Bitti'
            book.reading_end_date = datetime.utcnow()
        
        db.session.commit()
        return jsonify(book.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Güncelleme başarısız oldu', 'code': 'SERVER_ERROR'}), 500


@app.route('/api/books/<int:book_id>/notes', methods=['PUT'])
def update_book_notes(book_id):
    """Kitap notlarını güncelle"""
    try:
        book = Book.query.get(book_id)
        if not book or book.is_archived:
            return jsonify({'error': True, 'message': 'Kitap bulunamadı', 'code': 'NOT_FOUND'}), 404
        
        data = request.get_json()
        notes = data.get('notes', '').strip() or None
        
        # Notes validasyonu
        if notes and len(notes) > 1000:
            return jsonify({'error': True, 'message': 'Not 1000 karakterden fazla olamaz', 'code': 'VALIDATION_ERROR'}), 400
        
        book.notes = notes
        book.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(book.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Not güncellenirken hata oluştu', 'code': 'SERVER_ERROR'}), 500


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Kitap silme (soft delete)"""
    try:
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'error': True, 'message': 'Kitap bulunamadı', 'code': 'NOT_FOUND'}), 404
        
        # Soft delete: is_archived = True
        book.is_archived = True
        book.updated_at = datetime.utcnow()
        db.session.commit()
        
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': True, 'message': 'Silme işlemi başarısız oldu', 'code': 'SERVER_ERROR'}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """KPI metrikleri"""
    try:
        total_books = Book.query.filter_by(is_archived=False).count()
        
        books = Book.query.filter_by(is_archived=False).all()
        total_read_pages = sum(book.read_pages for book in books)
        books_reading = Book.query.filter_by(status='Okunuyor', is_archived=False).count()
        books_finished = Book.query.filter_by(status='Bitti', is_archived=False).count()
        
        completion_percentage = 0
        if total_books > 0:
            completion_percentage = round((books_finished / total_books) * 100, 1)
        
        # Yıllık hedef (2026 için hedef 30 kitap)
        yearly_goal = 30
        yearly_goal_percentage = round((books_finished / yearly_goal) * 100, 1) if yearly_goal > 0 else 0
        
        return jsonify({
            'total_books': total_books,
            'total_read_pages': total_read_pages,
            'books_reading': books_reading,
            'completion_percentage': completion_percentage,
            'books_finished': books_finished,
            'yearly_goal': yearly_goal,
            'yearly_goal_percentage': yearly_goal_percentage
        }), 200
    except Exception as e:
        return jsonify({'error': True, 'message': 'İstatistikler alınamadı', 'code': 'SERVER_ERROR'}), 500


# ============== VALIDATION ==============

def validate_book_data(data):
    """Kitap verisi validasyonu"""
    errors = []
    
    # Title validasyonu
    title = data.get('title', '').strip() if isinstance(data.get('title'), str) else ''
    if not title or len(title) < 1 or len(title) > 150:
        errors.append('Kitap adı 1-150 karakter arasında olmalıdır')
    
    # Author validasyonu
    author = data.get('author', '').strip() if isinstance(data.get('author'), str) else ''
    if not author or len(author) < 1 or len(author) > 100:
        errors.append('Yazar adı 1-100 karakter arasında olmalıdır')
    
    # Genre validasyonu
    genre = data.get('genre')
    if genre not in VALID_GENRES:
        errors.append(f'Geçersiz türü. Geçerli türler: {", ".join(VALID_GENRES)}')
    
    # Total pages validasyonu
    try:
        total_pages = int(data.get('total_pages', 0))
        if total_pages < 1 or total_pages > 50000:
            errors.append('Toplam sayfa sayısı 1-50000 arasında olmalıdır')
    except (ValueError, TypeError):
        errors.append('Toplam sayfa sayısı geçerli bir sayı olmalıdır')
    
    # Read pages validasyonu
    try:
        read_pages = int(data.get('read_pages', 0))
        total_pages = int(data.get('total_pages', 0))
        if read_pages < 0 or read_pages > total_pages:
            errors.append('Okunan sayfa 0 ile toplam sayfa arasında olmalıdır')
    except (ValueError, TypeError):
        pass
    
    # Status validasyonu
    status = data.get('status', 'Okunacak')
    if status not in VALID_STATUSES:
        errors.append(f'Geçersiz durum. Geçerli durumlar: {", ".join(VALID_STATUSES)}')
    
    # Rating validasyonu
    if 'rating' in data and data['rating'] is not None:
        try:
            rating = int(data['rating'])
            if rating < 1 or rating > 5:
                errors.append('Puan 1-5 arasında olmalıdır')
        except (ValueError, TypeError):
            errors.append('Puan geçerli bir sayı olmalıdır')
    
    # Notes validasyonu
    notes = data.get('notes', '')
    if notes and len(notes) > 1000:
        errors.append('Not 1000 karakterden fazla olamaz')
    
    return errors


# ============== ERROR HANDLERS ==============

@app.errorhandler(404)
def not_found(error):
    """404 hatası"""
    return jsonify({'error': True, 'message': 'Sayfa bulunamadı', 'code': 'NOT_FOUND'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 hatası"""
    db.session.rollback()
    return jsonify({'error': True, 'message': 'Sunucu hatası oluştu', 'code': 'SERVER_ERROR'}), 500


# ============== MAIN ==============

if __name__ == '__main__':
    init_db()
    print("✓ Veritabanı hazırlandı")
    print("✓ Flask uygulaması başlatılıyor: http://localhost:5002")
    app.run(debug=True, host='127.0.0.1', port=5002)
