from models import db, Book
from datetime import datetime
import random


def populate_seed_data():
    """Veritabanına seed verisi yükle"""
    
    seed_books = [
        # Roman
        Book(
            title="Sapiens: İnsan Tarihine Kısa Bir Giriş",
            author="Yuval Noah Harari",
            genre="Bilim",
            total_pages=656,
            read_pages=450,
            status="Okunuyor",
            rating=5,
            notes="İnsanlık tarihini yeni bir perspektiften anlatan harika bir eser."
        ),
        Book(
            title="1984",
            author="George Orwell",
            genre="Roman",
            total_pages=328,
            read_pages=328,
            status="Bitti",
            rating=5,
            notes="Distopik bir dünya. Çok düşündüren bir kitap.",
            reading_end_date=datetime.utcnow()
        ),
        Book(
            title="Yüz Yılın Yalnızlığı",
            author="Gabriel García Márquez",
            genre="Roman",
            total_pages=432,
            read_pages=0,
            status="Okunacak",
            rating=None,
            notes=None
        ),
        Book(
            title="Savaş ve Barış",
            author="Lev Tolstoy",
            genre="Roman",
            total_pages=1200,
            read_pages=600,
            status="Okunuyor",
            rating=4,
            notes="Tarihi romanın en büyük örneklerinden biri."
        ),
        Book(
            title="Suç ve Ceza",
            author="Fyodor Dostoyevski",
            genre="Roman",
            total_pages=671,
            read_pages=0,
            status="Okunacak",
            rating=None,
            notes=None
        ),

        # Bilim
        Book(
            title="Gödel, Escher, Bach",
            author="Douglas Hofstadter",
            genre="Bilim",
            total_pages=777,
            read_pages=300,
            status="Okunuyor",
            rating=4,
            notes="Zihin ve bilişsel mimarinin etkileyici bir incelemesi."
        ),
        Book(
            title="Evrim Teorisi",
            author="Richard Dawkins",
            genre="Bilim",
            total_pages=688,
            read_pages=688,
            status="Bitti",
            rating=4,
            notes="Darwin'in evrim teorisinin açık ve net açıklaması.",
            reading_end_date=datetime.utcnow()
        ),
        Book(
            title="Fizik Nedir?",
            author="Brian Greene",
            genre="Bilim",
            total_pages=550,
            read_pages=0,
            status="Okunacak",
            rating=None,
            notes=None
        ),
        Book(
            title="Kozmik Araştırma",
            author="Carl Sagan",
            genre="Bilim",
            total_pages=496,
            read_pages=496,
            status="Bitti",
            rating=5,
            notes="Evren hakkında harika bir perspektif.",
            reading_end_date=datetime.utcnow()
        ),

        # Kişisel Gelişim
        Book(
            title="Atomic Habits",
            author="James Clear",
            genre="Kişisel Gelişim",
            total_pages=384,
            read_pages=384,
            status="Bitti",
            rating=5,
            notes="Küçük alışkanlıklar, büyük sonuçlar yaratır.",
            reading_end_date=datetime.utcnow()
        ),
        Book(
            title="7 Alışkanlık",
            author="Stephen Covey",
            genre="Kişisel Gelişim",
            total_pages=432,
            read_pages=200,
            status="Okunuyor",
            rating=4,
            notes="Verimli insanların ortak özellikleri."
        ),
        Book(
            title="Düşün ve Zengin Ol",
            author="Napoleon Hill",
            genre="Kişisel Gelişim",
            total_pages=324,
            read_pages=0,
            status="Okunacak",
            rating=None,
            notes=None
        ),

        # Felsefe
        Book(
            title="Platon: Sokrates'in Savunması",
            author="Platon",
            genre="Felsefe",
            total_pages=256,
            read_pages=256,
            status="Bitti",
            rating=4,
            notes="Felsefen temelleri hakkında temel bir eser.",
            reading_end_date=datetime.utcnow()
        ),
        Book(
            title="Ahlak Felsefesi",
            author="Peter Singer",
            genre="Felsefe",
            total_pages=428,
            read_pages=150,
            status="Okunuyor",
            rating=3,
            notes="Etik sorunlara farklı bakış açıları."
        ),
        Book(
            title="Varoluş Felsefesi",
            author="Jean-Paul Sartre",
            genre="Felsefe",
            total_pages=532,
            read_pages=0,
            status="Okunacak",
            rating=None,
            notes=None
        ),

        # Tarih
        Book(
            title="Günümüz Tarihçesi",
            author="Harari & Diamomd",
            genre="Tarih",
            total_pages=528,
            read_pages=350,
            status="Okunuyor",
            rating=4,
            notes="Modern dünyanın nasıl oluştuğunun harika bir anlatımı."
        ),
        Book(
            title="Birinci Dünya Savaşı",
            author="Margaret MacMillan",
            genre="Tarih",
            total_pages=656,
            read_pages=0,
            status="Okunacak",
            rating=None,
            notes=None
        ),

        # Psikoloji
        Book(
            title="Düşünen İnsan",
            author="Daniel Kahneman",
            genre="Psikoloji",
            total_pages=656,
            read_pages=656,
            status="Bitti",
            rating=5,
            notes="İnsan karar alma süreçlerinin en iyi analizi.",
            reading_end_date=datetime.utcnow()
        ),
        Book(
            title="Davranış Psikolojisi",
            author="B.F. Skinner",
            genre="Psikoloji",
            total_pages=488,
            read_pages=0,
            status="Okunacak",
            rating=None,
            notes=None
        ),
    ]

    # Seed verisini veritabanına ekle
    try:
        for book in seed_books:
            db.session.add(book)
        db.session.commit()
        print(f"✓ {len(seed_books)} kitap başarıyla yüklendi!")
    except Exception as e:
        db.session.rollback()
        print(f"✗ Seed verisi yüklenirken hata: {e}")
