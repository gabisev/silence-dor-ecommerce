# Guide de dépannage - Silence d'Or E-commerce

## Erreurs courantes et solutions

### 1. Erreurs d'importation

#### `ModuleNotFoundError: No module named 'dj_database_url'`
```bash
pip install dj-database-url==2.1.0
```

#### `ModuleNotFoundError: No module named 'decouple'`
```bash
pip install python-decouple==3.8
```

#### `ModuleNotFoundError: No module named 'stripe'`
```bash
pip install stripe==7.8.0
```

### 2. Erreurs de base de données

#### `django.db.utils.OperationalError: no such table`
```bash
python manage.py makemigrations
python manage.py migrate
```

#### `django.db.utils.IntegrityError: UNIQUE constraint failed`
```bash
# Supprimer la base de données et recréer
rm db.sqlite3
python manage.py migrate
```

### 3. Erreurs de configuration

#### `django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty`
```bash
# Copier le fichier d'environnement
cp env.example .env
# Éditer .env et ajouter une SECRET_KEY
```

#### `django.core.exceptions.ImproperlyConfigured: You're using the staticfiles app without having set the STATIC_ROOT setting`
```bash
# Créer le dossier staticfiles
mkdir staticfiles
python manage.py collectstatic --noinput
```

### 4. Erreurs de permissions

#### `PermissionError: [Errno 13] Permission denied`
```bash
# Sur Linux/Mac
chmod +x scripts/setup.sh
chmod +x scripts/deploy.sh

# Sur Windows
# Exécuter en tant qu'administrateur
```

### 5. Erreurs de dépendances

#### `pip install` échoue
```bash
# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances une par une
pip install Django==4.2.7
pip install djangorestframework==3.14.0
# etc...
```

### 6. Erreurs de serveur

#### `django.core.exceptions.AppRegistryNotReady`
```bash
# Vérifier que Django est correctement configuré
python manage.py check
```

#### `django.db.utils.OperationalError: database is locked`
```bash
# Arrêter le serveur Django et relancer
# Ou supprimer le fichier de verrou de la base de données
```

### 7. Erreurs Stripe

#### `stripe.error.AuthenticationError: No API key provided`
```bash
# Ajouter les clés Stripe dans .env
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### 8. Erreurs de templates

#### `django.template.exceptions.TemplateDoesNotExist`
```bash
# Vérifier que les templates sont dans le bon dossier
# templates/base.html doit exister
```

### 9. Erreurs de fichiers statiques

#### `django.contrib.staticfiles.utils.StaticFilesStorageError`
```bash
# Collecter les fichiers statiques
python manage.py collectstatic --noinput
```

### 10. Erreurs de migrations

#### `django.db.migrations.exceptions.InconsistentMigrationHistory`
```bash
# Réinitialiser les migrations
python manage.py migrate --fake-initial
```

## Commandes de diagnostic

### Vérifier la configuration
```bash
python manage.py check
python manage.py check --deploy
```

### Tester la configuration
```bash
python scripts/test_setup.py
```

### Vérifier les migrations
```bash
python manage.py showmigrations
python manage.py migrate --plan
```

### Vérifier les URLs
```bash
python manage.py show_urls
```

## Logs et débogage

### Activer le mode debug
```bash
# Dans .env
DEBUG=True
```

### Vérifier les logs
```bash
# Les logs sont dans logs/django.log
tail -f logs/django.log
```

### Tester l'API
```bash
# Tester l'endpoint de base
curl http://localhost:8000/api/

# Tester l'endpoint des produits
curl http://localhost:8000/api/products/
```

## Support

Si vous rencontrez d'autres erreurs :

1. Vérifiez les logs Django
2. Consultez la documentation Django
3. Vérifiez la configuration dans `.env`
4. Testez avec le script de diagnostic

### Contact
- Email : support@silence-dor.com
- Documentation : https://docs.djangoproject.com/

