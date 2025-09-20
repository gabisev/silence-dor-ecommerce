// JavaScript pour l'administration des informations du site

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Administration des informations du site chargée');
    
    // Validation en temps réel des URLs
    const socialUrlFields = [
        'id_facebook_url',
        'id_instagram_url', 
        'id_twitter_url',
        'id_linkedin_url'
    ];
    
    socialUrlFields.forEach(function(fieldId) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('blur', function() {
                validateUrl(field);
            });
        }
    });
    
    // Validation des emails
    const emailField = document.getElementById('id_contact_email');
    if (emailField) {
        emailField.addEventListener('blur', function() {
            validateEmail(emailField);
        });
    }
    
    // Validation des numéros de téléphone
    const phoneField = document.getElementById('id_contact_phone');
    if (phoneField) {
        phoneField.addEventListener('blur', function() {
            validatePhone(phoneField);
        });
    }
    
    // Auto-formatage du symbole de devise
    const currencySymbolField = document.getElementById('id_currency_symbol');
    if (currencySymbolField) {
        currencySymbolField.addEventListener('input', function() {
            formatCurrencySymbol(currencySymbolField);
        });
    }
    
    // Prévisualisation en temps réel
    const previewFields = [
        'id_site_name',
        'id_site_tagline',
        'id_site_description'
    ];
    
    previewFields.forEach(function(fieldId) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('input', function() {
                updatePreview();
            });
        }
    });
});

function validateUrl(field) {
    const url = field.value.trim();
    if (url && !isValidUrl(url)) {
        showFieldError(field, 'URL invalide');
    } else {
        clearFieldError(field);
    }
}

function validateEmail(field) {
    const email = field.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        showFieldError(field, 'Format d\'email invalide');
    } else {
        clearFieldError(field);
    }
}

function validatePhone(field) {
    const phone = field.value.trim();
    const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
    
    if (phone && !phoneRegex.test(phone)) {
        showFieldError(field, 'Format de téléphone invalide');
    } else {
        clearFieldError(field);
    }
}

function formatCurrencySymbol(field) {
    const symbol = field.value.trim();
    if (symbol && symbol.length > 5) {
        field.value = symbol.substring(0, 5);
    }
}

function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.style.color = '#dc3545';
    errorDiv.style.fontSize = '12px';
    errorDiv.style.marginTop = '5px';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
    field.style.borderColor = '#dc3545';
}

function clearFieldError(field) {
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    field.style.borderColor = '';
}

function updatePreview() {
    const siteName = document.getElementById('id_site_name')?.value || 'Silence d\'Or';
    const siteTagline = document.getElementById('id_site_tagline')?.value || 'Votre boutique de luxe en ligne';
    const siteDescription = document.getElementById('id_site_description')?.value || 'Description du site';
    
    const previewElement = document.querySelector('.field-preview_info');
    if (previewElement) {
        previewElement.innerHTML = `
            <div style="background: linear-gradient(135deg, #e91e63, #ffc107); color: white; padding: 20px; border-radius: 10px; margin: 10px 0;">
                <h4 style="margin: 0 0 10px 0; font-size: 24px; font-weight: bold;">${siteName}</h4>
                <p style="margin: 0 0 5px 0; font-style: italic; opacity: 0.9;">${siteTagline}</p>
                <p style="margin: 0; opacity: 0.8;">${siteDescription.length > 100 ? siteDescription.substring(0, 100) + '...' : siteDescription}</p>
            </div>
        `;
    }
}

// Fonction utilitaire pour formater les numéros
function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length >= 10) {
        value = value.replace(/(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/, '+$1 $2 $3 $4 $5');
    }
    input.value = value;
}

// Auto-sauvegarde (optionnel)
function autoSave() {
    const form = document.querySelector('form');
    if (form) {
        const formData = new FormData(form);
        
        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            if (response.ok) {
                console.log('✅ Auto-sauvegarde réussie');
            }
        })
        .catch(error => {
            console.error('❌ Erreur auto-sauvegarde:', error);
        });
    }
}

// Sauvegarde automatique toutes les 30 secondes (optionnel)
// setInterval(autoSave, 30000);

// Amélioration de l'expérience utilisateur
function enhanceFormFields() {
    // Ajouter des indicateurs visuels pour les champs obligatoires
    const requiredFields = document.querySelectorAll('input[required], textarea[required]');
    requiredFields.forEach(function(field) {
        const fieldBox = field.closest('.field-box');
        if (fieldBox) {
            fieldBox.classList.add('required-field');
        }
    });
    
    // Améliorer la navigation au clavier
    const allFields = document.querySelectorAll('input, textarea, select');
    allFields.forEach(function(field) {
        field.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && field.tagName !== 'TEXTAREA') {
                e.preventDefault();
                const nextField = field.closest('.field-box').nextElementSibling?.querySelector('input, textarea, select');
                if (nextField) {
                    nextField.focus();
                }
            }
        });
    });
    
    // Ajouter des tooltips d'aide
    const helpElements = document.querySelectorAll('.help');
    helpElements.forEach(function(help) {
        const helpText = help.textContent.trim();
        if (helpText) {
            help.setAttribute('title', helpText);
            help.classList.add('help-tooltip');
        }
    });
    
    // Validation en temps réel pour les emails
    const emailFields = document.querySelectorAll('input[type="email"]');
    emailFields.forEach(function(field) {
        field.addEventListener('blur', function() {
            const email = field.value;
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (email && !emailRegex.test(email)) {
                field.classList.add('error');
                showFieldError(field, 'Format d\'email invalide');
            } else {
                field.classList.remove('error');
                clearFieldError(field);
            }
        });
    });
    
    // Validation en temps réel pour les URLs
    const urlFields = document.querySelectorAll('input[type="url"]');
    urlFields.forEach(function(field) {
        field.addEventListener('blur', function() {
            const url = field.value;
            if (url && !isValidUrl(url)) {
                field.classList.add('error');
                showFieldError(field, 'Format d\'URL invalide');
            } else {
                field.classList.remove('error');
                clearFieldError(field);
            }
        });
    });
}

// Initialiser les améliorations
document.addEventListener('DOMContentLoaded', function() {
    enhanceFormFields();
});
