# 📚 Kitap & Okuma Alışkanlığı Portalı - Proje Rehberi (Project Blueprint)

Bu doküman, kişisel kütüphane yönetimini sağlayan, okuma hedeflerini dinamik metriklerle takip eden ve okuma alışkanlıklarını görselleştiren web uygulamasının fonksiyonel ve teknik mimarisidir.

---

## 1. Kesin Teknik Kurallar ve Standartlar
- **Backend Çatısı:** Python 3 (Flask).
- **Giriş Noktası:** `application.py`.
- **Veritabanı Motoru:** Yalnızca **SQLite**. Harici servisler (PostgreSQL, MySQL vb.) veya Docker kesinlikle kullanılmayacaktır.
- **Veri Depolama Konumu:** Veritabanı dosyası `data/app.db` yolunda tutulacaktır. `data/` klasörü uygulama başlatıldığında Python tarafından (`os.makedirs`) otomatik oluşturulacaktır.
- **ORM Katmanı:** `Flask-SQLAlchemy`.
- **Frontend Teknolojileri:** Bootstrap 5 (CDN), Bootstrap Icons (CDN), Chart.js (CDN) ve özel CSS.
- **Versiyon Disiplini:** Her mantıksal birim (model, route, şablon, seed scripti) tamamlandığında anlamlı Git commit mesajları ile versiyonlanacaktır.

---

## 2. Kullanıcı Deneyimi ve Arayüz Mimarisi (UI/UX)

Uygulama tek sayfa odaklı, modern, kart tabanlı ve göz yormayan nötr tonlara (adaçayı yeşili, taş grisi, kırık beyaz ve lacivert aksanlar) sahip bir gösterge paneli (Dashboard) sunacaktır.

### A. Üst Gösterge Paneli (KPI İstatistik Sayaçları)
Sayfanın en üstünde kullanıcının okuma durumunu özetleyen 4 ana metrik kartı yer alacaktır:
1. **Toplam Kitap:** Kütüphanedeki tüm kitapların sayısı.
2. **Okunan Sayfa:** Biten ve devam eden kitaplardan okunan toplam sayfa miktarı.
3. **Şu An Okunanlar:** Aktif olarak okuma sürecinde olan kitap sayısı.
4. **Tamamlanma Oranı (%):** Kütüphanedeki kitapların kaçta kaçının bittiğini gösteren yüzde rozeti.

### B. Grafik ve Analiz Alanı (Chart.js)
- **Tür Dağılımı (Doughnut Chart):** Kütüphanedeki kitapların kategorilere göre dağılımı (Örn: %40 Roman, %30 Kişisel Gelişim, %20 Bilim, %10 Felsefe).
- **Okuma Durumu Özeti (Bar Chart):** "Bitti", "Okunuyor" ve "Okunacak" durumlarındaki kitap adetlerinin görsel karşılaştırması.

### C. Kitap Listesi ve Akıllı Kart Tasarımı
Her kitap, modern bir grid düzeninde kart olarak listelenecektir:
- **Kitap Başlığı ve Yazar:** Kalın ve okunaklı tipografi.
- **Tür Rozeti (Badge):** Kategoriye özel renkli etiket.
- **Dinamik İlerleme Çubuğu (Progress Bar):** `(read_pages / total_pages) * 100` formülüyle hesaplanan canlı yüzde çubuğu (Örn: 240/400 sayfa - %60).
- **Puanlama:** 1 ile 5 arasında sarı yıldız ikonları.
- **Durum Butonları:** Tek tıkla okunan sayfa sayısını artırma modalı, düzenleme ve silme aksiyonları.

### D. Canlı Arama ve Filtreleme Bölümü
- **Metin Araması:** Kitap adı veya yazar adına göre anlık filtreleme.
- **Durum Hapları (Filter Pills):** `[Tümü]` `[Okunuyor]` `[Okunacaklar]` `[Bitenler]`.
- **Kategori Açılır Menüsü:** Belirli türe göre filtreleme.

### E. Hızlı Kitap Ekleme (Modal Formu)
Sağ üstteki "+ Yeni Kitap Ekle" butonuna basıldığında açılan temiz bir modal:
- Kitap Adı (Metin)
- Yazar (Metin)
- Tür (Açılır menü: Roman, Kişisel Gelişim, Bilim, Felsefe, Tarih, Psikoloji vb.)
- Toplam Sayfa Sayısı (Sayı)
- Okunan Sayfa Sayısı (Varsayılan 0)
- Durum (Okunuyor, Okunacak, Bitti)
- Değerlendirme / Puan (1-5 arası seçim)
- Kişisel Not / Favori Alıntı (Metin kutusu)

---

## 3. Veritabanı Şeması (`models.py`)

### `Book` Tablosu
| Alan Adı | Tip | Kısıtlar | Açıklama |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto Increment | Benzersiz kimlik |
| `title` | String(150) | Not Null | Kitabın tam adı |
| `author` | String(100) | Not Null | Yazar adı |
| `genre` | String(50) | Not Null | Kitap türü |
| `total_pages` | Integer | Not Null | Toplam sayfa sayısı |
| `read_pages` | Integer | Not Null, Default: 0 | Okunmuş sayfa sayısı |
| `status` | String(20) | Not Null, Default: 'Okunacak' | 'Okunuyor', 'Bitti', 'Okunacak' |
| `rating` | Integer | Nullable (1-5) | Kullanıcı puanı |
| `notes` | Text | Nullable | Alıntı veya kişisel inceleme |
| `created_at` | DateTime | Default: datetime.utcnow | Eklenme zamanı |

---

## 4. Klasör ve Modül Hiyerarşisi
```text
kitap-takip/
├── data/
│   └── app.db               # SQLite veritabanı (otomatik oluşur)
├── static/
│   ├── css/
│   │   └── style.css        # Özel renk paleti ve kart stilleri
│   └── js/
│       └── main.js          # Chart.js başlatıcı ve filtreleme betikleri
├── templates/
│   ├── base.html            # Genel iskelet, navbar ve CDN bağlantıları
│   └── index.html           # Dashboard, sayaçlar, grafikler ve kitap kartları
├── .gitignore               # .venv/, *.db ve cache dışlama kuralları
├── application.py           # Flask route yönetimi ve hesaplamalar
├── models.py                # SQLAlchemy Book modeli
├── proje_rehberi.md         # Proje anayasası ve mimari doküman
└── seed.py                  # 15-20 adet gerçekçi kitap yükleme scripti
```

---

## 5. Mimari Eksiklikler ve Kritik Geliştirme Detayları

Aşağıda geliştirmeye başlamadan önce **mutlaka** tamamlanması gereken kritik detaylar listelenmiştir.

### A. API Endpoints ve Request/Response Contract

#### CRUD İşlemleri için Gerekli Endpoints:
```
GET    /                              # Dashboard ana sayfası
GET    /api/books                     # Tüm kitapları listele (filtreleme query params destekli)
GET    /api/books?status=Okunuyor     # Durum filtrelemesi
GET    /api/books?genre=Roman         # Tür filtrelemesi
GET    /api/books?search=Sapiens      # Metin araması (title + author)
POST   /api/books                     # Yeni kitap ekleme
GET    /api/books/<id>                # Spesifik kitap detayları
PUT    /api/books/<id>                # Kitap tam güncelleme
PUT    /api/books/<id>/progress       # Okunan sayfayı artırma (quick action)
DELETE /api/books/<id>                # Kitap silme
GET    /api/stats                     # KPI metrikleri (dashboard sayaçları)
```

#### POST /api/books - Request Body:
```json
{
  "title": "string (1-150 chars, required)",
  "author": "string (1-100 chars, required)",
  "genre": "string (enum: Roman|Kişisel Gelişim|Bilim|Felsefe|Tarih|Psikoloji)",
  "total_pages": "integer (1-50000, required)",
  "read_pages": "integer (0-total_pages, default: 0)",
  "status": "string (enum: Okunuyor|Okunacak|Bitti, default: Okunacak)",
  "rating": "integer (1-5) | null",
  "notes": "string (0-1000 chars) | null"
}
```

#### POST /api/books - Response (201 Created):
```json
{
  "id": 1,
  "title": "Sapiens",
  "author": "Yuval Noah Harari",
  "genre": "Bilim",
  "total_pages": 656,
  "read_pages": 0,
  "status": "Okunacak",
  "rating": null,
  "notes": null,
  "created_at": "2026-09-21T10:30:00Z",
  "progress_percentage": 0
}
```

#### GET /api/stats - Response:
```json
{
  "total_books": 15,
  "total_read_pages": 3250,
  "books_reading": 3,
  "completion_percentage": 45.5
}
```

#### Error Response (400 Bad Request):
```json
{
  "error": true,
  "message": "Okunan sayfa toplam sayfadan fazla olamaz",
  "code": "VALIDATION_ERROR",
  "field": "read_pages"
}
```

### B. Input Validation ve Kısıtlamalar

| Alan | Min | Max | Tip | Zorunlu | Kural |
|------|-----|-----|-----|---------|-------|
| `title` | 1 | 150 | String | ✅ | Boşluk trimle, unique olmalı mı? |
| `author` | 1 | 100 | String | ✅ | Boşluk trimle |
| `genre` | - | - | Enum | ✅ | Sadece tanımlı türler kabul et |
| `total_pages` | 1 | 50000 | Integer | ✅ | Pozitif tam sayı |
| `read_pages` | 0 | `total_pages` | Integer | ✅ | 0 ile total_pages arasında |
| `status` | - | - | Enum | ✅ | `Okunuyor`, `Okunacak`, `Bitti` |
| `rating` | 1 | 5 | Integer | ❌ | Sadece 1-5 ya da null |
| `notes` | 0 | 1000 | String | ❌ | Null olabilir, HTML sanitize edilmeli |

### C. Veritabanı Şeması Güncellemeleri (Eksik Alanlar)

Mevcut `Book` tablosuna aşağıdaki alanlar **eklenmelidir**:

```python
# models.py güncellemesi:
class Book(db.Model):
    # ... mevcut alanlar ...
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Son güncelleme
    reading_start_date = db.Column(db.DateTime, nullable=True)  # Okumaya başlama tarihi
    reading_end_date = db.Column(db.DateTime, nullable=True)    # Okuma bitişi
    is_archived = db.Column(db.Boolean, default=False)          # Soft delete (silme yerine arşivle)
```

### D. Error Handling Strategy

**HTTP Status Codes:**
- `200 OK` - Başarılı GET/PUT
- `201 Created` - Başarılı POST
- `204 No Content` - Başarılı DELETE
- `400 Bad Request` - Validation hatası (invalid input)
- `404 Not Found` - Kitap bulunamadı
- `500 Internal Server Error` - Sunucu hatası (log'la)

**Backend Error Handling:**
- Tüm route'larda try-except bloğu
- SQLAlchemy exception'larını (IntegrityError, etc.) catch et
- Kullanıcı-dostu Türkçe hata mesajları dön
- Sunucu hatalarını log'a yaz

### E. Database Initialization Flow

```
application.py çalıştırıldığında:
1. os.makedirs('data/', exist_ok=True)  # data/ klasörü oluştur
2. app.app_context() ile Flask context'ine gir
3. db.create_all()  # Şema oluştur (varsa skip)
4. DB boş mu kontrol et
   └─ Boşsa: seed.py'i auto-run et (15-20 kitap yükle)
   └─ Değilse: "Database ready" mesajı
5. Flask dev server başlat (debug=True)
```

### F. Frontend Form Validation & UX States

**Kitap Ekle/Düzenle Modalında:**
- ✅ **Real-time validation** (onChange)
  - Başlık: "Boş olamaz" → "1-150 karakter arası"
  - Toplam Sayfa: "Pozitif sayı" + "Max 50000"
  - Okunan Sayfa: "0 ile toplam arasında"
- ✅ **Loading State**: Form submit sırasında spinner, input'lar disabled
- ✅ **Success Feedback**: Green toast "Kitap eklendi!" (3 sn sonra fade-out)
- ✅ **Error Alert**: Red alert box, campo hata mesajı inline
- ✅ **Delete Confirmation**: Modal ile "Silmek istediğinize emin misiniz?"

### G. Security Policy

- **Input Sanitization**: Tüm text input'ları HTML sanitize et (Flask escape yeterli mi?)
- **CSRF Token**: Form POST'ları CSRF token ile koru (Flask-WTF)
- **SQL Injection**: SQLAlchemy parameterized queries kullan (risk az)
- **Debug Mode**: Production'da `debug=False`
- **Secret Key**: `application.py`'de `app.config['SECRET_KEY']` = secure random string

### H. Gerekli Dosyalar ve Konfigürasyon

**requirements.txt:**
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
python-dotenv==1.0.0
```

**.env (örnek):**
```
FLASK_APP=application.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-min-32-char
DEBUG=True
```

**Veritabanı İnitialize Script (seed.py):**
- 15-20 adet çeşitli kitap oluştur
- Durum mix'i: Bitti (60%), Okunuyor (25%), Okunacak (15%)
- Genre mix'i: Roman, Bilim, Kişisel Gelişim, Tarih vs.

### I. Geliştirme Sırasında Kontrol Edilecek Noktalar

- [ ] API endpoint'ler Postman/curl ile test edildi
- [ ] Validation kuralları hem backend hem frontend'de uygulandı
- [ ] Form hatası durumunda kullanıcı geri bildirim alıyor
- [ ] Silme işleminde confirmation modal çıkıyor
- [ ] Dashboard KPI'ları gerçek veriye dayanıyor
- [ ] Grafikler Chart.js ile render ediliyor
- [ ] Arama/filtreleme canlı çalışıyor
- [ ] SQLite DB otomatik oluşuyor ve seed data yükleniyor
- [ ] `.gitignore` `.venv/`, `*.db`, `__pycache__/` dışlıyor