/**
 * Audit Logging - frontend controller
 * Talks to /api/v1/audit/* and renders /admin/audit/list.html
 */

const AUDIT_API = '/api/v1/audit';

const auditState = {
  page: 1,
  pageSize: 25,
  totalPages: 0,
  totalRecords: 0,
  searchTimer: null
};

/* ------------------------------------------------------------------ */
/* Networking                                                          */
/* ------------------------------------------------------------------ */

async function auditFetch(path, params) {
  const url = new URL(path, window.location.origin);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        url.searchParams.set(key, value);
      }
    });
  }

  const response = await fetch(url.toString(), {
    method: 'GET',
    credentials: 'same-origin',
    headers: { 'Accept': 'application/json' }
  });

  if (response.status === 401) {
    throw new AuditAccessError('Your session has expired. Please sign in again.');
  }
  if (response.status === 403) {
    throw new AuditAccessError('Audit logs are restricted to administrator accounts.');
  }

  const payload = await response.json().catch(() => null);

  if (!response.ok || !payload || payload.success === false) {
    throw new Error((payload && payload.message) || 'Request failed');
  }

  return payload.data;
}

class AuditAccessError extends Error {}

/* ------------------------------------------------------------------ */
/* Filters                                                             */
/* ------------------------------------------------------------------ */

function currentAuditFilters() {
  const value = (id) => {
    const el = document.getElementById(id);
    return el ? el.value.trim() : '';
  };

  return {
    search: value('auditSearch'),
    module: value('moduleFilter'),
    action: value('actionFilter'),
    status: value('statusFilter'),
    start_date: value('startDateFilter'),
    end_date: value('endDateFilter')
  };
}

async function loadAuditFilterOptions() {
  try {
    const data = await auditFetch(`${AUDIT_API}/filters`);
    fillSelect('moduleFilter', data.modules, 'All Functional Modules');
    fillSelect('actionFilter', data.actions, 'All Action Types');
    fillSelect('statusFilter', data.statuses, 'All Statuses');
  } catch (error) {
    /* Dropdowns stay empty; the table error banner already explains why. */
  }
}

function fillSelect(elementId, values, placeholder) {
  const select = document.getElementById(elementId);
  if (!select) return;

  const previous = select.value;
  select.innerHTML = `<option value="">${placeholder}</option>` +
    (values || []).map(v => `<option value="${escapeHtml(v)}">${escapeHtml(v)}</option>`).join('');

  if (previous) select.value = previous;
}

function filterAudit() {
  auditState.page = 1;
  loadAuditLogs();
}

function debouncedAuditSearch() {
  clearTimeout(auditState.searchTimer);
  auditState.searchTimer = setTimeout(filterAudit, 350);
}

function resetAuditFilters() {
  ['auditSearch', 'moduleFilter', 'actionFilter', 'statusFilter',
   'startDateFilter', 'endDateFilter'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  filterAudit();
}

/* ------------------------------------------------------------------ */
/* Rendering                                                           */
/* ------------------------------------------------------------------ */

function escapeHtml(value) {
  if (value === null || value === undefined) return '';
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function formatTimestamp(isoString) {
  if (!isoString) return '—';
  const date = new Date(isoString);
  if (isNaN(date.getTime())) return escapeHtml(isoString);

  const today = new Date();
  const sameDay = date.toDateString() === today.toDateString();
  const time = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return sameDay
    ? `Today, ${time}`
    : `${date.toLocaleDateString([], { day: '2-digit', month: 'short' })}, ${time}`;
}

function actionBadgeClass(action) {
  const value = (action || '').toUpperCase();
  if (value.includes('DELETE') || value.includes('FAIL')) return 'bg-danger';
  if (value.includes('CREATE') || value.includes('LOGIN')) return 'bg-primary';
  if (value.includes('PUBLISH')) return 'bg-success';
  if (value.includes('UPDATE') || value.includes('PASSWORD')) return 'bg-info';
  return 'bg-secondary';
}

function statusBadgeClass(status) {
  return (status || '').toUpperCase() === 'SUCCESS'
    ? 'status-badge badge-active'
    : 'status-badge badge-inactive';
}

function renderAuditRows(items) {
  const tbody = document.getElementById('auditTableBody');
  if (!tbody) return;

  if (!items.length) {
    tbody.innerHTML = `
      <tr><td colspan="9" class="text-center text-muted py-4">
        <i class="bi bi-inbox me-2"></i>No audit records match the current filters.
      </td></tr>`;
    return;
  }

  tbody.innerHTML = items.map(log => `
    <tr>
      <td class="font-monospace fw-bold">#${escapeHtml(log.audit_log_id)}</td>
      <td class="text-muted">${formatTimestamp(log.created_at)}</td>
      <td class="fw-semibold">
        ${escapeHtml(log.actor_name)}
        ${log.actor_role ? `<span class="badge bg-light text-dark border ms-1">${escapeHtml(log.actor_role)}</span>` : ''}
        ${log.actor_email ? `<div class="text-muted small">${escapeHtml(log.actor_email)}</div>` : ''}
      </td>
      <td><span class="badge bg-light text-dark border">${escapeHtml(log.module)}</span></td>
      <td><span class="badge ${actionBadgeClass(log.action)}">${escapeHtml(log.action)}</span></td>
      <td>${escapeHtml(log.target)}</td>
      <td class="font-monospace text-info">${escapeHtml(log.ip_address || '—')}</td>
      <td><code>${escapeHtml(log.details || '—')}</code></td>
      <td><span class="${statusBadgeClass(log.status)}">${escapeHtml(log.status)}</span></td>
    </tr>
  `).join('');
}

function renderAuditPagination(pagination) {
  const info = document.getElementById('auditRecordCount');
  if (info) {
    const from = pagination.total_records === 0
      ? 0 : (pagination.page - 1) * pagination.page_size + 1;
    const to = Math.min(pagination.page * pagination.page_size, pagination.total_records);
    info.textContent = `Showing ${from}-${to} of ${pagination.total_records} immutable records`;
  }

  const prev = document.getElementById('auditPrevBtn');
  const next = document.getElementById('auditNextBtn');
  const label = document.getElementById('auditPageLabel');

  if (prev) prev.disabled = !pagination.has_previous;
  if (next) next.disabled = !pagination.has_next;
  if (label) {
    label.textContent = `Page ${pagination.page} of ${pagination.total_pages || 1}`;
  }
}

function renderAuditSummary(summary) {
  const set = (id, value) => {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  };

  set('auditTotalCount', summary.total_logs.toLocaleString());
  set('auditSuccessCount', summary.success_count.toLocaleString());
  set('auditFailureCount', summary.non_success_count.toLocaleString());
  set('auditRecentCount', summary.last_24h_count.toLocaleString());
  set('auditActorCount', summary.distinct_actors.toLocaleString());
}

function showAuditError(message) {
  const banner = document.getElementById('auditErrorBanner');
  if (banner) {
    banner.classList.remove('d-none');
    banner.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-2"></i>${escapeHtml(message)}
      <a href="/auth/login.html" class="alert-link ms-1">Sign in</a>`;
  }

  const tbody = document.getElementById('auditTableBody');
  if (tbody) {
    tbody.innerHTML = `<tr><td colspan="9" class="text-center text-muted py-4">${escapeHtml(message)}</td></tr>`;
  }
}

function hideAuditError() {
  const banner = document.getElementById('auditErrorBanner');
  if (banner) banner.classList.add('d-none');
}

/* ------------------------------------------------------------------ */
/* Actions                                                             */
/* ------------------------------------------------------------------ */

async function loadAuditLogs() {
  const tbody = document.getElementById('auditTableBody');
  if (tbody) {
    tbody.innerHTML = `<tr><td colspan="9" class="text-center text-muted py-4">
      <span class="spinner-border spinner-border-sm me-2"></span>Loading audit trail...
    </td></tr>`;
  }

  try {
    const data = await auditFetch(`${AUDIT_API}/logs`, {
      ...currentAuditFilters(),
      page: auditState.page,
      page_size: auditState.pageSize
    });

    hideAuditError();
    renderAuditRows(data.items);
    renderAuditPagination(data.pagination);
    auditState.totalPages = data.pagination.total_pages;
    auditState.totalRecords = data.pagination.total_records;
  } catch (error) {
    showAuditError(error.message);
  }
}

async function loadAuditSummary() {
  try {
    const summary = await auditFetch(`${AUDIT_API}/summary`);
    renderAuditSummary(summary);
  } catch (error) {
    /* The table banner already reports access problems. */
  }
}

function changeAuditPage(delta) {
  const next = auditState.page + delta;
  if (next < 1 || (auditState.totalPages && next > auditState.totalPages)) return;
  auditState.page = next;
  loadAuditLogs();
}

function exportAuditCsv() {
  const url = new URL(`${AUDIT_API}/logs/export`, window.location.origin);
  Object.entries(currentAuditFilters()).forEach(([key, value]) => {
    if (value) url.searchParams.set(key, value);
  });

  if (typeof showToast === 'function') {
    showToast('Preparing audit CSV export...', 'info');
  }
  window.location.href = url.toString();
}

document.addEventListener('DOMContentLoaded', () => {
  if (!document.getElementById('auditTableBody')) return;
  loadAuditFilterOptions();
  loadAuditSummary();
  loadAuditLogs();
});
