# TBF Obligations V2

Basketbol Oyun Kuralları ve Yorumları Yönetim Paneli

## Özellikler

- Kullanıcı yönetimi ve kimlik doğrulama
- Günlük soru sistemi
- Ekolarka soruları
- PDF yönetimi
- Admin paneli

## Teknolojiler

- Django 4.2.7+
- PostgreSQL (Production)
- SQLite (Development)
- WhiteNoise (Static files)

## Kurulum (Local Development)

1. Repository'yi klonlayın:
```bash
git clone https://github.com/Sey1tayd/tbf_v2.git
cd tbf_v2
```

2. Virtual environment oluşturun ve aktive edin:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. Environment variables dosyasını oluşturun:
```bash
cp .env.example .env
```

5. `.env` dosyasını düzenleyin ve gerekli değerleri girin.

6. Veritabanı migrasyonlarını çalıştırın:
```bash
python manage.py migrate
```

7. Superuser oluşturun:
```bash
python manage.py createsuperuser
```

8. Statik dosyaları toplayın:
```bash
python manage.py collectstatic --noinput
```

9. Development sunucusunu başlatın:
```bash
python manage.py runserver
```

## Railway Deployment

### Adımlar:

1. Railway hesabınızda yeni bir proje oluşturun

2. GitHub repository'nizi bağlayın:
   - Railway dashboard'da "New Project" → "Deploy from GitHub repo"
   - Repository'nizi seçin

3. PostgreSQL servisi ekleyin:
   - Railway dashboard'da "New" → "Database" → "Add PostgreSQL"
   - PostgreSQL servisi otomatik olarak `DATABASE_URL` environment variable'ını ayarlayacaktır

4. Environment variables ekleyin (Railway dashboard → Variables):
   - `SECRET_KEY`: Django secret key (güçlü bir key oluşturun)
   - `DEBUG`: `False` (production için)
   - `ALLOWED_HOSTS`: Railway domain'iniz (örn: `yourapp.up.railway.app`)

5. Deploy edin:
   - Railway otomatik olarak değişiklikleri algılayıp deploy edecektir
   - İlk deploy sonrası migrasyonları çalıştırın:
     - Railway dashboard → Deployments → Latest → "View Logs" → "Run Command"
     - Veya Railway CLI kullanarak: `railway run python manage.py migrate`

6. Superuser oluşturun:
   - Railway dashboard → "Run Command" → `python manage.py createsuperuser`

7. Static files otomatik olarak collectstatic ile toplanacaktır (Railway build sırasında)

### Railway CLI ile Deploy:

```bash
# Railway CLI'yi yükleyin
npm i -g @railway/cli

# Railway'e login olun
railway login

# Projeyi başlatın
railway init

# Deploy edin
railway up
```

## Notlar

- Production ortamında `DEBUG=False` olmalıdır
- `SECRET_KEY` asla git'e commit edilmemelidir
- Railway PostgreSQL bağlantısı otomatik olarak `DATABASE_URL` üzerinden yapılır
- Static dosyalar WhiteNoise ile serve edilir
- Media dosyaları için Railway'de bir volume veya S3 benzeri bir servis kullanmanız gerekebilir

## Lisans

Bu proje özel bir projedir.