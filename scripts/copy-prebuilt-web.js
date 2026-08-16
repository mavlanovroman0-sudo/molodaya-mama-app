const fs = require('fs');
const path = require('path');

const src = path.join('frontend', 'dist');
const dest = path.join('frontend', 'prebuilt-web');

function rmrf(dir) {
  if (!fs.existsSync(dir)) return;
  fs.rmSync(dir, { recursive: true, force: true });
}

function copyDir(from, to) {
  fs.mkdirSync(to, { recursive: true });
  for (const entry of fs.readdirSync(from, { withFileTypes: true })) {
    const a = path.join(from, entry.name);
    const b = path.join(to, entry.name);
    if (entry.isDirectory()) copyDir(a, b);
    else fs.copyFileSync(a, b);
  }
}

if (!fs.existsSync(src)) throw new Error('missing ' + src);
rmrf(dest);
copyDir(src, dest);

const indexPath = path.join(dest, 'index.html');
let html = fs.readFileSync(indexPath, 'utf8');
if (!html.includes('<title>')) {
  html = html.replace('<head>', '<head>\n    <title>молодая мама</title>');
} else if (!/<title>[^<]*<\/title>/.test(html)) {
  html = html.replace(/<title>[\s\S]*?<\/title>/, '<title>молодая мама</title>');
}
html = html.replace(/<html[^>]*>/, '<html lang="ru">');
fs.writeFileSync(indexPath, html, 'utf8');
console.log('copied', dest);
console.log('title', (html.match(/<title>([^<]*)<\/title>/) || [])[1]);
