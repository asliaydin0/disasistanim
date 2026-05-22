import random
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from backend.dal.database import get_db_connection

app = FastAPI(title="DişAsistanım API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statik dosyalar (CSS, JS) ve HTML şablonları için ayarlar
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")


# --- SAYFALAR (HTML DÖNDÜREN UÇLAR) ---
@app.get("/haritam")
def haritam_sayfasini_goster(request: Request):
    # Artık request=request ve name="sayfa.html" şeklinde açıkça belirtiyoruz
    return templates.TemplateResponse(request=request, name="hasta/haritam.html")

@app.get("/analiz")
def analiz_sayfasini_goster(request: Request):
    """Diş analiz sayfasını ekrana basar."""
    return templates.TemplateResponse(request=request, name="hasta/analiz.html")


# --- API UÇLARI (JSON DÖNDÜREN UÇLAR) ---

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="anasayfa.html")

@app.get("/db-test")
def test_db():
    conn = get_db_connection()
    if conn:
        conn.close()
        return {"mesaj": "Veritabanı bağlantısı BAŞARILI! 🚀"}
    return {"mesaj": "Veritabanı bağlantısı BAŞARISIZ! ❌"}

@app.get("/api/dis-haritasi/{hasta_id}")
def dis_haritasini_getir(hasta_id: int):
    """Hastanın diş haritasını Stored Procedure ile getirir."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanı bağlantısı yok")
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('sp_DisHaritasiGetir', [hasta_id])
        
        disler = []
        for result in cursor.stored_results():
            disler = result.fetchall()
            
        cursor.close()
        conn.close()
        
        # SADECE LİSTEYİ DÖNDÜRÜYORUZ (Sözlük içine koymadan, JavaScript şaşırmasın diye)
        return disler
        
    except Exception as e:
        print(f"🔥 MySQL HATASI (Diş Haritası): {str(e)}")
        if conn.is_connected():
            conn.close()
        raise HTTPException(status_code=500, detail=str(e))

# Arayüzden gelecek verinin yapısını (Modelini) tanımlıyoruz
class DisGuncelleme(BaseModel):
    hasta_id: int
    dis_numarasi: int
    durum: str

class FircalamaEkle(BaseModel):
    hasta_id: int
    zaman_dilimi: str

class FircalamaSil(BaseModel):
    kayit_id: int

class TedaviNotuEkle(BaseModel):
    hekim_id: int
    hasta_id: int
    not_metni: str

class LoginVerisi(BaseModel):
    email: str
    password: str
    role: str

class AnalizTalebi(BaseModel):
    hasta_id: int
    dis_numarasi: int
    sikayet: str


@app.post('/api/analiz')
def analiz_istegi(istek: AnalizTalebi):
    """Kullanıcının seçtiği diş ve şikayete göre dinamik analiz önerisi döner."""
    sikayet = istek.sikayet
    dis_no = istek.dis_numarasi

    # Bölge temelli değerlendirme
    if dis_no <= 8:
        bolge = 'üst ön diş bölgesi'
    elif dis_no <= 16:
        bolge = 'üst arka diş bölgesi'
    elif dis_no <= 24:
        bolge = 'alt arka diş bölgesi'
    else:
        bolge = 'alt ön diş bölgesi'

    temel_oneri = {
        'Diş ağrısı': {
            'title': 'Diş ağrısı analizi',
            'analysis': f'{bolge} üzerinde hassasiyet ve potansiyel çürük riski var.',
            'advice': 'Hemen bir muayene planlayın ve sıcak-soğuk hassasiyetini takip edin.',
            'priority': 'Yüksek'
        },
        'Diş eti kanaması': {
            'title': 'Diş eti kanaması değerlendirmesi',
            'analysis': f'{bolge} çevresinde diş eti iltihabı belirtileri olabilir.',
            'advice': 'Diş eti bakımını güçlendir, tuzlu suyla gargara yap ve 1 hafta sonra tekrar kontrol et.',
            'priority': 'Orta'
        },
        'Hassasiyet': {
            'title': 'Hassasiyet analizi',
            'analysis': f'{bolge} için mine erozyonu veya açığa çıkmış dentin gösterebilir.',
            'advice': 'Florürlü diş macunu kullan, aşındırıcı olmayan fırçalama teknikleri uygula.',
            'priority': 'Orta'
        },
        'Çürük riski': {
            'title': 'Çürük riski raporu',
            'analysis': f'{bolge} için yüksek çürük olasılığı tespit edildi.',
            'advice': 'Hızlı bir klinik kontrol ve gerekirse dolgu planı oluştur.',
            'priority': 'Yüksek'
        },
        'Dolgu sonrası ağrı': {
            'title': 'Dolgu sonrası ağrı incelemesi',
            'analysis': f'{bolge} çevresinde dolgu uyumsuzluğu veya pulpa hassasiyeti olabilir.',
            'advice': 'Dolgunun 48 saat içinde düzelmemesi halinde hekimle iletişime geç.',
            'priority': 'Orta'
        },
        'Ağız kokusu': {
            'title': 'Ağız kokusu değerlendirmesi',
            'analysis': f'{bolge} bölgesinde plak birikimi ya da diş eti problemleri olabilir.',
            'advice': 'Dil temizliği yap, ağız gargarası kullan ve protez/ dolgu yüzeylerini kontrol et.',
            'priority': 'Orta'
        },
        'Sıcak/soğuk hassasiyeti': {
            'title': 'Sıcak/soğuk hassasiyeti analizi',
            'analysis': f'{bolge} için mine incelmesi veya çatlak olasılığı değerlendirilmelidir.',
            'advice': 'Duyarlı diş için hassasiyet azaltıcı ürün kullan, gerekli ise hekim değerlendirmesi al.',
            'priority': 'Orta'
        }
    }

    if sikayet not in temel_oneri:
        sikayet = 'Diş ağrısı'

    secim = temel_oneri[sikayet]
    risk_factor = 60 + (8 if secim['priority'] == 'Yüksek' else 0) + (5 if 'arka' in bolge else 0)
    risk_score = min(100, risk_factor)

    next_step = []
    if secim['priority'] == 'Yüksek':
        next_step.append('Hekimle hızlı randevu al.')
    if sikayet == 'Diş eti kanaması':
        next_step.append('Günde iki kez nazik diş eti masajı yap.')
    if sikayet == 'Hassasiyet' or sikayet == 'Sıcak/soğuk hassasiyeti':
        next_step.append('Florürlü hassasiyet giderici macun kullan.')

    return {
        'dis_numarasi': dis_no,
        'sikayet': sikayet,
        'analysis_title': secim['title'],
        'analysis_summary': secim['analysis'],
        'recommendation': secim['advice'],
        'priority': secim['priority'],
        'risk_score': risk_score,
        'next_steps': next_step or ['Kayıtları takip et ve durum kötüleşirse tekrar analiz iste.']
    }


@app.post("/api/dis-guncelle")
def dis_durumu_guncelle(veri: DisGuncelleme):
    """Arayüzden gelen diş güncelleme talebini Stored Procedure ile veritabanına yazar."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanına bağlanılamadı")
    
    try:
        cursor = conn.cursor()
        # Kesinlikle UPDATE yazmıyoruz, Procedure çağırıyoruz!
        cursor.callproc('sp_DisDurumuGuncelle', [veri.hasta_id, veri.dis_numarasi, veri.durum])
        conn.commit() # Değişikliği kaydet
        
        cursor.close()
        conn.close()
        
        return {"mesaj": "Diş başarıyla güncellendi", "durum": "success"}

    except Exception as e:
        if conn.is_connected():
            conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    

# --- FIRÇALAMA TAKİBİ UÇLARI ---

@app.get("/fircalama")
def fircalama_sayfasini_goster(request: Request):
    """Fırçalama HTML sayfasını ekrana basar."""
    return templates.TemplateResponse(request=request, name="hasta/fircalama.html")


@app.post("/api/fircalama-ekle")
def fircalama_kaydet(veri: FircalamaEkle):
    """Stored Procedure kullanarak fırçalama kaydı ekler (INSERT Kuralı)."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanı hatası")
    try:
        cursor = conn.cursor()
        # Doğrudan INSERT yok, Procedure var!
        cursor.callproc('sp_FircalamaEkle', [veri.hasta_id, veri.zaman_dilimi])
        conn.commit()
        cursor.close()
        conn.close()
        return {"mesaj": "Fırçalama kaydedildi", "durum": "success"}
    except Exception as e:
        if conn.is_connected():
            conn.close()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/fircalama-sil")
def fircalama_sil(veri: FircalamaSil):
    """Stored Procedure kullanarak fırçalama kaydını siler (DELETE Kuralı)."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanı hatası")
    try:
        cursor = conn.cursor()
        # Doğrudan DELETE yok, Procedure var!
        cursor.callproc('sp_FircalamaSil', [veri.kayit_id])
        conn.commit()
        cursor.close()
        conn.close()
        return {"mesaj": "Kayıt silindi", "durum": "success"}
    except Exception as e:
        if conn.is_connected():
            conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/api/fircalama-istatistik/{hasta_id}")
def fircalama_istatistik_getir(hasta_id: int):
    """Hastanın fırçalama verilerini ve AI önerilerini getirir."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanı hatası")
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('sp_FircalamaIstatistik', [hasta_id])
        
        istatistik = None
        for result in cursor.stored_results():
            istatistik = result.fetchone()
            
        cursor.close()
        conn.close()

        if not istatistik:
            istatistik = {
                "bugun_sabah_id": None, "bugun_aksam_id": None,
                "sabah_toplam": 0, "aksam_toplam": 0, "seri": 0, "basari_yuzdesi": 0
            }

        # --- AI KARAR MEKANİZMASI (PHP'den Python'a Uyarlama) ---
        ai_tips = [
            "Gece fırçalaması, tükürük akışının azaldığı uyku sırasında diş minesini korumak için en kritik adımdır.",
            "Fırçanı 45 derecelik açıyla tutarak diş eti çizgisine masaj yapman, plak oluşumunu %30 daha fazla engeller.",
            "Dil temizliği, ağız kokusuna neden olan bakterilerin %80'ini yok eder. Unutma!",
            "Diş fırçanı her 3 ayda bir veya hastalık sonrası mutlaka değiştirmelisin."
        ]

        ai_response = {}
        basari = istatistik["basari_yuzdesi"] or 0
        sabah_top = istatistik["sabah_toplam"] or 0
        aksam_top = istatistik["aksam_toplam"] or 0
        seri = istatistik["seri"] or 0

        if basari >= 90:
            ai_response = {"icon": "fa-crown text-warning", "title": "Zirvedesin, Aslı!", "bg": "rgba(255, 193, 7, 0.08)", "text": "Muazzam bir disiplin! Son 7 günde neredeyse hiç fire vermedin. Dişlerin şu an bir kale kadar korunaklı."}
        elif aksam_top < sabah_top and aksam_top < 3:
            ai_response = {"icon": "fa-moon text-danger", "title": "Gece Nöbeti Eksik", "bg": "rgba(220, 53, 69, 0.06)", "text": "Akşam fırçalamalarını sabahçılara göre daha çok ihmal ediyorsun. Gece bakterileri çok hızlı ürer, bu akşam bir istisna yapalım mı?"}
        elif seri >= 3:
            ai_response = {"icon": "fa-fire text-danger", "title": f"{seri} Günlük Seri!", "bg": "rgba(253, 126, 20, 0.06)", "text": f"Harika gidiyorsun! Tam {seri} gündür dişlerine vakit ayırıyorsun. Bu seriyi bozmamak için bugünkü kayıtlarını tamamla."}
        else:
            ai_response = {"icon": "fa-lightbulb text-info", "title": "Biliyor muydun?", "bg": "rgba(23, 162, 184, 0.05)", "text": random.choice(ai_tips)}

        # Arayüze JSON Dönüşü
        return {
            "bugun_sabah": bool(istatistik["bugun_sabah_id"]),
            "bugun_sabah_id": istatistik["bugun_sabah_id"],
            "bugun_aksam": bool(istatistik["bugun_aksam_id"]),
            "bugun_aksam_id": istatistik["bugun_aksam_id"],
            "sabah_toplam": sabah_top,
            "aksam_toplam": aksam_top,
            "seri": seri,
            "basari_yuzdesi": basari,
            "ai": ai_response
        }

    except Exception as e:
        if conn.is_connected():
            conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    


# --- HEKİM (DOKTOR) MODÜLÜ UÇLARI ---

@app.get("/hekim/dashboard")
def hekim_dashboard_goster(request: Request):
    """Hekim ana yönetim panelini (Dashboard) ekrana basar."""
    return templates.TemplateResponse(request=request, name="hekim/dashboard.html")

@app.get("/api/hekim/hasta-listesi")
def hekim_hasta_listesi_getir():
    """Stored Procedure ile hastaları ve sağlık puanlarını getirir."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanı hatası")
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('sp_HekimHastaListesi')
        
        hastalar = []
        for result in cursor.stored_results():
            hastalar = result.fetchall()
            
        cursor.close()
        conn.close()
        return {"mesaj": "Liste getirildi", "hastalar": hastalar}
        
    except Exception as e:
        print(f"🔥 MySQL HATASI (Hekim Liste): {str(e)}")
        if conn.is_connected():
            conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/hekim/hasta-detay/{hasta_id}")
def hasta_detay_sayfasi(request: Request, hasta_id: int):
    """Hasta detay şablonunu ekrana basar."""
    return templates.TemplateResponse(request=request, name="hekim/hasta_detay.html", context={"hasta_id": hasta_id})

@app.get("/api/hekim/hasta-gecmis/{hasta_id}")
def hasta_islem_gecmisi(hasta_id: int):
    """Hastanın tüm diş geçmişini (Log) getirir."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.callproc('sp_HastaIslemGecmisiGetir', [hasta_id])
    gecmis = []
    for result in cursor.stored_results():
        gecmis = result.fetchall()
    cursor.close()
    conn.close()
    return {"gecmis": gecmis}

@app.get("/api/hekim/tedavi-notlari/{hasta_id}")
def tedavi_notlarini_getir(hasta_id: int):
    """Hekimlerin bu hastaya düştüğü notları getirir."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.callproc('sp_TedaviNotlariGetir', [hasta_id])
    notlar = []
    for result in cursor.stored_results():
        notlar = result.fetchall()
    cursor.close()
    conn.close()
    return {"notlar": notlar}

@app.post("/api/hekim/tedavi-notu-ekle")
def tedavi_notu_kaydet(veri: TedaviNotuEkle):
    """Yeni bir tedavi notu/talimatı ekler."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.callproc('sp_TedaviNotuEkle', [veri.hekim_id, veri.hasta_id, veri.not_metni])
        conn.commit()
        cursor.close()
        conn.close()
        return {"durum": "success", "mesaj": "Not başarıyla eklendi"}
    except Exception as e:
        print(f"Hata: {str(e)}")
        return {"durum": "error", "mesaj": str(e)}
        
    
@app.get("/login")
def login_sayfasi(request: Request):
    """Giriş sayfasını ekrana basar. (Kendi özel tasarımı olduğu için base.html kullanmaz)"""
    return templates.TemplateResponse(request=request, name="auth/login.html")

@app.post("/api/login")
def giris_yap(veri: LoginVerisi):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('sp_KullaniciGiris', [veri.email, veri.role])
        
        kullanici = None
        for result in cursor.stored_results():
            kullanici = result.fetchone()
            
        cursor.close()
        conn.close()

        if kullanici:
            # Gerçek projelerde burada Hash kontrolü (örn: bcrypt) yapılır.
            # Şimdilik test aşamasında olduğumuz için düz metin kontrolü yapıyoruz.
            if kullanici['Sifre_Hash'] == veri.password:
                return {
                    "durum": "success", 
                    "mesaj": "Giriş başarılı, yönlendiriliyorsunuz...",
                    "rol": kullanici['Rol_Adi'],
                    "kullanici_id": kullanici['Kullanici_ID']
                }
            else:
                return {"durum": "error", "mesaj": "Şifre hatalı!"}
        else:
            return {"durum": "error", "mesaj": f"Bu e-posta adresiyle kayıtlı bir {veri.role} bulunamadı!"}
            
    except Exception as e:
        print(f"Hata: {str(e)}")
        return {"durum": "error", "mesaj": "Sistemsel bir hata oluştu."}
    
# --- HASTA PROFİL UÇLARI ---

@app.get("/profil")
def hasta_profil_sayfasi(request: Request):
    """Hastanın modern profil ve yönetim panelini ekrana basar."""
    return templates.TemplateResponse(request=request, name="hasta/profil.html")

@app.get("/api/hasta/profil/{hasta_id}")
def hasta_profil_getir(hasta_id: int):
    """Hastanın profil bilgilerini Stored Procedure ile getirir."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanı hatası")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('sp_HastaProfilGetir', [hasta_id])
        
        profil = None
        for result in cursor.stored_results():
            profil = result.fetchone()
            
        cursor.close()
        conn.close()
        
        if profil:
            return profil
        else:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
            
    except Exception as e:
        if conn.is_connected():
            conn.close()
        raise HTTPException(status_code=500, detail=str(e))