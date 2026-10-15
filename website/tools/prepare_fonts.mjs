// Optional asset preparation. The website serves these open fonts locally.
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { content } from '../src/content.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const directory = join(root, 'src', 'fonts');
await mkdir(directory, { recursive: true });
const source = JSON.stringify(content).replace(/<[^>]+>/g, '');
const chars = [...new Set([...source + '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?/:;()[]{}+−→↗↓↑∅⊢∀∧∨⊥≡⊙✓×—中文EN'])].sort().join('');
async function fetchAsset(url, options = {}) {
  let failure;
  for (let attempt = 0; attempt < 3; attempt++) {
    try { return await fetch(url, { ...options, signal: AbortSignal.timeout(20000) }); }
    catch (error) { failure = error; }
  }
  throw failure;
}
for (const [family, filename, licensePath] of [
  ['Noto Sans SC', 'noto-sans-sc.woff2', 'notosanssc'],
  ['Noto Serif SC', 'noto-serif-sc.woff2', 'notoserifsc']
]) {
  const query = new URLSearchParams({ family: `${family}:wght@400..600`, display: 'swap', text: chars });
  const response = await fetchAsset(`https://fonts.googleapis.com/css2?${query}`, { headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' } });
  if (!response.ok) throw new Error(`${family}: CSS request failed (${response.status})`);
  const css = await response.text();
  const urls = [...new Set([...css.matchAll(/url\((https:\/\/[^)]+)\)/g)].map(match => match[1]))];
  if (urls.length !== 1) throw new Error(`${family}: expected a single variable subset, got ${urls.length}; weights: ${[...css.matchAll(/font-weight:\s*([^;]+)/g)].map(match => match[1]).join(', ')}`);
  const assetResponse = await fetchAsset(urls[0]);
  if (!assetResponse.ok) throw new Error(`${family}: asset request failed (${assetResponse.status})`);
  const bytes = Buffer.from(await assetResponse.arrayBuffer());
  await writeFile(join(directory, filename), bytes);
  const licenseResponse = await fetchAsset(`https://raw.githubusercontent.com/google/fonts/main/ofl/${licensePath}/OFL.txt`);
  if (!licenseResponse.ok) throw new Error(`${family}: license request failed (${licenseResponse.status})`);
  await writeFile(join(directory, `${licensePath}-OFL.txt`), await licenseResponse.text());
  console.log(`${family}: ${Math.round(bytes.length / 1024)} KB; OFL license saved.`);
}
