function sortTableByRank(tableId, ascending) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const tbody = table.querySelector("tbody");
    const rows = Array.from(tbody.querySelectorAll("tr"));

    rows.sort((a, b) => {
        const aText = a.cells[3].innerText.trim(); // "opening - closing"
        const bText = b.cells[3].innerText.trim();

        const aClosing = parseInt(aText.split("-")[1]);
        const bClosing = parseInt(bText.split("-")[1]);

        if (isNaN(aClosing) || isNaN(bClosing)) return 0;

        return ascending ? aClosing - bClosing : bClosing - aClosing;
    });

    rows.forEach(row => tbody.appendChild(row));
}

function toggleInstitute(id) {
    const panel = document.getElementById(`panel-${id}`);
    const chev = document.getElementById(`chevron-${id}`);
    if (!panel || !chev) return;

    const isHidden = panel.style.display === "none" || panel.style.display === "";
    panel.style.display = isHidden ? "block" : "none";
    chev.textContent = isHidden ? "▲" : "▼";
}


// Terms checkbox - enable/disable Send OTP button
function initUnlockForm() {
    const termsCheckbox = document.getElementById('terms');
    const sendOtpBtn = document.getElementById('sendOtpBtn');
    
    if (termsCheckbox && sendOtpBtn) {
        // Enable button when checkbox is checked
        termsCheckbox.addEventListener('change', function() {
            sendOtpBtn.disabled = !this.checked;
            sendOtpBtn.classList.toggle('disabled', !this.checked);
        });
        
        // Initially disable button
        sendOtpBtn.disabled = true;
        sendOtpBtn.classList.add('disabled');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initUnlockForm);
