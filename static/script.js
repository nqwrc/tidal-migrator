// Function to handle login
function handleLogin() {
  fetch('/login', {
    method: 'POST'
  })
  .then(response => {
    if (response.ok) {
      window.location.href = '/post_login';
    } else {
      console.error('Could not connect to Tidal');
    }
  })
  .catch(error => console.error(error));
}

// Show the selected category view and hide the category selection
function showCategory(category) {
  document.getElementById("categorySelection").style.display = "none";
  var views = document.getElementsByClassName("category-view");
  for (var i = 0; i < views.length; i++) {
    views[i].style.display = "none";
  }
  document.getElementById(category + "View").style.display = "block";
}

// Return to the main category selection
function backToCategories() {
  var views = document.getElementsByClassName("category-view");
  for (var i = 0; i < views.length; i++) {
    views[i].style.display = "none";
  }
  var catSel = document.getElementById("categorySelection");
  catSel.style.display = ""; // Remove inline style so CSS grid applies
}

// CSV File Upload handling
document.getElementById('uploadForm')?.addEventListener('submit', function(e) {
  e.preventDefault();
  const csvInput = document.getElementById('csvFile');
  const file = csvInput.files[0];

  if (file) {
    const formData = new FormData();
    formData.append('csvFile', file);

    fetch('/import_favorites', {
      method: 'POST',
      body: formData 
    })
    .then(response => response.text())
    .then(result => {
      console.log('Import Result:', result);
      // Optionally, display a success or error message.
    })
    .catch(error => console.error('Import Error:', error));

    const reader = new FileReader();
    reader.onload = function(e) {
      const csvData = e.target.result;
      // Optionally process CSV data here.
    }
    reader.readAsText(file);
  }
});

// CSV Download handling
const downloadButtons = document.querySelectorAll('.download-csv');
downloadButtons.forEach(button => {
  button.addEventListener('click', handleCSVDownload);
});

function handleCSVDownload(event) {
  const link = document.createElement('a');
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Modal logic for Transfer Favorites
const openModalBtn = document.getElementById('openTransferModal');
const closeModalBtn = document.getElementById('closeTransferModal');
const transferModal = document.getElementById('transferModal');

if (openModalBtn && closeModalBtn && transferModal) {
  openModalBtn.onclick = function() {
    transferModal.style.display = 'block';
  };
  closeModalBtn.onclick = function() {
    transferModal.style.display = 'none';
  };
  window.onclick = function(event) {
    if (event.target === transferModal) {
      transferModal.style.display = 'none';
    }
  };
}

// Transfer Favorites AJAX logic
const transferForm = document.getElementById('transferFavoritesForm');
const transferBtn = document.getElementById('transferSubmitBtn');
const transferBtnText = document.getElementById('transferBtnText');
const transferLoading = document.getElementById('transferLoading');
const transferInfo = document.getElementById('transferInfo');

if (transferForm) {
  transferForm.onsubmit = function(e) {
    e.preventDefault();
    transferBtn.disabled = true;
    transferBtnText.style.display = 'none';
    transferLoading.style.display = 'inline-block';
    transferInfo.textContent = 'Transferring favorites, please wait...';

    const formData = new FormData(transferForm);
    fetch('/transfer_all_favorites', {
      method: 'POST',
      body: formData
    })
    .then(async response => {
      const text = await response.text();
      if (response.redirected) {
        window.location.href = response.url;
      } else if (response.ok) {
        transferInfo.textContent = 'Transfer complete.';
        setTimeout(() => { window.location.reload(); }, 1200);
      } else {
        transferInfo.textContent = text || 'An error occurred during transfer.';
        transferBtn.disabled = false;
        transferBtnText.style.display = 'inline';
        transferLoading.style.display = 'none';
      }
    })
    .catch(err => {
      transferInfo.textContent = 'Network error: ' + err;
      transferBtn.disabled = false;
      transferBtnText.style.display = 'inline';
      transferLoading.style.display = 'none';
    });
  };
}
