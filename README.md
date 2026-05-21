# DişAsistanım

DişAsistanım, hasta ve hekim tarafı için basit bir diş sağlığı yönetimi uygulamasıdır. FastAPI ile yazılmış backend, Jinja2 ile oluşturulmuş HTML şablonları ve statik frontend dosyaları içerir. Veritabanı işlemleri stored procedure'ler ile gerçekleştirilir.

## Özellikler
- Hasta ve hekim panelleri (HTML şablonları)
- Fırçalama takibi ve istatistikleri
- Diş haritası görüntüleme
- Hekim tedavi notları ve hasta geçmişi
- FastAPI tabanlı REST API ve HTML sayfa uçları

## Gereksinimler
- Python 3.10+ (veya projede kullanılan versiyon)
- MySQL sunucusu
- Sanal ortam (recommended)

Projede kullanılan Python paketleri `requirements.txt` içinde listelenmiştir:

- fastapi
- uvicorn
- mysql-connector-python
- pydantic
- python-dotenv
- jinja2

## Kurulum
1. Depoyu klonlayın veya dosyaları indirin.
2. Proje kökünde sanal ortam oluşturun ve etkinleştirin:

Windows (PowerShell):

```powershell
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& .\venv\Scripts\Activate.ps1
```

3. Gerekli paketleri yükleyin:

```powershell
pip install -r requirements.txt
```

4. Veritabanı kurulumu:
- `database/db_kurulum.sql` dosyasını kullanarak veritabanı ve gerekli tabloları/stored procedure'leri oluşturun.
- Bir MySQL kullanıcısı yaratın ve yetki verin.

5. Ortam değişkenleri (.env) oluşturun:
Projede `backend/dal/database.py` içinde `python-dotenv` ile `.env` dosyası yüklenmektedir. Proje köküne bir `.env` dosyası ekleyin ve aşağıdaki örneği doldurun:

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=kullanici
DB_PASS=sifre
DB_NAME=disasistanim_db
```

## Çalıştırma
Geliştirme ortamında FastAPI uygulamasını `uvicorn` ile çalıştırabilirsiniz:

```powershell
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

- API kök: `http://localhost:8000/`
- Swagger/OpenAPI (dokümantasyon): `http://localhost:8000/docs`
- Yaygın kullanılan ön yüz sayfaları örnekleri:
  - Harita: `http://localhost:8000/haritam`
  - Fırçalama sayfası: `http://localhost:8000/fircalama`
  - Giriş sayfası: `http://localhost:8000/login`
  - Hekim paneli: `http://localhost:8000/hekim/dashboard`
  - Hasta profil: `http://localhost:8000/profil`

> Not: `backend/dal/database.py` dosyası `.env` içindeki `DB_*` değişkenlerini okur. Veritabanı bağlantı hataları için konsoldaki çıktıları kontrol edin.

## Proje Yapısı (Özet)
- `backend/` — FastAPI uygulaması ve iş mantığı
- `backend/dal/` — Veri erişim katmanı (DB bağlantıları, stored procedure çağrıları)
- `backend/bll/` — İş mantığı (iş kuralları)
- `frontend/` — HTML şablonları, statik dosyalar (CSS/JS)
- `database/` — SQL kurulum scriptleri
- `requirements.txt` — Python bağımlılıkları

## Sık Karşılaşılan Sorunlar
- Veritabanı bağlantısı çalışmıyorsa `.env` içindeki bilgileri kontrol edin ve MySQL servisinin çalıştığından emin olun.
- Statik dosyalar veya şablonlar yüklenmiyorsa uygulamayı proje kökünden çalıştırdığınızdan emin olun (çalışma dizini önemlidir).

## Katkıda Bulunma
Katkı yapmak isterseniz fork ve pull request yoluyla değişiklik gönderebilirsiniz. Küçük düzeltmeler, hata raporları veya yeni özellik önerileri memnuniyetle kabul edilir.

## İletişim
Projeyle ilgili sorular için repository sahibiyle iletişime geçin.

## Geliştirici: 
Aslı AYDIN