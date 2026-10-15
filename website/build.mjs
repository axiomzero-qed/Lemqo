import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { mkdir, readFile, writeFile, copyFile, cp } from 'node:fs/promises';
import { content } from './src/content.mjs';
import { renderPage, renderNotFound } from './src/template.mjs';
import { verify } from './src/checker.mjs';

const root = dirname(fileURLToPath(import.meta.url));
const output = join(root, 'dist');
const assets = join(output, 'assets');
const sourceNames = ['styles.css', 'app.mjs', 'content.mjs', 'checker.mjs', 'favicon.svg'];
const inputs = await Promise.all(sourceNames.map(name => readFile(join(root, 'src', name))));
const version = createHash('sha256').update(Buffer.concat(inputs)).digest('hex').slice(0, 12);
await mkdir(join(output, 'en'), { recursive: true });
await mkdir(join(assets, 'examples'), { recursive: true });
await Promise.all(sourceNames.map(name => copyFile(join(root, 'src', name), join(assets, name))));

const examples = {};
for (const { id } of content.en.examples) {
  const files = await Promise.all(['proof', 'claim'].map(type => readFile(join(root, '..', 'examples', `${id}.${type}.json`), 'utf8')));
  const [proof, claim] = files.map(text => JSON.parse(text));
  verify(claim, proof);
  examples[id] = { proof, claim };
  await Promise.all(['proof', 'claim'].map((type, i) => writeFile(join(assets, 'examples', `${id}.${type}.json`), files[i])));
}
await writeFile(join(assets, 'examples.mjs'), `// These are exact Lemqo repository examples.\nexport default ${JSON.stringify(examples, null, 2)};\n`);
await Promise.all([
  writeFile(join(output, 'index.html'), renderPage(content.zh, version)),
  writeFile(join(output, 'en', 'index.html'), renderPage(content.en, version)),
  writeFile(join(output, '404.html'), renderNotFound(content.zh)),
  copyFile(join(root, '..', 'LICENSE'), join(output, 'LICENSE.txt')),
  writeFile(join(output, 'robots.txt'), 'User-agent: *\nAllow: /\nSitemap: https://lemqo.com/sitemap.xml\n'),
  writeFile(join(output, 'sitemap.xml'), `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n${['', 'en/'].map(path => `  <url><loc>https://lemqo.com/${path}</loc><xhtml:link rel="alternate" hreflang="zh-CN" href="https://lemqo.com/"/><xhtml:link rel="alternate" hreflang="en" href="https://lemqo.com/en/"/></url>`).join('\n')}\n</urlset>\n`),
  writeFile(join(output, '_headers'), `/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: DENY\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'\n/assets/*\n  Cache-Control: public, max-age=0, must-revalidate\n`),
  writeFile(join(output, '_redirects'), '/en /en/ 301\n/zh / 301\n/zh/ / 301\n')
]);
// The share image is committed as a prepared asset, with no generation dependency.
await cp(join(root, 'src', 'fonts'), join(assets, 'fonts'), { recursive: true });
await copyFile(join(root, 'src', 'social-card.png'), join(assets, 'social-card.png'));
console.log(`Lemqo website built: ${output}\nChinese: /\nEnglish: /en/\nStatic assets require no installation.`);
