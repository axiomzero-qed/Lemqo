import { repository } from './content.mjs';

const arrow = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const diagonal = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 18 18 6M6 6h12v12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const github = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.86c-2.78.6-3.37-1.18-3.37-1.18-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.61.07-.61 1 .07 1.53 1.03 1.53 1.03.9 1.53 2.34 1.09 2.91.83.09-.65.35-1.09.64-1.34-2.22-.25-4.55-1.11-4.55-4.94 0-1.1.39-1.99 1.03-2.69-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.03A9.6 9.6 0 0 1 12 6.83c.85 0 1.71.11 2.51.33 1.91-1.3 2.75-1.03 2.75-1.03.55 1.38.2 2.4.1 2.65.64.7 1.03 1.59 1.03 2.69 0 3.84-2.33 4.69-4.56 4.94.36.31.68.92.68 1.85v2.75c0 .27.18.58.69.48A10 10 0 0 0 12 2Z"/></svg>';
const logo = '<svg class="brand-mark" viewBox="0 0 36 40" fill="none" aria-hidden="true"><path d="M18 2 33 11v18L18 38 3 29V11L18 2Z" stroke="currentColor" stroke-width="1.5"/><path d="M18 2v18L3 29m15-9 15 9M3 11l15 9 15-9M18 20v18" stroke="currentColor" stroke-width="1.5"/><circle cx="18" cy="20" r="3.4" fill="currentColor"/></svg>';
export const escape = text => String(text).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
function external(href, label, className = 'text-link', icon = diagonal) {
  return `<a class="${className}" href="${href}" target="_blank" rel="noopener noreferrer">${label}${icon}</a>`;
}

function proofGraph(t) {
  return `<div class="proof-graph">
    <div class="graph-heading"><span class="tiny-square"></span><span>${t.graphLabel}</span><span class="mono">FIG. 001</span></div>
    <svg class="reasoning-svg" viewBox="0 0 600 490" role="img" aria-labelledby="graph-title">
      <title id="graph-title">${t.graphAlt}</title>
      <defs><pattern id="dot-grid" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="#c9c9bf"/></pattern>
      <marker id="graph-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="m1 1 6 3-6 3" fill="none" stroke="#a55b42" stroke-width="1.2"/></marker></defs>
      <rect width="600" height="490" fill="url(#dot-grid)"/>
      <g fill="none" stroke="#d4d4c8" stroke-width="1.1" stroke-dasharray="4 6"><path d="M70 18v90h100M520 170v-60h-80M90 390v-55h62M525 465v-112h-73"/><circle cx="70" cy="18" r="4" fill="#eeeee7"/><circle cx="520" cy="170" r="4" fill="#eeeee7"/><circle cx="90" cy="390" r="4" fill="#eeeee7"/><circle cx="525" cy="465" r="4" fill="#eeeee7"/></g>
      <g class="graph-paths" fill="none" stroke="#a55b42" stroke-width="1.5" marker-end="url(#graph-arrow)"><path d="M300 112v20c0 25-126 15-126 48v13"/><path d="M300 112v20c0 25 126 15 126 48v13"/><path d="M174 257v17c0 22 126 16 126 42"/><path d="M426 257v17c0 22-126 16-126 42"/><path d="M300 365v42"/></g>
      <g class="graph-rule" fill="#837a69"><text x="173" y="168">∧E₁</text><text x="434" y="168">∧E₂</text><text x="315" y="296">∧I</text><text x="315" y="391">→I</text></g>
      <g class="graph-node"><rect x="206" y="41" width="188" height="72" rx="5"/><text class="node-label" x="300" y="62">${t.graphAssumption}</text><text class="node-formula" x="300" y="95">P ∧ Q</text></g>
      <g class="graph-node"><rect x="118" y="194" width="112" height="62" rx="5"/><text class="node-formula" x="174" y="235">P</text><rect x="370" y="194" width="112" height="62" rx="5"/><text class="node-formula" x="426" y="235">Q</text></g>
      <g class="graph-node"><rect x="216" y="316" width="168" height="50" rx="5"/><text class="node-formula" x="300" y="350">Q ∧ P</text></g>
      <g class="graph-final"><rect x="119" y="408" width="362" height="72" rx="5"/><circle cx="148" cy="434" r="3"/><text class="node-label" x="161" y="437">${t.graphClosed}</text><text class="final-formula" x="300" y="464">⊢ (P ∧ Q) → (Q ∧ P)</text></g>
      <g class="graph-points" fill="#a55b42"><circle cx="300" cy="132" r="3"/><circle cx="174" cy="274" r="3"/><circle cx="426" cy="274" r="3"/></g>
    </svg>
    <div class="graph-caption"><span class="graph-caption-line"></span>${t.graphCaption}</div>
  </div>`;
}

export function renderPage(t, version) {
  const code = version;
  const path = t.path;
  return `<!doctype html>
<html lang="${t.lang}">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${t.title}</title><meta name="description" content="${escape(t.description)}">
  <meta name="theme-color" content="#f7f7f0"><meta name="color-scheme" content="light">
  <link rel="canonical" href="https://lemqo.com${path}">
  <link rel="alternate" hreflang="zh-CN" href="https://lemqo.com/">
  <link rel="alternate" hreflang="en" href="https://lemqo.com/en/">
  <link rel="alternate" hreflang="x-default" href="https://lemqo.com/">
  <meta property="og:type" content="website"><meta property="og:site_name" content="Lemqo">
  <meta property="og:title" content="${escape(t.title)}"><meta property="og:description" content="${escape(t.description)}">
  <meta property="og:url" content="https://lemqo.com${path}"><meta property="og:locale" content="${t.locale}">
  <meta property="og:image" content="https://lemqo.com/assets/social-card.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  ${t.lang === 'zh-CN' ? '<link rel="preload" href="/assets/fonts/noto-sans-sc.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/assets/fonts/noto-serif-sc.woff2" as="font" type="font/woff2" crossorigin>' : ''}
  <link rel="stylesheet" href="/assets/styles.css?v=${code}">
  <script type="module" src="/assets/app.mjs?v=${code}"></script>
</head>
<body id="top">
  <a class="skip-link" href="#main">${t.skip}</a>
  <header class="site-header"><div class="header-inner wrap">
    <a class="brand" href="${path}" aria-label="Lemqo">${logo}<span>Lemqo<span class="brand-dot">.</span></span></a>
    <nav class="desktop-nav" aria-label="${t.lang === 'en' ? 'Main navigation' : '主导航'}">
      ${['vision', 'system', 'verify', 'contribute'].map((id, i) => `<a href="#${id}">${t.nav[i]}</a>`).join('')}
    </nav>
    <div class="header-actions">
      <a class="language-switch" data-language-switch href="${t.otherPath}" lang="${t.lang === 'en' ? 'zh-CN' : 'en'}" hreflang="${t.lang === 'en' ? 'zh-CN' : 'en'}" aria-label="${t.language}"><span class="${t.lang === 'en' ? '' : 'active'}">中文</span><span class="language-divider">/</span><span class="${t.lang === 'en' ? 'active' : ''}">EN</span></a>
      ${external(repository, github + `<span>${t.source}</span>`, 'header-source', '')}
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-nav" aria-label="${t.menu}"><span></span><span></span></button>
    </div>
  </div><nav class="mobile-nav" id="mobile-nav" aria-label="${t.lang === 'en' ? 'Mobile navigation' : '移动导航'}" hidden>${['vision', 'system', 'verify', 'contribute'].map((id, i) => `<a href="#${id}">${t.nav[i]}${arrow}</a>`).join('')}${external(repository, t.source, 'mobile-source')}</nav></header>

  <main id="main">
    <section class="hero wrap" aria-labelledby="hero-title">
      <div class="hero-copy"><p class="eyebrow"><span class="tiny-square"></span>${t.eyebrow}</p>
        <h1 id="hero-title">${t.heroTitle}</h1><p class="hero-description">${t.heroDescription}</p>
        <div class="hero-actions"><a class="button button-dark" href="#vision">${t.heroPrimary}${arrow}</a><a class="text-link" href="#verify">${t.heroSecondary}${diagonal}</a></div>
        <p class="hero-note"><span class="little-cross">+</span>${t.heroNote}</p>
      </div>
      ${proofGraph(t)}
      <div class="hero-bottom"><span class="mono">LEM Q.E.D.</span><span>OPEN SOURCE. OPEN POSSIBILITIES.</span><a href="#vision" aria-label="${t.heroPrimary}" class="scroll-cue">↓</a></div>
    </section>

    <div class="principle-strip"><div class="wrap">${t.strip.map((text, i) => `<span><span class="strip-symbol">${['∅', '↗', '⊢', '∀'][i]}</span>${text}</span>`).join('')}</div></div>

    <section class="vision section wrap" id="vision" aria-labelledby="vision-title">
      <p class="section-label">${t.visionLabel}</p>
      <div class="vision-intro"><h2 id="vision-title">${t.visionTitle}</h2><div class="vision-body"><p class="lead">${t.visionLead}</p><p>${t.visionBody}</p><p class="muted">${t.visionFoot}</p></div></div>
      <div class="principles">${t.principles.map((item, i) => `<article class="principle"><div class="principle-top"><span class="mono">0${i + 1}</span><span class="principle-symbol">${item.symbol}</span></div><h3>${item.title}</h3><p>${item.text}</p></article>`).join('')}</div>
    </section>

    <section class="system-section" id="system" aria-labelledby="system-title"><div class="wrap section">
      <p class="section-label">${t.systemLabel}</p><div class="section-intro"><h2 id="system-title">${t.systemTitle}</h2><p>${t.systemDescription}</p></div>
      <div class="pipeline">${t.pipeline.map((item, i) => `<article class="pipeline-step"><div class="pipeline-top"><span class="pipeline-symbol">${item.symbol}</span><span class="mono">0${i + 1}</span>${i < 3 ? '<span class="pipeline-arrow">→</span>' : ''}</div><p class="pipeline-label">${item.label}</p><h3>${item.title}</h3><p>${item.text}</p></article>`).join('')}</div>
      <div class="system-bottom"><p><span class="tiny-square"></span>${t.systemFoot}</p>${external(repository + '/blob/main/docs/specification.md', t.systemLink)}</div>
    </div></section>

    <section class="proof-section section wrap" id="verify" aria-labelledby="proof-title">
      <p class="section-label">${t.proofLabel}</p><div class="section-intro"><h2 id="proof-title">${t.proofTitle}</h2><p>${t.proofDescription}</p></div>
      <div class="proof-lab"><div class="lab-bar"><span><span class="lab-icon">⊢</span>${t.labTitle}</span><span class="lab-local"><span class="status-dot"></span>${t.local}</span></div>
        <div class="proof-tabs" role="tablist" aria-label="${t.lang === 'en' ? 'Proof examples' : '证明示例'}">${t.examples.map((example, i) => `<button class="proof-tab${i === 0 ? ' active' : ''}" id="tab-${example.id}" type="button" role="tab" aria-selected="${i === 0}" aria-controls="proof-panel" tabindex="${i === 0 ? 0 : -1}" data-example="${example.id}">${example.label}<span class="tab-index">0${i + 1}</span></button>`).join('')}</div>
        <div class="lab-body" id="proof-panel" role="tabpanel" aria-labelledby="tab-identity" tabindex="0">
          <div class="proof-workspace"><p class="small-label">${t.statement}</p><div id="statement-formula" class="statement-formula">P → P</div><p id="statement-description" class="statement-description">${t.examples[0].explanation}</p>
            <div class="proof-table-scroll"><table class="proof-table"><thead><tr><th scope="col">${t.step}</th><th scope="col">${t.formula}</th><th scope="col">${t.rule}</th><th scope="col" aria-label="${t.lang === 'en' ? 'Check status' : '检查状态'}"></th></tr></thead><tbody id="proof-steps"><tr><td>01</td><td class="math">P</td><td>${t.rules.assume}</td><td class="step-status">·</td></tr><tr><td>02</td><td class="math">P → P</td><td>${t.rules.imp_intro}</td><td class="step-status">·</td></tr></tbody></table></div>
            <div class="proof-controls"><button class="button button-dark" type="button" id="verify-button" disabled>${t.verify}${arrow}</button><label class="tamper-control"><input type="checkbox" id="tamper-checkbox" disabled><span class="switch-track" aria-hidden="true"></span><span>${t.tamper}</span></label></div>
            <p class="tamper-note" id="tamper-note" hidden>${t.tamperNote}</p>
          </div>
          <aside class="receipt" aria-label="${t.receiptTitle}"><div class="receipt-heading"><span>${t.receiptTitle}</span><span class="receipt-corner">↗</span></div><div id="receipt-content" aria-live="polite" aria-atomic="true"><div class="receipt-symbol" data-state="ready">⊢</div><span class="receipt-status">READY</span><h3>${t.readyTitle}</h3><p>${t.readyDescription}</p><dl class="receipt-details"><div><dt>${t.checked}</dt><dd>—</dd></div><div><dt>${t.assumptions}</dt><dd>—</dd></div></dl></div><div class="receipt-footer"><span class="mono">lemqo-proof-v1</span><span class="mono">IPL</span></div></aside>
        </div>
        <div class="lab-files"><details class="certificate-details"><summary>${t.json}<span>+</span></summary><pre id="certificate-json">${escape(JSON.stringify({ format: 'lemqo-proof-v1', logic: 'ipl', formulas: [['atom', 'P'], ['imp', 0, 0]], steps: [['assume', 0], ['imp_intro', 1, 0]], root: 1 }, null, 2))}</pre></details><div class="download-links"><a id="download-proof" href="/assets/examples/identity.proof.json" download="identity.proof.json">${t.proofFile}<span>↓</span></a><a id="download-claim" href="/assets/examples/identity.claim.json" download="identity.claim.json">${t.claimFile}<span>↓</span></a></div></div>
      </div>
      <noscript><p class="no-js">${t.noJs}</p></noscript>
      <div class="lab-note"><p>${t.labNote}</p>${external(repository + '#try-a-valid-and-an-invalid-proof', t.labLink)}</div>
    </section>

    <section class="progress-section section wrap" id="progress" aria-labelledby="progress-title"><p class="section-label">${t.progressLabel}</p><div class="section-intro"><h2 id="progress-title">${t.progressTitle}</h2><p>${t.progressDescription}</p></div>
      <article class="release-panel" aria-labelledby="release-title"><div class="release-intro"><div><p class="section-label">${t.releaseLabel}</p><h3 id="release-title">${t.releaseTitle}</h3><p>${t.releaseDescription}</p></div>${external(repository + '/releases/tag/v0.3.0', t.releaseLink)}</div><div class="release-features">${t.releaseFeatures.map(item => `<section><span class="mono">${item.number}</span><h4>${item.title}</h4><p>${item.text}</p>${external(repository + item.href, item.link)}</section>`).join('')}</div></article>
      <div class="progress-grid"><article class="current-progress"><p class="progress-tag"><span class="status-dot"></span>${t.currentTag}</p><h3>${t.currentTitle}</h3>${t.currentItems.map(item => `<div class="current-item"><h4>${item.title}</h4><p>${item.text}</p>${external(repository + item.href, item.link)}</div>`).join('')}</article>
        <article class="next-progress"><p class="progress-tag">${t.nextTag}</p><h3>${t.nextTitle}</h3><ol class="next-list">${t.nextItems.map(item => `<li><span class="mono">${item.number}</span><div><h4>${item.title}</h4><p>${item.text}</p></div></li>`).join('')}</ol>${external(repository + '/blob/main/docs/roadmap.md', t.roadmap)}</article>
      </div>
    </section>

    <section class="join-section" id="contribute" aria-labelledby="join-title"><div class="wrap section"><p class="section-label">${t.joinLabel}</p><div class="join-intro"><div><h2 id="join-title">${t.joinTitle}</h2><p>${t.joinDescription}</p><div class="join-actions">${external(repository, github + t.joinPrimary, 'button button-paper', arrow)}${external(repository + '/blob/main/CONTRIBUTING.md', t.joinSecondary)}</div></div><div class="join-art" aria-hidden="true"><span class="join-orbit orbit-one"></span><span class="join-orbit orbit-two"></span><span class="join-orbit orbit-three"></span><span class="join-art-symbol">∀</span><span class="join-art-caption">FOR ALL THE CURIOUS.</span></div></div><div class="join-roles">${t.roles.map((item, i) => `<article><span class="mono">0${i + 1}</span><h3>${item.title}</h3><p>${item.text}</p></article>`).join('')}</div></div></section>
  </main>

  <footer class="site-footer"><div class="wrap"><div class="footer-main"><div><a class="brand" href="${path}" aria-label="Lemqo">${logo}<span>Lemqo<span class="brand-dot">.</span></span></a><p>${t.footerLine}</p></div><div class="footer-links">${external(repository + '/tree/main/docs', t.footerDocs)}${external(repository + '/issues', t.footerIssues)}${external(repository + '/blob/main/docs/trust.md', t.footerTrust)}</div></div><div class="footer-bottom"><span>© ${new Date().getUTCFullYear()} Lemqo contributors</span>${external(repository + '/blob/main/LICENSE', t.footerLicense, 'license-link', '')}<a href="#top" class="back-top">${t.backTop}<span>↑</span></a></div></div></footer>
</body></html>`;
}

export function renderNotFound(t) {
  return `<!doctype html><html lang="${t.lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><title>404 — Lemqo</title><link rel="icon" href="/assets/favicon.svg"><link rel="stylesheet" href="/assets/styles.css"></head><body><main class="not-found wrap"><a class="brand" href="/">${logo}<span>Lemqo.</span></a><p class="section-label">404 / PATH NOT FOUND</p><h1>${t.notFoundTitle}</h1><p>${t.notFoundText}</p><a class="button button-dark" href="/">${t.notFoundLink}${arrow}</a><a class="text-link" href="/en/">English${arrow}</a></main></body></html>`;
}
