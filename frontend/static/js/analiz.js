document.addEventListener('DOMContentLoaded', () => {
    const username = localStorage.getItem('kullanici_ad') || 'Değerli Kullanıcı';
    const heroTitle = document.querySelector('.display-5');
    if (heroTitle) {
        heroTitle.innerHTML = `Merhaba, <span class="text-primary">${username}</span> — analiz raporunuzu başlatın.`;
    }

    const analizForm = document.getElementById('analysis-form');
    const resultPanel = document.getElementById('analysis-results');
    const recommendationTitle = document.getElementById('recommendation-title');
    const recommendationText = document.getElementById('recommendation-text');
    const priorityLabel = document.getElementById('priority-badge');
    const riskBadge = document.getElementById('risk-score');
    const nextStepsList = document.getElementById('next-steps');
    const summaryCard = document.getElementById('analysis-summary');
    const toothField = document.getElementById('selected-tooth');
    const complaintField = document.getElementById('selected-complaint');
    const chartInfo = document.getElementById('tooth-chart-instruction');
    const svgToothGroups = document.querySelectorAll('.tooth-group');
    const selectedToothDisplay = document.getElementById('selected-tooth-display');

    const clearSelection = () => {
        svgToothGroups.forEach(group => group.classList.remove('selected-tooth'));
        toothField.value = '';
        selectedToothDisplay.innerText = 'Henüz diş seçilmedi';
        chartInfo.innerText = 'Diş şemasından bir diş seçin, ardından şikayetinizi seçin.';
    };

    svgToothGroups.forEach(group => {
        group.addEventListener('click', () => {
            const label = group.querySelector('.tooth-label');
            const toothNumber = label ? label.textContent.trim() : null;
            if (!toothNumber) return;
            svgToothGroups.forEach(g => g.classList.remove('selected-tooth'));
            group.classList.add('selected-tooth');
            toothField.value = toothNumber;
            selectedToothDisplay.innerText = `${toothNumber} numaralı diş seçildi`;
            chartInfo.innerText = 'Seçiminiz kaydedildi. Şimdi şikayetinizi seçin.';
        });
    });

    analizForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        if (!toothField.value || !complaintField.value) return;

        const payload = {
            hasta_id: parseInt(localStorage.getItem('kullanici_id') || '1', 10),
            dis_numarasi: parseInt(toothField.value, 10),
            sikayet: complaintField.value
        };

        try {
            const response = await fetch('/api/analiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'Analiz yapılamadı.');
            }

            renderResult(data);
        } catch (error) {
            console.error(error);
            resultPanel.innerHTML = `<div class="alert alert-danger">Analiz sırasında bir hata oluştu. Lütfen tekrar deneyin.</div>`;
        }
    });

    function renderResult(data) {
        resultPanel.classList.remove('d-none');
        recommendationTitle.innerText = `${data.analysis_title} — Diş #${data.dis_numarasi}`;
        recommendationText.innerText = data.recommendation;
        priorityLabel.innerText = `Öncelik: ${data.priority}`;
        riskBadge.innerText = `${data.risk_score}%`;
        riskBadge.className = `badge ${data.risk_score >= 80 ? 'bg-success' : data.risk_score >= 60 ? 'bg-warning text-dark' : 'bg-danger'} py-2 px-3`;
        summaryCard.innerText = data.analysis_summary;
        nextStepsList.innerHTML = data.next_steps.map(step => `<li class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>${step}</li>`).join('');
        document.getElementById('analysis-result-header').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    clearSelection();
});
