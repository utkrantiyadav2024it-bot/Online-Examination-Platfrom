/**
 * MMCOE Online Examination Platform - Shared Application Utilities
 */

// Toast notification trigger
function showToast(message, type = 'info') {
  const toastContainer = document.getElementById('toast-container') || createToastContainer();
  
  const bgClass = type === 'success' ? 'bg-success' : 
                  type === 'danger' ? 'bg-danger' : 
                  type === 'warning' ? 'bg-warning text-dark' : 'bg-primary';

  const toastId = 'toast-' + Date.now();
  const html = `
    <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0 show shadow-sm" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          <i class="bi bi-info-circle-fill me-2"></i> ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;
  
  toastContainer.insertAdjacentHTML('beforeend', html);
  setTimeout(() => {
    const el = document.getElementById(toastId);
    if (el) el.remove();
  }, 4000);
}

function createToastContainer() {
  const div = document.createElement('div');
  div.id = 'toast-container';
  div.className = 'toast-container position-fixed bottom-0 end-0 p-3';
  div.style.zIndex = '9999';
  document.body.appendChild(div);
  return div;
}

// Password visibility toggle helper
function togglePasswordVisibility(inputId, iconId) {
  const input = document.getElementById(inputId);
  const icon = document.getElementById(iconId);
  if (!input) return;
  
  if (input.type === 'password') {
    input.type = 'text';
    if (icon) {
      icon.classList.remove('bi-eye');
      icon.classList.add('bi-eye-slash');
    }
  } else {
    input.type = 'password';
    if (icon) {
      icon.classList.remove('bi-eye-slash');
      icon.classList.add('bi-eye');
    }
  }
}

// Mobile sidebar toggle
function toggleMobileSidebar() {
  const sidebar = document.querySelector('.sidebar');
  if (sidebar) {
    sidebar.classList.toggle('show');
  }
}

// Dynamic Option Row Adder for Question Creation
function addQuestionOption() {
  const container = document.getElementById('optionsContainer');
  if (!container) return;
  
  const currentCount = container.children.length;
  const optionLetter = String.fromCharCode(65 + currentCount); // A, B, C...
  
  const div = document.createElement('div');
  div.className = 'input-group mb-2 option-row';
  div.id = `option-row-${currentCount}`;
  div.innerHTML = `
    <span class="input-group-text bg-light text-dark font-monospace">${optionLetter}</span>
    <input type="text" class="form-control form-control-custom" placeholder="Option ${optionLetter} text" required>
    <div class="input-group-text bg-light text-dark">
      <input class="form-check-input mt-0" type="checkbox" title="Mark as correct answer">
      <span class="ms-1 small">Correct</span>
    </div>
    <button class="btn btn-outline-danger" type="button" onclick="removeQuestionOption(this)">
      <i class="bi bi-trash"></i>
    </button>
  `;
  container.appendChild(div);
  reindexOptions();
}

function removeQuestionOption(btn) {
  const row = btn.closest('.option-row');
  if (!row) return;
  const container = document.getElementById('optionsContainer');
  if (container.children.length <= 2) {
    showToast('A question must have at least 2 options!', 'warning');
    return;
  }
  row.remove();
  reindexOptions();
}

function reindexOptions() {
  const container = document.getElementById('optionsContainer');
  if (!container) return;
  
  Array.from(container.children).forEach((row, idx) => {
    const letter = String.fromCharCode(65 + idx);
    const span = row.querySelector('.font-monospace');
    if (span) span.textContent = letter;
    const input = row.querySelector('input[type="text"]');
    if (input) input.placeholder = `Option ${letter} text`;
  });
}

// Table search and filter utility
function filterTable(tableId, searchInputId, columnIndex = -1) {
  const input = document.getElementById(searchInputId);
  const table = document.getElementById(tableId);
  if (!input || !table) return;

  const filter = input.value.toLowerCase().trim();
  const rows = table.querySelectorAll('tbody tr');

  rows.forEach(row => {
    if (columnIndex >= 0) {
      const cell = row.cells[columnIndex];
      const text = cell ? cell.textContent.toLowerCase() : '';
      row.style.display = text.includes(filter) ? '' : 'none';
    } else {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(filter) ? '' : 'none';
    }
  });
}

// Wizard Step Navigation
function switchStep(stepNumber, maxSteps = 5) {
  for (let i = 1; i <= maxSteps; i++) {
    const stepEl = document.getElementById(`step-${i}`);
    const tabBtn = document.getElementById(`step-tab-${i}`) || document.getElementById(`tab${i}-btn`);
    if (stepEl) {
      stepEl.classList.toggle('d-none', i !== stepNumber);
    }
    if (tabBtn) {
      tabBtn.classList.toggle('active', i === stepNumber);
      if (i < stepNumber) {
        tabBtn.classList.add('completed');
      }
    }
  }
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Autosave Simulation Indicator
function triggerAutosave(status = 'saving') {
  const pill = document.getElementById('autosavePill');
  const textEl = document.getElementById('autosaveText');
  if (!pill) return;

  if (status === 'saving') {
    pill.className = 'autosave-pill saving';
    if (textEl) textEl.textContent = 'Saving answer...';
    setTimeout(() => {
      pill.className = 'autosave-pill';
      if (textEl) textEl.textContent = 'Answer Saved';
    }, 450);
  }
}

// Global initialization
document.addEventListener('DOMContentLoaded', () => {
  // Add mobile menu button to navbar if not exists
  const navbar = document.querySelector('.top-navbar');
  if (navbar && !navbar.querySelector('.mobile-toggle-btn')) {
    const btn = document.createElement('button');
    btn.className = 'btn btn-sm btn-outline-secondary d-lg-none me-2 mobile-toggle-btn';
    btn.innerHTML = '<i class="bi bi-list fs-5"></i>';
    btn.onclick = toggleMobileSidebar;
    navbar.insertBefore(btn, navbar.firstChild);
  }
});

// ============================================================================
// Secure Session & Authentication Utilities
// ============================================================================

let _cachedCsrfToken = null;

async function getCsrfToken() {
  if (_cachedCsrfToken) return _cachedCsrfToken;
  try {
    const res = await fetch('/api/v1/auth/csrf-token', { credentials: 'include' });
    if (res.ok) {
      const json = await res.json();
      _cachedCsrfToken = json.data?.csrf_token;
      return _cachedCsrfToken;
    }
  } catch (err) {
    console.warn('Could not fetch CSRF token:', err);
  }
  return null;
}

async function apiFetch(url, options = {}) {
  const defaultHeaders = {
    'Accept': 'application/json'
  };

  if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
    options.body = JSON.stringify(options.body);
    defaultHeaders['Content-Type'] = 'application/json';
  }

  // Include CSRF token on state-modifying requests
  const method = (options.method || 'GET').toUpperCase();
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    const csrf = await getCsrfToken();
    if (csrf) {
      defaultHeaders['X-CSRFToken'] = csrf;
    }
  }

  options.headers = {
    ...defaultHeaders,
    ...options.headers
  };

  // Crucial: always include credentials so HttpOnly cookies are passed
  options.credentials = 'include';

  try {
    const response = await fetch(url, options);

    // Handle 401 Unauthorized (expired or missing session)
    if (response.status === 401 && !window.location.pathname.includes('/auth/login')) {
      showToast('Your session has expired. Redirecting to login...', 'warning');
      setTimeout(() => {
        window.location.href = '/auth/login.html?expired=true';
      }, 1200);
    }

    return response;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

const SessionAuth = {
  async login(email, password) {
    const response = await apiFetch('/api/v1/auth/login', {
      method: 'POST',
      body: { email, password }
    });
    return response.json();
  },

  async logout() {
    try {
      await apiFetch('/api/v1/auth/logout', { method: 'POST' });
    } finally {
      showToast('Logged out successfully', 'info');
      setTimeout(() => {
        window.location.href = '/auth/login.html';
      }, 400);
    }
  },

  async getCurrentSession() {
    const response = await apiFetch('/api/v1/sessions/current');
    if (!response.ok) return null;
    return response.json();
  },

  async validateSession() {
    const response = await apiFetch('/api/v1/sessions/validate');
    if (!response.ok) return false;
    const json = await response.json();
    return json.data?.is_valid === true;
  },

  async refreshSession() {
    const response = await apiFetch('/api/v1/sessions/refresh', { method: 'POST' });
    return response.json();
  }
};


