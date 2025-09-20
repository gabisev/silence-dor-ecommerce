// Silence d'Or - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeCart();
    initializeWishlist();
    initializeSearch();
    initializeNotifications();
    initializeAnimations();
});

// Cart functionality
function initializeCart() {
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            addToCart(productId);
        });
    });
}

function addToCart(productId, quantity = 1) {
    // Vérifier si l'utilisateur est connecté
    if (!isUserAuthenticated()) {
        showNotification('Vous devez vous connecter pour ajouter des produits au panier.', 'warning');
        // Rediriger vers la page de connexion
        setTimeout(() => {
            window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
        }, 2000);
        return;
    }
    
    // Récupérer la quantité depuis l'input si disponible
    const quantityInput = document.getElementById(`quantity-${productId}`);
    if (quantityInput) {
        quantity = parseInt(quantityInput.value) || 1;
    }
    
    const button = document.querySelector(`[data-product-id="${productId}"]`);
    const originalText = button.innerHTML;
    
    // Show loading state
    button.innerHTML = '<span class="spinner"></span>';
    button.disabled = true;
    
    // Make API call
    fetch('/cart/api/add/' + productId + '/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showNotification(data.message, 'success');
            updateCartBadge();
        } else if (data.error) {
            showNotification(data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Une erreur est survenue', 'error');
    })
    .finally(() => {
        // Restore button state
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

// Wishlist functionality
function initializeWishlist() {
    const wishlistButtons = document.querySelectorAll('.wishlist-btn');
    
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            toggleWishlist(productId, this);
        });
    });
}

function toggleWishlist(productId, button) {
    // Vérifier si l'utilisateur est connecté
    if (!isUserAuthenticated()) {
        showNotification('Vous devez vous connecter pour ajouter des produits à votre liste de souhaits.', 'warning');
        // Rediriger vers la page de connexion
        setTimeout(() => {
            window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
        }, 2000);
        return;
    }
    
    const isActive = button.classList.contains('active');
    const url = isActive ? 
        `/cart/api/wishlist/remove/${productId}/` : 
        `/cart/api/wishlist/add/${productId}/`;
    
    fetch(url, {
        method: isActive ? 'DELETE' : 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showNotification(data.message, 'success');
            button.classList.toggle('active');
        } else if (data.error) {
            showNotification(data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Une erreur est survenue', 'error');
    });
}

// Search functionality
function initializeSearch() {
    const searchForm = document.querySelector('form[role="search"]');
    const searchInput = document.querySelector('input[type="search"]');
    
    if (searchForm && searchInput) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = searchInput.value.trim();
            if (query) {
                window.location.href = `/search/?q=${encodeURIComponent(query)}`;
            }
        });
        
        // Real-time search suggestions
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    fetchSearchSuggestions(query);
                }, 300);
            }
        });
    }
}

function fetchSearchSuggestions(query) {
    fetch(`/api/products/search/?q=${encodeURIComponent(query)}`)
    .then(response => response.json())
    .then(data => {
        if (data.products) {
            showSearchSuggestions(data.products);
        }
    })
    .catch(error => {
        console.error('Search error:', error);
    });
}

function showSearchSuggestions(products) {
    // Implementation for search suggestions dropdown
    console.log('Search suggestions:', products);
}

// Notifications
function initializeNotifications() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.classList.contains('show')) {
                alert.classList.remove('show');
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        }, 5000);
    });
}

function showNotification(message, type = 'info') {
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        const alert = document.querySelector('.alert:last-of-type');
        if (alert) {
            alert.classList.remove('show');
            setTimeout(() => {
                alert.remove();
            }, 300);
        }
    }, 5000);
}

// Animations
function initializeAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements with animation class
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

// Cart badge update
function updateCartBadge() {
    fetch('/cart/api/')
    .then(response => response.json())
    .then(data => {
        const badge = document.querySelector('.cart-badge, .badge');
        if (badge && data.total_items !== undefined) {
            badge.textContent = data.total_items;
            if (data.total_items > 0) {
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }
    })
    .catch(error => {
        console.error('Error updating cart badge:', error);
    });
}

// Utility functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function formatPrice(price) {
    return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'EUR'
    }).format(price);
}

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

// Product image lazy loading
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Initialize additional features
document.addEventListener('DOMContentLoaded', function() {
    initializeLazyLoading();
    initializeFormValidation();
});

// Utility functions
function isUserAuthenticated() {
    // Vérifier si l'utilisateur est connecté en regardant les éléments du DOM
    const loginLink = document.querySelector('a[href*="/accounts/login/"]');
    const logoutLink = document.querySelector('a[href*="/accounts/logout/"]');
    
    // Si on trouve un lien de déconnexion, l'utilisateur est connecté
    return logoutLink !== null;
}

function showLoginRequired() {
    showNotification('Vous devez vous connecter pour ajouter des produits au panier.', 'warning');
    // Rediriger vers la page de connexion
    setTimeout(() => {
        window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
    }, 2000);
}

// Export functions for global use
window.SilenceDor = {
    addToCart,
    toggleWishlist,
    showNotification,
    formatPrice,
    updateCartBadge,
    isUserAuthenticated,
    showLoginRequired
};
