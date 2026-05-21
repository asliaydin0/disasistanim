// Modal ve Seçilen Diş Değişkenleri
let currentToothId = null;
let toothModal; // Modal objesi sayfa yüklenince atanacak

// Kavis formülü
function calculateArchOffset(toothNum, jawType) {
    let center = jawType === 'upper' ? 8.5 : 24.5;
    let dist = Math.abs(toothNum - center);
    let offset = (dist * dist) * 1.5;
    return jawType === 'upper' ? -offset : offset;
}

// Diş Tıklandığında Modal'ı Açan Fonksiyon
function openToothModal(id) {
    currentToothId = id;
    document.getElementById('modalToothNo').innerText = id;
    if (toothModal) {
        toothModal.show();
    }
}

// Modal İçinden Durum Seçildiğinde Python API'sine Veri Gönderen Fonksiyon
async function saveStatus(status) {
    if(!currentToothId) return;

    try {
        // Python'a POST isteği atıyoruz
        const response = await fetch('http://127.0.0.1:8000/api/dis-guncelle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                hasta_id: 1, // Şimdilik 1 numaralı test hastamız (Aslı)
                dis_numarasi: currentToothId,
                durum: status
            })
        });

        const data = await response.json();

        if (data.durum === 'success') {
            // Pencereyi kapat
            if (toothModal) {
                toothModal.hide();
            }
            // Sayfayı yenilemeye gerek kalmadan haritayı tekrar çiz (Dinamik UI)
            disHaritasiniCiz(); 
        } else {
            alert("Hata oluştu: " + data.mesaj);
        }

    } catch (error) {
        console.error("Güncelleme hatası:", error);
        alert("Sunucuya ulaşılamadı!");
    }
}

function goToAnalysis() {
    window.location.href = '/analiz';
}

async function disHaritasiniCiz() {
    try {
        // Bootstrap Modal'ı hazırla
        toothModal = new bootstrap.Modal(document.getElementById('toothActionModal'));

        const response = await fetch('http://127.0.0.1:8000/api/dis-haritasi/1');
        const data = await response.json();
        
        let teethMap = {};
        for(let i = 1; i <= 32; i++) { teethMap[i] = 'healthy'; }

        if(data.veri && data.veri.length > 0) {
            data.veri.forEach(dis => { teethMap[dis.Dis_Numarasi] = dis.Mevcut_Durum; });
        }

        const ustCeneDiv = document.getElementById('ust-cene-alani');
        const altCeneDiv = document.getElementById('alt-cene-alani');
        ustCeneDiv.innerHTML = ""; 
        altCeneDiv.innerHTML = ""; 

        // Puan Hesaplama
        let durumlar = Object.values(teethMap);
        let curukSayisi = durumlar.filter(d => d === 'decay').length;
        let kanalSayisi = durumlar.filter(d => d === 'canal').length;
        let eksikSayisi = durumlar.filter(d => d === 'missing').length;

        let penalty = (curukSayisi * 8) + (kanalSayisi * 5) + (eksikSayisi * 10);
        let puan = Math.max(0, 100 - penalty);

        let renk = "", mesaj = "", ikon = "";
        if (puan >= 85) { renk = "#10b981"; mesaj = "Mükemmel Durum!"; ikon = "🏆"; } 
        else if (puan >= 60) { renk = "#f59e0b"; mesaj = "İyi, Ama Dikkat Gerek."; ikon = "🛡️"; } 
        else { renk = "#ef4444"; mesaj = "Acil Bakım Şart!"; ikon = "⚠️"; }

        document.getElementById('puan-text').innerText = puan;
        document.getElementById('mesaj-text').innerText = mesaj;
        document.getElementById('mesaj-text').style.color = renk;
        document.getElementById('ikon-text').innerText = ikon;

        const circle = document.getElementById('progress-circle');
        circle.style.stroke = renk;
        circle.style.strokeDashoffset = 301 - (301 * puan / 100);

        // --- Üst Çene ---
        for (let i = 16; i >= 1; i--) {
            let durum = teethMap[i];
            let imgSrc = durum === 'missing' ? 'default-tooth.png' : 'mutlu-dis.png';
            let offset = calculateArchOffset(i, 'upper');

            ustCeneDiv.innerHTML += `
                <div class="tooth-item ${durum}" onclick="openToothModal(${i})" style="--offset: ${offset}px;">
                    <span class="tooth-number">${i}</span>
                    <img src="/static/img/${imgSrc}" alt="Diş ${i}" onerror="this.src='https://cdn-icons-png.flaticon.com/512/3204/3204095.png';">
                </div>
            `;
        }

        // --- Alt Çene ---
        for (let i = 32; i >= 17; i--) {
            let durum = teethMap[i];
            let imgSrc = durum === 'missing' ? 'default-tooth.png' : 'mutlu-dis.png';
            let offset = calculateArchOffset(i, 'lower');

            altCeneDiv.innerHTML += `
                <div class="tooth-item ${durum}" onclick="openToothModal(${i})" style="--offset: ${offset}px;">
                    <span class="tooth-number">${i}</span>
                    <img src="/static/img/${imgSrc}" alt="Diş ${i}" onerror="this.src='https://cdn-icons-png.flaticon.com/512/3204/3204095.png';">
                </div>
            `;
        }

    } catch (error) { 
        console.error("Hata:", error); 
    }
}

document.addEventListener('DOMContentLoaded', disHaritasiniCiz);