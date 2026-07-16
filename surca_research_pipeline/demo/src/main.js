import './styles.css'
import generatedData from './generated/trace-ed-data.json'
import sampleData from './sample-data.js'

const app = document.querySelector('#app')

const data = generatedData.runs && generatedData.runs.length ? generatedData : sampleData
const usingSampleData = !(generatedData.runs && generatedData.runs.length)

const state = {
  runIndex: 0,
  resultIndex: 0
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function summarizeResult(result) {
  if (!result) {
    return 'No result selected.'
  }

  const total = result.scored_field_count ?? 0
  const correct = result.correct_scored_fields ?? 0
  const misses = Math.max(total - correct, 0)
  const abstention = result.abstention_detected ? 'Yes' : 'No'
  return `Accuracy ${result.accuracy_percent ?? 0}% | Correct ${correct}/${total} | Misses ${misses} | Abstention ${abstention}`
}

function formatTruth(value) {
  if (value === null || value === undefined) {
    return 'Unscored'
  }
  return value ? 'Yes' : 'No'
}

function summarizeClaimTypes(result) {
  if (!result?.claims_by_type || !Object.keys(result.claims_by_type).length) {
    return 'No claims extracted.'
  }

  return Object.entries(result.claims_by_type)
    .map(([claimType, count]) => `${claimType}: ${count}`)
    .join(' | ')
}

function summarizeClaimSupport(result) {
  if (!result?.claim_support_counts || !Object.keys(result.claim_support_counts).length) {
    return 'No claim support check saved.'
  }

  return Object.entries(result.claim_support_counts)
    .map(([status, count]) => `${status}: ${count}`)
    .join(' | ')
}

function renderFieldRows(result) {
  if (!result || !result.field_results?.length) {
    return '<tr><td colspan="6">No field data available.</td></tr>'
  }

  return result.field_results
    .map((row) => {
      const rowClass = row.scored_in_prompt ? (row.is_match ? 'match' : 'miss') : 'unscored'
      const evidence = [row.positive_hits, row.negative_hits].filter(Boolean).join(' / ')
      const patterns = [row.matched_positive_patterns, row.matched_negative_patterns].filter(Boolean).join(' / ')

      return `
        <tr class="${rowClass}">
          <td>${escapeHtml(row.field_label)}</td>
          <td>${row.scored_in_prompt ? 'Scored' : 'Not scored'}</td>
          <td>${formatTruth(row.predicted)}</td>
          <td>${formatTruth(row.ground_truth)}</td>
          <td>${escapeHtml(row.error_type || (row.is_match === null || row.is_match === undefined ? 'unscored' : row.is_match ? 'match' : 'miss'))}</td>
          <td>${escapeHtml(evidence || '-')}</td>
        </tr>
      `
    })
    .join('')
}

function renderClaimRows(result) {
  if (!result || !result.claims?.length) {
    return '<tr><td colspan="4">No claims extracted for this response.</td></tr>'
  }

  return result.claims
    .map((claim) => {
      const statusClass =
        claim.support_status === 'supported'
          ? 'match'
          : claim.support_status === 'unsupported'
            ? 'miss'
            : 'unscored'
      return `
        <tr class="${statusClass}">
          <td>${escapeHtml(claim.claim_id)}</td>
          <td>${escapeHtml(claim.claim_type)}</td>
          <td>${escapeHtml(claim.support_status || 'not_checked')}</td>
          <td>${escapeHtml(claim.source_text)}</td>
        </tr>
      `
    })
    .join('')
}

function renderClaimUnitRows(result) {
  if (!result || !result.claim_units?.length) {
    return '<tr><td colspan="4">No split units saved for this response.</td></tr>'
  }

  return result.claim_units
    .map((unit) => {
      return `
        <tr class="${unit.looks_like_claim ? 'match' : 'unscored'}">
          <td>${unit.unit_index}</td>
          <td>${unit.looks_like_claim ? 'Kept' : 'Dropped'}</td>
          <td>${escapeHtml(unit.claim_type || '-')}</td>
          <td>${escapeHtml(unit.source_text)}</td>
        </tr>
      `
    })
    .join('')
}

function renderRunOptions() {
  return data.runs
    .map((run, index) => {
      const provider = run.provider || 'unknown'
      return `<option value="${index}">${escapeHtml(provider)} | ${escapeHtml(run.run_id)}</option>`
    })
    .join('')
}

function renderResultOptions(run) {
  return (run.results || [])
    .map((result, index) => {
      const label = `${result.case_id} | ${result.model_name} | ${result.prompt_id}`
      return `<option value="${index}">${escapeHtml(label)}</option>`
    })
    .join('')
}

function bindEvents() {
  const runSelect = document.querySelector('#run-select')
  const resultSelect = document.querySelector('#result-select')

  if (runSelect) {
    runSelect.addEventListener('change', (event) => {
      state.runIndex = Number(event.target.value)
      state.resultIndex = 0
      render()
    })
  }

  if (resultSelect) {
    resultSelect.addEventListener('change', (event) => {
      state.resultIndex = Number(event.target.value)
      render()
    })
  }
}

function render() {
  const run = data.runs[state.runIndex]

  if (!run) {
    app.innerHTML = `
      <main class="page simple-page">
        <section class="panel">
          <h1>TRACE-ED Demo</h1>
          <p class="muted">No run data found.</p>
          <p class="muted">Run the export step or keep the sample data file in place.</p>
        </section>
      </main>
    `
    return
  }

  const results = run.results || []
  const currentResult = results[state.resultIndex] || results[0]
  const summary = run.summary || {}
  const resultCount = results.length
  const accuracyClass =
    !currentResult ? '' : currentResult.accuracy_percent >= 85 ? 'good' : currentResult.accuracy_percent < 70 ? 'bad' : ''

  app.innerHTML = `
    <main class="page simple-page">
      <section class="panel header-panel">
        <div>
          <h1>TRACE-ED Demo</h1>
          <p class="muted">${usingSampleData ? 'Sample data' : 'Saved run data'}</p>
        </div>
        <div class="header-meta">
          <span>Runs: ${data.runs.length}</span>
          <span>Export: ${escapeHtml(data.export_provider || 'all')}</span>
          <span>Generated: ${escapeHtml(data.generated_at_utc || 'local sample')}</span>
        </div>
      </section>

      <section class="panel">
        <div class="controls simple-controls">
          <div class="control">
            <label for="run-select">Run</label>
            <select id="run-select">${renderRunOptions()}</select>
          </div>
          <div class="control">
            <label for="result-select">Result</label>
            <select id="result-select">${renderResultOptions(run)}</select>
          </div>
        </div>
      </section>

      <section class="panel">
        <h2>Run Summary</h2>
        <div class="metrics simple-metrics">
          <div class="metric-card">
            <span class="metric-label">Run ID</span>
            <span class="metric-text">${escapeHtml(run.run_id)}</span>
          </div>
          <div class="metric-card">
            <span class="metric-label">Provider</span>
            <span class="metric-text">${escapeHtml(run.provider || 'unknown')}</span>
          </div>
          <div class="metric-card">
            <span class="metric-label">Evaluations</span>
            <span class="metric-text">${summary.total_evaluations ?? 0}</span>
          </div>
          <div class="metric-card">
            <span class="metric-label">Average Accuracy</span>
            <span class="metric-text">${summary.overall_average_accuracy ?? 0}%</span>
          </div>
          <div class="metric-card">
            <span class="metric-label">Abstentions</span>
            <span class="metric-text">${summary.abstention_detected_count ?? 0}</span>
          </div>
          <div class="metric-card">
            <span class="metric-label">Results in Run</span>
            <span class="metric-text">${resultCount}</span>
          </div>
        </div>
      </section>

      <section class="panel">
        <h2>Selected Result</h2>
        ${
          currentResult
            ? `
              <div class="result-grid">
                <div><span class="field-name">Case</span><span>${escapeHtml(currentResult.case_id)}</span></div>
                <div><span class="field-name">Model</span><span>${escapeHtml(currentResult.model_name)}</span></div>
                <div><span class="field-name">Prompt</span><span>${escapeHtml(currentResult.prompt_id)}</span></div>
                <div><span class="field-name">Prompt Label</span><span>${escapeHtml(currentResult.prompt_label)}</span></div>
                <div><span class="field-name">Accuracy</span><span class="${accuracyClass}">${currentResult.accuracy_percent}%</span></div>
                <div><span class="field-name">Scored Fields</span><span>${currentResult.correct_scored_fields}/${currentResult.scored_field_count}</span></div>
                <div><span class="field-name">Abstention</span><span>${currentResult.abstention_detected ? 'Yes' : 'No'}</span></div>
                <div><span class="field-name">Units Scanned</span><span>${currentResult.source_unit_count ?? 0}</span></div>
                <div><span class="field-name">Claims Kept</span><span>${currentResult.claim_count ?? 0}</span></div>
              </div>
              <p class="muted compact-note">${escapeHtml(summarizeResult(currentResult))}</p>
              <p class="muted compact-note">${escapeHtml(summarizeClaimSupport(currentResult))}</p>
            `
            : '<p class="muted">No result available in this run.</p>'
        }
      </section>

      <section class="panel">
        <h2>Model Response</h2>
        <div class="text-box">${escapeHtml(currentResult?.raw_response || 'No raw response saved for this result.')}</div>
      </section>

      <section class="panel">
        <h2>Prompt</h2>
        <div class="text-box">${escapeHtml(currentResult?.prompt_text || 'No prompt text saved for this result.')}</div>
      </section>

      <section class="panel">
        <h2>Claim Extraction</h2>
        <p class="muted compact-note">${escapeHtml(summarizeClaimTypes(currentResult))}</p>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Claim ID</th>
                <th>Type</th>
                <th>Support</th>
                <th>Claim Text</th>
              </tr>
            </thead>
            <tbody>
              ${renderClaimRows(currentResult)}
            </tbody>
          </table>
        </div>
      </section>

      <section class="panel">
        <h2>Split Units</h2>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Unit</th>
                <th>Filter</th>
                <th>Type</th>
                <th>Unit Text</th>
              </tr>
            </thead>
            <tbody>
              ${renderClaimUnitRows(currentResult)}
            </tbody>
          </table>
        </div>
      </section>

      <section class="panel">
        <h2>Field Results</h2>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Field</th>
                <th>Status</th>
                <th>Predicted</th>
                <th>Ground truth</th>
                <th>Result type</th>
                <th>Evidence</th>
              </tr>
            </thead>
            <tbody>
              ${renderFieldRows(currentResult)}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  `

  const runSelect = document.querySelector('#run-select')
  const resultSelect = document.querySelector('#result-select')
  if (runSelect) runSelect.value = String(state.runIndex)
  if (resultSelect) resultSelect.value = String(state.resultIndex)

  bindEvents()
}

render()
