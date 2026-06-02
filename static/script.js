// Selected books management
let selectedBooks = JSON.parse(sessionStorage.getItem('selectedBooks') || '[]');

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadInitialBooks();
    setupSearch();
    updateSelectionUI();
});

// ============================================
// BOOK SELECTION MANAGEMENT
// ============================================

function addBook(title) {
    if (selectedBooks.length >= 5) {
        showNotification('You can select maximum 5 books', 'warning');
        return;
    }

    if (!selectedBooks.includes(title)) {
        selectedBooks.push(title);
        saveSelection();
        updateSelectionUI();
        showNotification(`✓ "${title}" added to your selection`, 'success');
    } else {
        showNotification(`"${title}" is already selected`, 'info');
    }
}

function removeBook(title) {
    selectedBooks = selectedBooks.filter(book => book !== title);
    saveSelection();
    updateSelectionUI();
    showNotification(`✗ "${title}" removed from selection`, 'info');
}

function saveSelection() {
    sessionStorage.setItem('selectedBooks', JSON.stringify(selectedBooks));
}

function updateSelectionUI() {
    const count = selectedBooks.length;
    const countBadge = document.getElementById('selectionCount');
    const recommendBtn = document.getElementById('recommendBtn');
    const selectedList = document.getElementById('selectedBooksList');

    // Update count badge
    if (countBadge) {
        countBadge.textContent = `${count}/5`;
    }

    // Update button state
    if (recommendBtn) {
        recommendBtn.disabled = count < 3;
        if (count >= 3) {
            recommendBtn.classList.add('btn-success');
        } else {
            recommendBtn.classList.remove('btn-success');
        }
    }

    // Update selected books display
    if (selectedList) {
        if (selectedBooks.length === 0) {
            selectedList.innerHTML = `
                <div class="empty-state text-center text-muted py-5 w-100">
                    <i class="fas fa-inbox fa-3x mb-3"></i>
                    <p>Select 3-5 books to get started</p>
                </div>
            `;
        } else {
            selectedList.innerHTML = selectedBooks.map((book, index) => `
                <div class="book-card-selected" data-book="${escapeHtml(book)}">
                    <button class="btn btn-sm btn-light" 
                            onclick="removeBook('${book.replace(/'/g, "\\'")}')">
                        <i class="fas fa-times"></i>
                    </button>
                    <div class="book-card-selected" style="margin-top: 0.5rem;">
                        <h6>${escapeHtml(book)}</h6>
                    </div>
                </div>
            `).join('');
        }
    }

    // Update book card buttons
    updateBookCardStates();
}

function updateBookCardStates() {
    document.querySelectorAll('.btn-add-book').forEach(btn => {
        const bookTitle = btn.getAttribute('data-book-title');
        if (selectedBooks.includes(bookTitle)) {
            btn.textContent = '✓ Selected';
            btn.classList.add('selected');
            btn.disabled = true;
        } else {
            btn.textContent = '+ Add to Selection';
            btn.classList.remove('selected');
            btn.disabled = false;
        }
    });
}

// ============================================
// SEARCH FUNCTIONALITY
// ============================================

function setupSearch() {
    const localInput = document.getElementById('localSearchInput');
    const googleInput = document.getElementById('googleSearchInput');

    if (localInput) {
        localInput.addEventListener('input', debounce(handleLocalSearch, 300));
        localInput.addEventListener('blur', () => {
            setTimeout(() => {
                const results = document.getElementById('localSearchResults');
                if (results) results.classList.remove('active');
            }, 200);
        });
    }

    if (googleInput) {
        googleInput.addEventListener('input', debounce(handleGoogleSearch, 500));
        googleInput.addEventListener('blur', () => {
            setTimeout(() => {
                const results = document.getElementById('googleSearchResults');
                if (results) results.classList.remove('active');
            }, 200);
        });
    }
}

async function handleLocalSearch(e) {
    const query = e.target.value.trim();
    const resultsContainer = document.getElementById('localSearchResults');

    if (query.length < 2) {
        resultsContainer.classList.remove('active');
        return;
    }

    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query })
        });

        const data = await response.json();
        displaySearchResults(data.results, resultsContainer);
    } catch (error) {
        console.error('Search error:', error);
    }
}

async function handleGoogleSearch(e) {
    const query = e.target.value.trim();
    const resultsContainer = document.getElementById('googleSearchResults');

    if (query.length < 2) {
        resultsContainer.classList.remove('active');
        return;
    }

    try {
        const response = await fetch('/api/google-search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query })
        });

        const data = await response.json();
        if (data.error) {
            resultsContainer.innerHTML = `
                <div class="search-result-item">
                    <div class="search-result-info">
                        <p class="text-danger"><i class="fas fa-exclamation-circle"></i> ${data.error}</p>
                    </div>
                </div>
            `;
        } else {
            displaySearchResults(data.results, resultsContainer, true);
        }
    } catch (error) {
        console.error('Google search error:', error);
    }
}

function displaySearchResults(results, container, isGoogle = false) {
    if (!results || results.length === 0) {
        container.innerHTML = `
            <div class="search-result-item">
                <div class="search-result-info">
                    <p class="text-muted">No results found</p>
                </div>
            </div>
        `;
        container.classList.add('active');
        return;
    }

    container.innerHTML = results.map(book => {
        const imageUrl = book.image_url || 'https://via.placeholder.com/50x75?text=Book';
        return `
            <div class="search-result-item">
                <div class="search-result-info">
                    <div class="search-result-title">${escapeHtml(book.title)}</div>
                    <div class="search-result-author">${escapeHtml(book.authors)}</div>
                </div>
                <button class="search-result-btn" onclick="addBook('${book.title.replace(/'/g, "\\'")}')">
                    Add
                </button>
            </div>
        `;
    }).join('');

    container.classList.add('active');
}

// ============================================
// INITIAL BOOKS LOADING
// ============================================

async function loadInitialBooks() {
    const catalog = document.getElementById('booksCatalog');
    if (!catalog) return;

    try {
        // For demo purposes, create a sample of books
        // In production, this would fetch from the backend
        displayCatalogBooks([]);
    } catch (error) {
        console.error('Error loading books:', error);
    }
}

function displayCatalogBooks(books) {
    const catalog = document.getElementById('booksCatalog');
    if (!catalog) return;

    // Create a sample catalog with placeholder cards
    const sampleHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
            <p class="text-muted">
                <i class="fas fa-info-circle"></i>
                Use the search features above to find and select books.
            </p>
            <p class="small text-secondary">
                Local search queries the dataset, Google search uses the Books API.
            </p>
        </div>
    `;
    catalog.innerHTML = sampleHTML;
}

// ============================================
// RECOMMENDATIONS
// ============================================

async function generateRecommendations() {
    if (selectedBooks.length < 3) {
        showNotification('Please select at least 3 books', 'warning');
        return;
    }

    const btn = document.getElementById('recommendBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';

    try {
        // Save selection to session storage for the recommendations page
        sessionStorage.setItem('selectedBooks', JSON.stringify(selectedBooks));

        // Navigate to recommendations page
        window.location.href = '/recommendations';
    } catch (error) {
        console.error('Error:', error);
        showNotification('An error occurred', 'danger');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-magic"></i> Generate Recommendations';
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type = 'info') {
    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show`;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(toast);

    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.remove();
    }, 4000);
}

// Make functions global
window.addBook = addBook;
window.removeBook = removeBook;
window.generateRecommendations = generateRecommendations;
