document.addEventListener('DOMContentLoaded', function() {
    // Sayfa açıldığında verileri Python'dan çek
    verileriGetir();

    if ("Notification" in window) {
        if (Notification.permission !== "granted" && Notification.permission !== "denied") {
            Notification.requestPermission();
        }
    }
    setInterval(bildirimKontrol, 60000);
});

// API'den veri çeken ana fonksiyon
async function verileriGetir() {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/fircalama-istatistik/1');
        const data = await response.json();

        // Butonları Çiz
        cizButonlar(data.bugun_sabah, data.bugun_aksam, data.bugun_sabah_id, data.bugun_aksam_id);
        
        // İstatistikleri Çiz
        document.getElementById('basari-bar').style.width = data.basari_yuzdesi + '%';
        document.getElementById('basari-text').innerText = '%' + data.basari_yuzdesi + ' Başarı';
        document.getElementById('stat-sabah').innerText = data.sabah_toplam;
        document.getElementById('stat-aksam').innerText = data.aksam_toplam;
        document.getElementById('stat-seri').innerText = data.seri;

        // AI Kartını Çiz
        document.getElementById('ai-karti').style.background = data.ai.bg;
        document.getElementById('ai-icon').className = `fas ${data.ai.icon} fa-2x`;
        document.getElementById('ai-title').innerText = data.ai.title;
        document.getElementById('ai-message').innerText = `"${data.ai.text}"`;

    } catch (error) {
        console.error("Veri çekilemedi:", error);
    }
}

function cizButonlar(sabahFircalandi, aksamFircalandi, sabahId, aksamId) {
    const sabahAlani = document.getElementById('sabah-buton-alani');
    const aksamAlani = document.getElementById('aksam-buton-alani');

    // Sabah Butonları
    sabahAlani.innerHTML = `
        <button class="btn ${sabahFircalandi ? 'btn-secondary' : 'btn-success'} btn-lg" onclick="islemYap('Sabah', 'kaydet')" ${sabahFircalandi ? 'disabled' : ''}>
            <i class="fas fa-sun me-2"></i> ${sabahFircalandi ? 'Sabah Kaydedildi' : 'Sabah Fırçaladım'}
        </button>
        ${sabahFircalandi ? `<button class="btn btn-outline-danger btn-lg border-0" onclick="islemYap('Sabah', 'sil', ${sabahId})"><i class="fas fa-trash-can"></i></button>` : ''}
    `;

    // Akşam Butonları
    aksamAlani.innerHTML = `
        <button class="btn ${aksamFircalandi ? 'btn-secondary' : 'btn-success'} btn-lg" onclick="islemYap('Akşam', 'kaydet')" ${aksamFircalandi ? 'disabled' : ''}>
            <i class="fas fa-moon me-2"></i> ${aksamFircalandi ? 'Akşam Kaydedildi' : 'Akşam Fırçaladım'}
        </button>
        ${aksamFircalandi ? `<button class="btn btn-outline-danger btn-lg border-0" onclick="islemYap('Akşam', 'sil', ${aksamId})"><i class="fas fa-trash-can"></i></button>` : ''}
    `;
}

// Fırçalama Kaydet veya Sil İşlemi
async function islemYap(vakit, tip, kayitId = null) {
    if (tip === 'sil' && !confirm("Bu kaydı silmek istediğinize emin misiniz?")) return;
    
    let url = tip === 'kaydet' ? 'http://127.0.0.1:8000/api/fircalama-ekle' : 'http://127.0.0.1:8000/api/fircalama-sil';
    let bodyData = tip === 'kaydet' ? { hasta_id: 1, zaman_dilimi: vakit } : { kayit_id: kayitId };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(bodyData)
        });
        
        const data = await response.json();
        if(data.durum === 'success') {
            verileriGetir(); // Sayfayı yenilemeden verileri güncelle
        }
    } catch(err) {
        console.error("Hata:", err);
    }
}

// --- POPUP VE BİLDİRİM KODLARI (Aynen Kalıyor) ---
function gosterPopup(tip) {
    const overlay = document.getElementById('reminder-popup');
    const box = document.querySelector('.reminder-box');
    const title = document.getElementById('popup-title');
    const msg = document.getElementById('popup-message');
    const icon = document.getElementById('popup-icon');
    const iconContainer = document.getElementById('popup-icon-container');

    if(tip === 'sabah') {
        box.style.borderTopColor = "#ffc107";
        icon.className = "fas fa-sun text-warning";
        iconContainer.style.background = "#fff9db";
        title.innerText = "Günaydın Aslı! ☀️";
        msg.innerText = "Güne ferah bir başlangıç yapmak için dişlerini fırçalamayı unutma.";
    } else {
        box.style.borderTopColor = "#0d6efd";
        icon.className = "fas fa-moon text-primary";
        iconContainer.style.background = "#e7f1ff";
        title.innerText = "İyi Geceler Aslı! 🌙";
        msg.innerText = "Günü bitirmeden önce 2 dakikanı dişlerine ayırmayı unutma.";
    }
    overlay.style.display = 'flex';
}

function kapatPopup() { document.getElementById('reminder-popup').style.display = 'none'; }

function saatleriKaydet() {
    const msg = document.getElementById('status-msg');
    msg.classList.remove('d-none'); 
    setTimeout(() => msg.classList.add('d-none'), 3000);
    if (Notification.permission !== "granted") Notification.requestPermission();
}

let sonBildirimZamani = "";
function bildirimKontrol() {
    const simdi = new Date();
    const suan = String(simdi.getHours()).padStart(2, '0') + ':' + String(simdi.getMinutes()).padStart(2, '0');
    if (suan === sonBildirimZamani) return;

    const sabahHedef = document.getElementById('sabah').value;
    const aksamHedef = document.getElementById('aksam').value;

    if (suan === sabahHedef) { gosterPopup('sabah'); if (Notification.permission === "granted") { new Notification("Fırçalama Vakti!"); } sonBildirimZamani = suan; }
    if (suan === aksamHedef) { gosterPopup('aksam'); if (Notification.permission === "granted") { new Notification("Fırçalama Vakti!"); } sonBildirimZamani = suan; }
}