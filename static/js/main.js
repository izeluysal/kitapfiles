// ==================== GLOBAL STATE ====================
let allBooks = [];
let currentEditingBookId = null;
let genreChart = null;
let statusChart = null;
const formModal = new bootstrap.Modal(document.getElementById('formModal'));
const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));

const GENRE_COLORS = {
    'Roman': '#D67E7E',
    'Bilim': '#6BA8D4',
    'Kişisel Gelişim': '#B89FBD',
    'Felsefe': '#8FA67E',
    'Tarih': '#C89D7C',
    'Psikoloji': '#7FA6D4'
};

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadStats();
    loadBooks();
    initializeCharts();
});

// ==================== EVENT LISTENERS ====================
function initializeEventListeners() {
    // Add Book Button
    document.getElementById('addBookBtn').addEventListener('click', openAddModal);

    // Form Submit
    document.getElementById('bookForm').addEventListener('submit', handleFormSubmit);

    // Search & Filter
    document.getElementById('searchInput').addEventListener('input', filterBooks);
    document.getElementById('genreFilter').addEventListener('change', filterBooks);

    // Status Filter Pills
    document.querySelectorAll('.filter-pill').forEach(pill => {
        pill.addEventListener('click', function() {
            document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
            this.classList.add('active');
            filterBooks();
        });
    });

    // Delete Modal Confirm
    document.getElementById('confirmDeleteBtn').addEventListener('click', confirmDelete);

    // Notes Character Counter
    document.getElementById('notes').addEventListener('input', function() {
        document.getElementById('noteChars').textContent = this.value.length;
    });

    // Modal Reset on Close
    document.getElementById('formModal').addEventListener('hidden.bs.modal', resetForm);
}

// ==================== DATA LOADING ====================
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        document.getElementById('totalBooks').textContent = stats.total_books;
        document.getElementById('totalReadPages').textContent = stats.total_read_pages;
        document.getElementById('booksReading').textContent = stats.books_reading;
        document.getElementById('completionPercent').textContent = stats.completion_percentage + '%';
    } catch (error) {
        console.error('İstatistikler yüklenemedi:', error);
    }
}

async function loadBooks(status = '', genre = '', search = '') {
    try {
        let url = '/api/books?';
        const params = new URLSearchParams();
        
        if (status) params.append('status', status);
        if (genre) params.append('genre', genre);
        if (search) params.append('search', search);

        if (params.toString()) url += params.toString();

        const response = await fetch(url);
        allBooks = await response.json();

        renderBooks(allBooks);
        updateCharts();
    } catch (error) {
        console.error('Kitaplar yüklenemedi:', error);
        showToast('Kitaplar yüklenirken hata oluştu', false);
    }
}

// ==================== RENDERING ====================
function renderBooks(books) {
    const container = document.getElementById('booksContainer');
    container.innerHTML = '';

    if (books.length === 0) {
        document.getElementById('emptyState').style.display = 'block';
        return;
    }

    document.getElementById('emptyState').style.display = 'none';

    books.forEach(book => {
        const genreClass = book.genre.toLowerCase().replace(' ', '-');
        const statusClass = book.status.toLowerCase();
        const ratingStars = renderRatingStars(book.rating);

        const genreBadgeClass = [
            'genre-badge',
            book.genre === 'Roman' ? 'roman' :
            book.genre === 'Bilim' ? 'bilim' :
            book.genre === 'Kişisel Gelişim' ? 'kisisel-gelisim' :
            book.genre === 'Felsefe' ? 'felsefe' :
            book.genre === 'Tarih' ? 'tarih' :
            book.genre === 'Psikoloji' ? 'psikoloji' : ''
        ].join(' ');

        const card = document.createElement('div');
        card.className = 'col-md-6 col-lg-4 mb-3';
        card.innerHTML = `
            <div class="book-card" data-id="${book.id}">
                <div class="book-card-body">
                    <h5 class="book-title">${escapeHtml(book.title)}</h5>
                    <p class="book-author">${escapeHtml(book.author)}</p>

                    <div class="book-info">
                        <span class="${genreBadgeClass}">${book.genre}</span>
                        <span class="book-status ${statusClass}">${book.status}</span>
                    </div>

                    <div class="progress-container">
                        <div class="progress-label">
                            <span>Okuma İlerlemesi</span>
                            <strong>${book.read_pages}/${book.total_pages} sayfa</strong>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill" style="width: ${book.progress_percentage}%"></div>
                        </div>
                        <div style="text-align: right; font-size: 0.8rem; color: #666; margin-top: 0.25rem;">
                            ${book.progress_percentage}%
                        </div>
                    </div>

                    <div class="book-rating">
                        <div class="rating-stars" title="${book.rating ? book.rating + '/5' : 'Puanlandırılmamış'}">
                            ${ratingStars}
                        </div>
                    </div>

                    <div class="book-actions">
                        ${book.status === 'Bitti' || book.read_pages >= book.total_pages 
                            ? `<div class="completion-badge">
                                <i class="bi bi-check-circle-fill me-2"></i>✓ Tamamlandı
                              </div>`
                            : `<button class="action-btn-primary add-pages" data-id="${book.id}" title="İlerleme Gir">
                                <i class="bi bi-plus-lg me-2"></i>İlerleme Gir
                              </button>`
                        }
                        <div class="action-buttons-group">
                            <button class="action-btn-icon edit" data-id="${book.id}" title="Düzenle">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="action-btn-icon delete" data-id="${book.id}" title="Sil">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.appendChild(card);

        // Attach event listeners
        const addPagesBtn = card.querySelector('.add-pages');
        if (addPagesBtn) {
            addPagesBtn.addEventListener('click', () => openAddPagesModal(book.id, book.read_pages, book.total_pages));
        }
        card.querySelector('.edit').addEventListener('click', () => openEditModal(book.id));
        card.querySelector('.delete').addEventListener('click', () => openDeleteModal(book.id));
    });
}

function renderRatingStars(rating) {
    if (!rating) return '<span class="rating-empty">☆☆☆☆☆</span>';
    
    let stars = '';
    for (let i = 1; i <= 5; i++) {
        stars += i <= rating ? '★' : '☆';
    }
    return stars;
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ==================== FILTERING ====================
function filterBooks() {
    const search = document.getElementById('searchInput').value.trim();
    const genre = document.getElementById('genreFilter').value;
    const status = document.querySelector('.filter-pill.active')?.dataset.status || '';

    loadBooks(status, genre, search);
}

// ==================== MODALS ====================
function openAddModal() {
    currentEditingBookId = null;
    resetForm();
    document.getElementById('modalTitle').textContent = 'Yeni Kitap Ekle';
    document.getElementById('submitBtnText').textContent = 'Kaydet';
    formModal.show();
}

function openEditModal(bookId) {
    const book = allBooks.find(b => b.id === bookId);
    if (!book) return;

    currentEditingBookId = bookId;
    document.getElementById('modalTitle').textContent = 'Kitap Düzenle';
    document.getElementById('submitBtnText').textContent = 'Güncelle';

    // Fill form with book data
    document.getElementById('title').value = book.title;
    document.getElementById('author').value = book.author;
    document.getElementById('genre').value = book.genre;
    document.getElementById('total_pages').value = book.total_pages;
    document.getElementById('read_pages').value = book.read_pages;
    document.getElementById('status').value = book.status;
    document.getElementById('rating').value = book.rating || '';
    document.getElementById('notes').value = book.notes || '';
    document.getElementById('noteChars').textContent = (book.notes || '').length;

    formModal.show();
}

function openAddPagesModal(bookId, currentRead, totalPages) {
    const newRead = prompt(`Kaç sayfa daha okudunuz? (Şu anki: ${currentRead}/${totalPages})`, currentRead.toString());
    
    if (newRead === null) return;
    
    const readPages = parseInt(newRead);
    if (isNaN(readPages) || readPages < 0 || readPages > totalPages) {
        showToast('Geçersiz sayfa sayısı!', false);
        return;
    }

    updateBookProgress(bookId, readPages);
}

function openDeleteModal(bookId) {
    window.bookToDelete = bookId;
    deleteModal.show();
}

function resetForm() {
    document.getElementById('bookForm').reset();
    document.getElementById('formAlertContainer').innerHTML = '';
    document.getElementById('noteChars').textContent = '0';
    currentEditingBookId = null;
    
    // Clear validation states
    document.querySelectorAll('.form-control, .form-select').forEach(input => {
        input.classList.remove('is-invalid');
        const feedback = input.nextElementSibling;
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.textContent = '';
        }
    });
}

// ==================== FORM SUBMISSION ====================
async function handleFormSubmit(e) {
    e.preventDefault();

    const formData = {
        title: document.getElementById('title').value.trim(),
        author: document.getElementById('author').value.trim(),
        genre: document.getElementById('genre').value,
        total_pages: parseInt(document.getElementById('total_pages').value),
        read_pages: parseInt(document.getElementById('read_pages').value) || 0,
        status: document.getElementById('status').value,
        rating: document.getElementById('rating').value ? parseInt(document.getElementById('rating').value) : null,
        notes: document.getElementById('notes').value.trim() || null
    };

    try {
        const method = currentEditingBookId ? 'PUT' : 'POST';
        const url = currentEditingBookId ? `/api/books/${currentEditingBookId}` : '/api/books';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (!response.ok) {
            showFormError(result.message);
            return;
        }

        formModal.hide();
        resetForm();
        showToast(currentEditingBookId ? 'Kitap güncellendi!' : 'Kitap eklendi!');
        loadStats();
        loadBooks();
    } catch (error) {
        console.error('Form hatası:', error);
        showFormError('İşlem sırasında hata oluştu');
    }
}

function showFormError(message) {
    const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="bi bi-exclamation-circle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    document.getElementById('formAlertContainer').innerHTML = alertHtml;
}

// ==================== CRUD OPERATIONS ====================
async function updateBookProgress(bookId, readPages) {
    try {
        const response = await fetch(`/api/books/${bookId}/progress`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ read_pages: readPages })
        });

        if (!response.ok) throw new Error('Hata oluştu');

        showToast('Okuma ilerleme güncellendi!');
        loadStats();
        loadBooks();
    } catch (error) {
        console.error('Güncelleme hatası:', error);
        showToast('Güncelleme başarısız oldu', false);
    }
}

function confirmDelete() {
    const bookId = window.bookToDelete;
    if (!bookId) return;

    deleteBook(bookId);
    deleteModal.hide();
}

async function deleteBook(bookId) {
    try {
        const response = await fetch(`/api/books/${bookId}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Hata oluştu');

        showToast('Kitap silindi');
        loadStats();
        loadBooks();
    } catch (error) {
        console.error('Silme hatası:', error);
        showToast('Silme işlemi başarısız oldu', false);
    }
}

// ==================== CHARTS ====================
function initializeCharts() {
    const genreCtx = document.getElementById('genreChart').getContext('2d');
    const statusCtx = document.getElementById('statusChart').getContext('2d');

    genreChart = new Chart(genreCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: Object.values(GENRE_COLORS),
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        font: { size: 12 },
                        padding: 20
                    }
                }
            }
        }
    });

    statusChart = new Chart(statusCtx, {
        type: 'bar',
        data: {
            labels: ['Okunacak', 'Okunuyor', 'Bitti'],
            datasets: [{
                label: 'Kitap Sayısı',
                data: [],
                backgroundColor: ['#d4edda', '#ffeaa7', '#d1ecf1'],
                borderColor: ['#28a745', '#ffc107', '#17a2b8'],
                borderWidth: 1,
                borderRadius: 6,
                barThickness: 16,
                maxBarThickness: 18
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });

    updateCharts();
}

function updateCharts() {
    if (!allBooks.length) {
        genreChart.data.labels = [];
        genreChart.data.datasets[0].data = [];
        statusChart.data.datasets[0].data = [];
        genreChart.update();
        statusChart.update();
        return;
    }

    // Genre Chart
    const genreCounts = {};
    allBooks.forEach(book => {
        genreCounts[book.genre] = (genreCounts[book.genre] || 0) + 1;
    });

    genreChart.data.labels = Object.keys(genreCounts);
    genreChart.data.datasets[0].data = Object.values(genreCounts);
    genreChart.data.datasets[0].backgroundColor = Object.keys(genreCounts).map(g => GENRE_COLORS[g]);
    genreChart.update();

    // Status Chart
    const statusCounts = {
        'Okunacak': allBooks.filter(b => b.status === 'Okunacak').length,
        'Okunuyor': allBooks.filter(b => b.status === 'Okunuyor').length,
        'Bitti': allBooks.filter(b => b.status === 'Bitti').length
    };

    statusChart.data.datasets[0].data = [
        statusCounts['Okunacak'],
        statusCounts['Okunuyor'],
        statusCounts['Bitti']
    ];
    statusChart.update();
}

// ==================== UTILITIES ====================
function showToast(message, success = true) {
    const toastEl = document.getElementById('successToast');
    const messageEl = document.getElementById('toastMessage');
    
    messageEl.textContent = message;
    if (!success) {
        toastEl.classList.remove('bg-success');
        toastEl.classList.add('bg-danger');
    } else {
        toastEl.classList.add('bg-success');
        toastEl.classList.remove('bg-danger');
    }

    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}
