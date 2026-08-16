const fs = require('fs');
const path = process.argv[2];
const raw = fs.readFileSync(path, 'utf8');
let data;
try {
  data = JSON.parse(raw);
} catch (e) {
  console.error('PARSE_FAIL', e.message);
  process.exit(1);
}
const expected = [5, 10, 4];
const counts = (data.chapters || []).map((c) => (c.features || []).length);
const text = JSON.stringify(data);
const bad = [];
if (counts.length !== 3) bad.push('chapters=' + counts.length);
if (expected.some((n, i) => counts[i] !== n)) bad.push('counts=' + counts.join(','));
if (text.includes('\ufffd')) bad.push('replacement_char');
if (text.includes('сразу')) bad.push('russian_srazu');
if (/"how"\s*:\s*"[^"]*"\s*,\s*"how"/.test(raw)) bad.push('duplicate_how');
if (/"intro"\s*:\s*"[^"]*"\s*,\s*"intro"/.test(raw)) bad.push('duplicate_intro');
if (!data.lead) bad.push('no_lead');
if (bad.length) {
  console.error('INVALID', bad.join('; '));
  process.exit(1);
}
console.log('OK', path, counts.join(','));
