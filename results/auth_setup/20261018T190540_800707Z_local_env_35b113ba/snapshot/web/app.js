'use strict';
const el = id => document.getElementById(id);
let cases = [], revision = 0;
function busy(value) { el('explain').disabled = value; el('case').disabled = value; el('provider').disabled = value; el('patch').disabled = value; el('retest').disabled = value || !el('patch').value.trim(); }
function show(result) {
  el('status').textContent = `${result.mode}. Evidence: ${result.evidence}` + (result.error ? ` | ${result.error}` : '');
  el('diff').textContent = result.diff || 'No extracted patch.';
  const v = result.validation;
  if (!v || v.not_run) {
    el('outcome').textContent = 'No patch evaluated: ' + (v?.reason || result.status || 'unavailable');
    el('details').textContent = ''; return;
  }
  const summary = split => {
    const ts = v.tests.filter(t => t.split === split);
    return ts.length ? `${ts.filter(t => t.success).length}/${ts.length}` : 'not run';
  };
  el('outcome').textContent = `Compilation: ${v.compilation.success ? 'PASS' : 'FAIL'} | Visible tests: ${summary('visible')} | Held-out tests: ${summary('hidden')} | All tests: ${v.functional_success ? 'PASS' : 'FAIL'}`;
  el('details').textContent = JSON.stringify(v, null, 2);
}
async function post(path, data) {
  const response = await fetch(path, {method:'POST', headers:{'Content-Type':'application/json','X-Local-Review':'1'},body:JSON.stringify(data)});
  const result = await response.json(); if (!response.ok) throw Error(result.error); return result;
}
function selectCase() {
  revision++; el('original').textContent = cases.find(c => c.case_id === el('case').value).source;
  el('patch').value = ''; el('response').textContent = 'Request an explanation for this case.';
  el('diff').textContent = 'No patch yet.'; el('outcome').textContent = 'Not evaluated.'; el('details').textContent = '';
  el('status').textContent = 'Ready. Review the source before generating.'; busy(false);
}
el('case').addEventListener('change', selectCase);
el('patch').addEventListener('input', () => {el('retest').disabled = !el('patch').value.trim();el('outcome').textContent = 'Patch edited. Retest to verify the current text.';});
el('explain').addEventListener('click', async () => {
  const ownRevision = revision; busy(true); el('status').textContent = 'Evaluating locally...';
  try {
    const result = await post('/api/explain', {case_id:el('case').value,provider:el('provider').value});
    if (ownRevision !== revision) return;
    el('response').textContent = result.response || result.error || 'No response received.';
    el('patch').value = result.patch || ''; show(result);
    if (result.response_seconds != null) el('status').textContent += ` | Recorded generation: ${result.response_seconds.toFixed(6)} s`;
  } catch(error) {if (ownRevision === revision) el('status').textContent = error.message;}
  finally {if (ownRevision === revision) busy(false);}
});
el('retest').addEventListener('click', async () => {
  const ownRevision = revision; busy(true); el('status').textContent = 'Compiling and running tests...';
  try {const result = await post('/api/retest', {case_id:el('case').value,patch:el('patch').value});if (ownRevision === revision) show(result);}
  catch(error) {if (ownRevision === revision) el('status').textContent = error.message;}
  finally {if (ownRevision === revision) busy(false);}
});
fetch('/api/cases').then(r => {if (!r.ok) throw Error('Case loading failed');return r.json();}).then(data => {
  cases = data; for (const c of cases) {const option = document.createElement('option');option.value = c.case_id;option.textContent = `${c.case_id} / ${c.category} / ${c.title}`;el('case').append(option);}selectCase();
}).catch(error => {el('status').textContent = error.message;busy(true);});
