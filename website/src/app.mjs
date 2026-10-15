import { content } from './content.mjs';
import { expandFormulas, formatFormula, verify } from './checker.mjs';
import examples from './examples.mjs';

const t = content[document.documentElement.lang === 'en' ? 'en' : 'zh'];
const select = selector => document.querySelector(selector);
const tabs = [...document.querySelectorAll('[data-example]')];
const verifyButton = select('#verify-button');
const tamperCheckbox = select('#tamper-checkbox');
let selectedId = 'identity';
let currentProof;
let currentClaim;
let proofURL;
let claimURL;
let running = false;

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function details(rows) {
  const list = element('dl', 'receipt-details');
  for (const [label, value] of rows) {
    const row = element('div');
    row.append(element('dt', '', label), element('dd', '', value));
    list.append(row);
  }
  return list;
}

function showReceipt(state = 'ready', result = null, error = null) {
  const block = select('#receipt-content');
  const symbol = element('div', 'receipt-symbol', { ready: '⊢', valid: '✓', rejected: '×' }[state]);
  symbol.dataset.state = state;
  const status = element('span', `receipt-status${state === 'rejected' ? ' rejected-status' : ''}`, { ready: 'READY', valid: 'VALID', rejected: 'REJECTED' }[state]);
  const title = { ready: t.readyTitle, valid: t.validTitle, rejected: t.rejectedTitle }[state];
  const description = state === 'rejected' ? (tamperCheckbox.checked ? t.rejectedDescription : t.failedDescription) : state === 'valid' ? t.validDescription : t.readyDescription;
  const rows = state === 'valid'
    ? [[t.checked, String(result.checkedSteps).padStart(2, '0')], [t.assumptions, result.openAssumptions], [t.result, t[result.kind]]]
    : state === 'rejected'
      ? [[t.failedStep, error.step == null ? '—' : String(error.step + 1).padStart(2, '0')], [t.result, 'REJECTED']]
      : [[t.checked, '—'], [t.assumptions, '—']];
  block.replaceChildren(symbol, status, element('h3', '', title), element('p', '', description), details(rows));
}

function refreshDownloads() {
  if (proofURL) URL.revokeObjectURL(proofURL);
  if (claimURL) URL.revokeObjectURL(claimURL);
  const proofText = `${JSON.stringify(currentProof, null, 2)}\n`;
  proofURL = URL.createObjectURL(new Blob([proofText], { type: 'application/json;charset=utf-8' }));
  claimURL = URL.createObjectURL(new Blob([`${JSON.stringify(currentClaim, null, 2)}\n`], { type: 'application/json;charset=utf-8' }));
  const proofLink = select('#download-proof');
  const claimLink = select('#download-claim');
  proofLink.href = proofURL;
  proofLink.download = `${selectedId}${tamperCheckbox.checked ? '.altered' : ''}.proof.json`;
  claimLink.href = claimURL;
  claimLink.download = `${selectedId}.claim.json`;
  select('#certificate-json').textContent = proofText;
}

function showExample() {
  const example = t.examples.find(item => item.id === selectedId);
  currentProof = structuredClone(examples[selectedId].proof);
  currentClaim = structuredClone(examples[selectedId].claim);
  if (tamperCheckbox.checked) currentProof.steps.at(-1)[0] = 'and_left';
  const formulas = expandFormulas(currentProof);
  select('#statement-formula').textContent = formatFormula(currentClaim.goal);
  select('#statement-description').textContent = example.explanation;
  select('#tamper-note').hidden = !tamperCheckbox.checked;
  const table = select('#proof-steps');
  table.replaceChildren();
  currentProof.steps.forEach((step, i) => {
    const row = element('tr', tamperCheckbox.checked && i === currentProof.steps.length - 1 ? 'altered' : '');
    row.append(element('td', '', String(i + 1).padStart(2, '0')), element('td', 'math', formatFormula(formulas[step[1]])), element('td', '', t.rules[step[0]]), element('td', 'step-status', '·'));
    table.append(row);
  });
  for (const tab of tabs) {
    const active = tab.dataset.example === selectedId;
    tab.classList.toggle('active', active);
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
  }
  select('#proof-panel').setAttribute('aria-labelledby', `tab-${selectedId}`);
  showReceipt();
  refreshDownloads();
}

tabs.forEach((tab, i) => {
  tab.addEventListener('click', () => {
    if (running) return;
    selectedId = tab.dataset.example;
    tamperCheckbox.checked = false;
    showExample();
  });
  tab.addEventListener('keydown', event => {
    let next;
    if (event.key === 'ArrowRight') next = (i + 1) % tabs.length;
    if (event.key === 'ArrowLeft') next = (i + tabs.length - 1) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next === undefined || running) return;
    event.preventDefault();
    tabs[next].click(); tabs[next].focus();
  });
});
tamperCheckbox.addEventListener('change', showExample);

verifyButton.addEventListener('click', async () => {
  if (running) return;
  running = true;
  verifyButton.disabled = true;
  tamperCheckbox.disabled = true;
  tabs.forEach(tab => { tab.disabled = true; });
  verifyButton.firstChild.textContent = t.verifying;
  select('#proof-panel').setAttribute('aria-busy', 'true');
  try {
    // Let the browser paint the busy state; the result below is an actual check.
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    const result = verify(currentClaim, currentProof);
    showReceipt('valid', result);
    [...select('#proof-steps').rows].forEach(row => { row.classList.add('checked'); row.lastElementChild.textContent = '✓'; });
  } catch (error) {
    showReceipt('rejected', null, error);
    [...select('#proof-steps').rows].forEach((row, i) => {
      if (error.step == null) return;
      if (i < error.step) { row.classList.add('checked'); row.lastElementChild.textContent = '✓'; }
      if (i === error.step) { row.classList.add('rejected'); row.lastElementChild.textContent = '×'; }
    });
  } finally {
    running = false;
    verifyButton.firstChild.textContent = t.verify;
    verifyButton.disabled = false;
    tamperCheckbox.disabled = false;
    tabs.forEach(tab => { tab.disabled = false; });
    select('#proof-panel').setAttribute('aria-busy', 'false');
  }
});

const menuToggle = select('.menu-toggle');
const mobileMenu = select('#mobile-nav');
function closeMenu() {
  menuToggle.setAttribute('aria-expanded', 'false');
  menuToggle.setAttribute('aria-label', t.menu);
  mobileMenu.hidden = true;
}
menuToggle.addEventListener('click', () => {
  const open = menuToggle.getAttribute('aria-expanded') !== 'true';
  menuToggle.setAttribute('aria-expanded', String(open));
  menuToggle.setAttribute('aria-label', open ? t.closeMenu : t.menu);
  mobileMenu.hidden = !open;
});
mobileMenu.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !mobileMenu.hidden) { closeMenu(); menuToggle.focus(); }
});
matchMedia('(min-width: 721px)').addEventListener('change', event => { if (event.matches) closeMenu(); });

const languageSwitch = select('[data-language-switch]');
languageSwitch.addEventListener('click', () => {
  languageSwitch.href = `${t.otherPath}${location.hash}`;
});

if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      document.querySelectorAll('.desktop-nav a').forEach(link => {
        link.classList.toggle('current', link.getAttribute('href') === `#${entry.target.id}`);
      });
    });
  }, { rootMargin: '-12% 0px -65% 0px' });
  ['vision', 'system', 'verify', 'contribute'].forEach(id => observer.observe(document.getElementById(id)));
}

showExample();
verifyButton.disabled = false;
tamperCheckbox.disabled = false;
