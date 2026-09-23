/**
 * Reporting & Analytics - frontend controller
 * Talks to /api/v1/reports/* and renders /reports/exam_report.html
 */

const REPORTS_API = '/api/v1/reports';

const reportState = {
  examId: null
};

/* ------------------------------------------------------------------ */
/* Networking                                                          */
/* ------------------------------------------------------------------ */

async function reportsFetch(path, params) {
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
    throw new Error('Your session has expired. Please sign in again.');
  }
  if (response.status === 403) {
    throw new Error('Analytics are restricted to faculty and administrator accounts.');
  }

  const payload = await response.json().catch(() => null);

  if (!response.ok || !payload || payload.success === false) {
    throw new Error((payload && payload.message) || 'Request failed');
  }

  return payload.data;
}

/* ------------------------------------------------------------------ */
/* Helpers                                                             */
/* ------------------------------------------------------------------ */

function esc(value) {
  if (value === null || value === undefined) return '';
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function num(value, digits = 1) {
  if (value === null || value === undefined) return '—';
  return Number(value).toFixed(digits);
}

function bandColour(label) {
  if (label.startsWith('81')) return 'success';
  if (label.startsWith('61')) return 'info';
  if (label.startsWith('41')) return 'warning';
  return 'danger';
}

function accuracyColour(accuracy) {
  if (accuracy >= 85) return 'success';
  if (accuracy >= 70) return 'info';
  if (accuracy >= 55) return 'warning';
  return 'danger';
}

function difficultyBadge(level) {
  const map = { EASY: 'bg-success', MEDIUM: 'bg-warning text-dark', HARD: 'bg-danger' };
  return map[(level || '').toUpperCase()] || 'bg-secondary';
}

/* ------------------------------------------------------------------ */
/* Rendering                                                           */
/* ------------------------------------------------------------------ */

function renderSummary(summary) {
  const p = summary.participation;
  const s = summary.scores;
  const t = summary.timing;

  setText('kpiCandidates', p.active_registrations);
  setText('kpiCandidatesSub', `${p.submitted_attempts} submitted`);
  setText('kpiAttendance', `${num(p.attendance_rate)}% attendance`);

  setText('kpiPassRate', `${num(s.pass_rate)}%`);
  setText('kpiPassSub', `${s.pass_count} passed / ${s.fail_count} failed`);
  setText('kpiPassThreshold',
    `Threshold: ${num(summary.exam.passing_marks)} / ${num(summary.exam.total_marks)}`);

  setText('kpiAverage', num(s.average_percentage));
  setText('kpiAverageSub',
    `Median: ${num(s.median_percentage)} / Max: ${num(s.highest_percentage)}`);

  setText('kpiAvgTime', num(t.average_time_minutes));
  setText('kpiAvgTimeSub', `Scheduled: ${t.scheduled_duration_minutes} mins`);

  setText('reportExamHeading',
    `${summary.exam.exam_code} • ${summary.exam.exam_title}`);
  setText('reportSubject',
    `${summary.exam.subject_code} — ${summary.exam.subject_name}`);
}

function renderDistribution(distribution) {
  const container = document.getElementById('scoreDistribution');
  if (!container) return;

  setText('distributionCount', `${distribution.total_evaluated} submissions`);

  if (!distribution.total_evaluated) {
    container.innerHTML = '<p class="text-muted small m-0">No evaluated results yet for this exam.</p>';
  } else {
    container.innerHTML = distribution.bands.map(band => `
      <div class="score-bar-group">
        <div class="score-bar-label">${esc(band.label)}</div>
        <div class="score-bar-track">
          <div class="score-bar-fill bg-${bandColour(band.label)}" style="width: ${band.share}%;"></div>
        </div>
        <div class="score-bar-count text-${bandColour(band.label)}">
          ${band.count} (${num(band.share)}%)
        </div>
      </div>
    `).join('');
  }

  setText('distHighest', `${num(distribution.highest_marks)} / ${num(distribution.exam_total_marks)}`);
  setText('distLowest', `${num(distribution.lowest_marks)} / ${num(distribution.exam_total_marks)}`);
  setText('distStdDev', num(distribution.std_deviation, 2));
}

function renderMastery(mastery) {
  const container = document.getElementById('masteryBreakdown');
  if (!container) return;

  const rows = [
    ...mastery.by_difficulty.map(entry => ({
      label: `${entry.difficulty_level} questions`,
      accuracy: entry.accuracy,
      responses: entry.responses
    })),
    ...mastery.by_question_type.map(entry => ({
      label: `${entry.question_type} items`,
      accuracy: entry.accuracy,
      responses: entry.responses
    }))
  ];

  if (!rows.length) {
    container.innerHTML = '<p class="text-muted small m-0">No auto-evaluated responses recorded yet.</p>';
    return;
  }

  container.innerHTML = rows.map(row => `
    <div>
      <div class="d-flex justify-content-between small fw-semibold mb-1">
        <span>${esc(row.label)}</span>
        <span class="text-${accuracyColour(row.accuracy)}">${num(row.accuracy)}% accuracy</span>
      </div>
      <div class="progress" style="height: 10px;">
        <div class="progress-bar bg-${accuracyColour(row.accuracy)}" style="width: ${row.accuracy}%;"></div>
      </div>
      <div class="text-muted" style="font-size: 0.7rem;">${row.responses} responses</div>
    </div>
  `).join('');
}

function renderItemAnalysis(itemAnalysis) {
  const tbody = document.getElementById('itemAnalysisBody');
  if (!tbody) return;

  if (!itemAnalysis.items.length) {
    tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted py-4">
      No questions are assigned to this exam yet.</td></tr>`;
    return;
  }

  tbody.innerHTML = itemAnalysis.items.map(item => {
    const discrimination = item.discrimination_index === null
      ? `<span class="badge bg-light text-muted border">n/a (needs ≥ ${itemAnalysis.min_attempts_for_discrimination} attempts)</span>`
      : `<span class="badge bg-light text-dark border">${item.discrimination_index >= 0 ? '+' : ''}${num(item.discrimination_index, 2)} (${esc(item.discrimination_label)})</span>`;

    const correct = item.correct_percentage === null
      ? '<span class="text-muted">Manual</span>'
      : `<strong class="text-${accuracyColour(item.correct_percentage)}">${num(item.correct_percentage)}%</strong>`;

    const incorrect = item.incorrect_percentage === null
      ? '<span class="text-muted">—</span>'
      : `${num(item.incorrect_percentage)}%`;

    return `
      <tr>
        <td class="font-monospace fw-bold">Q${esc(item.question_order)}</td>
        <td class="fw-semibold text-dark">${esc(item.question_text)}</td>
        <td><span class="badge bg-primary">${esc(item.question_type)}</span></td>
        <td><span class="badge ${difficultyBadge(item.difficulty_level)}">${esc(item.difficulty_level)}</span></td>
        <td>${correct}</td>
        <td class="text-muted">${incorrect}</td>
        <td class="font-monospace">${Math.round(item.average_time_seconds)}s</td>
        <td>${discrimination}</td>
      </tr>`;
  }).join('');
}

function showReportError(message) {
  const banner = document.getElementById('reportErrorBanner');
  if (banner) {
    banner.classList.remove('d-none');
    banner.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-2"></i>${esc(message)}
      <a href="/auth/login.html" class="alert-link ms-1">Sign in</a>`;
  }
}

function hideReportError() {
  const banner = document.getElementById('reportErrorBanner');
  if (banner) banner.classList.add('d-none');
}

/* ------------------------------------------------------------------ */
/* Actions                                                             */
/* ------------------------------------------------------------------ */

async function loadExamOptions() {
  const select = document.getElementById('reportExamSelect');
  if (!select) return;

  try {
    const data = await reportsFetch(`${REPORTS_API}/exams`);

    if (!data.items.length) {
      select.innerHTML = '<option value="">No exams available</option>';
      showReportError('No exams exist yet, so there is nothing to analyse.');
      return;
    }

    select.innerHTML = data.items.map(exam =>
      `<option value="${exam.exam_id}">${esc(exam.exam_code)} • ${esc(exam.exam_title)}</option>`
    ).join('');

    reportState.examId = data.items[0].exam_id;
    select.value = reportState.examId;

    await loadExamReport();
  } catch (error) {
    select.innerHTML = '<option value="">Unavailable</option>';
    showReportError(error.message);
  }
}

async function loadExamReport() {
  if (!reportState.examId) return;

  try {
    const data = await reportsFetch(`${REPORTS_API}/exams/${reportState.examId}/full`);

    hideReportError();
    renderSummary(data.summary);
    renderDistribution(data.score_distribution);
    renderMastery(data.mastery);
    renderItemAnalysis(data.item_analysis);
    setText('reportGeneratedAt', `Generated ${new Date(data.generated_at).toLocaleString()}`);
  } catch (error) {
    showReportError(error.message);
  }
}

function onExamChange(select) {
  reportState.examId = select.value;
  loadExamReport();
}

function exportReportCsv() {
  if (!reportState.examId) return;
  if (typeof showToast === 'function') {
    showToast('Preparing analytics CSV export...', 'info');
  }
  window.location.href = `${REPORTS_API}/exams/${reportState.examId}/export`;
}

document.addEventListener('DOMContentLoaded', () => {
  if (!document.getElementById('itemAnalysisBody')) return;
  loadExamOptions();
});
