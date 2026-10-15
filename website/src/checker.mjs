// This browser demonstrator checks in-memory examples, not arbitrary JSON bytes.
// For strict byte-level validation and the full resource policy, use Lemqo's CLI.
export class ProofError extends Error {
  constructor(code, message, step = null) {
    super(message);
    this.name = 'ProofError';
    this.code = code;
    this.step = step;
  }
}

const arities = { assume: 2, imp_intro: 3, imp_elim: 4, and_intro: 4,
  and_left: 3, and_right: 3, or_left: 3, or_right: 3, or_elim: 5, false_elim: 3 };
const atomName = /^[A-Za-z][A-Za-z0-9_]{0,63}$/;
const equal = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const key = value => JSON.stringify(value);
const union = (...sets) => new Set(sets.flatMap(set => [...set]));
const remove = (set, value) => new Set([...set].filter(item => item !== key(value)));
function demand(condition, code, message, step = null) {
  if (!condition) throw new ProofError(code, message, step);
}
function schema(value, keys) {
  demand(value && typeof value === 'object' && !Array.isArray(value), 'schema', 'Expected a document object.');
  demand(equal(Object.keys(value).sort(), [...keys].sort()), 'schema', 'Unexpected or missing document fields.');
}
function index(value, bound, label, step = null) {
  demand(Number.isSafeInteger(value) && value >= 0 && value < bound, 'reference', `Invalid ${label} reference.`, step);
}
function claimFormula(value, depth = 0) {
  demand(depth < 64, 'limit', 'Formula depth limit exceeded.');
  if (typeof value === 'string') {
    demand(atomName.test(value), 'schema', 'Invalid atom name.');
    return;
  }
  demand(Array.isArray(value), 'schema', 'Invalid claim formula.');
  if (equal(value, ['false'])) return;
  demand(value.length === 3 && ['imp', 'and', 'or'].includes(value[0]), 'schema', 'Invalid connective.');
  claimFormula(value[1], depth + 1);
  claimFormula(value[2], depth + 1);
}

export function expandFormulas(proof) {
  const formulas = [];
  const depths = [];
  const sizes = [];
  proof.formulas.forEach((row, i) => {
    demand(Array.isArray(row), 'schema', 'Formula row must be an array.');
    if (row[0] === 'atom') {
      demand(row.length === 2 && atomName.test(row[1]) && typeof row[1] === 'string', 'schema', 'Invalid atom row.');
      formulas.push(row[1]); depths.push(1); sizes.push(row[1].length + 2);
    } else if (row[0] === 'false') {
      demand(row.length === 1, 'schema', 'Invalid falsehood row.');
      formulas.push(['false']); depths.push(1); sizes.push(9);
    } else {
      demand(row.length === 3 && ['imp', 'and', 'or'].includes(row[0]), 'schema', 'Invalid formula row.');
      index(row[1], i, 'formula'); index(row[2], i, 'formula');
      const depth = 1 + Math.max(depths[row[1]], depths[row[2]]);
      demand(depth <= 64, 'limit', 'Formula depth limit exceeded.');
      const size = 12 + sizes[row[1]] + sizes[row[2]];
      demand(size <= 10000, 'limit', 'Demo formula size limit exceeded.');
      formulas.push([row[0], formulas[row[1]], formulas[row[2]]]); depths.push(depth); sizes.push(size);
    }
  });
  return formulas;
}

export function formatFormula(formula, nested = false) {
  if (typeof formula === 'string') return formula;
  if (formula[0] === 'false') return '⊥';
  const symbol = { imp: '→', and: '∧', or: '∨' }[formula[0]];
  const text = `${formatFormula(formula[1], true)} ${symbol} ${formatFormula(formula[2], true)}`;
  return nested ? `(${text})` : text;
}

export function verify(claim, proof) {
  schema(claim, ['format', 'logic', 'name', 'premises', 'goal']);
  schema(proof, ['format', 'logic', 'formulas', 'steps', 'root']);
  demand(claim.format === 'lemqo-claim-v1' && proof.format === 'lemqo-proof-v1' && claim.logic === 'ipl' && proof.logic === 'ipl', 'format', 'Unsupported format or logic.');
  demand(typeof claim.name === 'string' && /^[A-Za-z][A-Za-z0-9_.-]{0,63}$/.test(claim.name), 'schema', 'Invalid claim name.');
  demand(Array.isArray(claim.premises) && claim.premises.length <= 256, 'schema', 'Invalid premise list.');
  claimFormula(claim.goal);
  claim.premises.forEach(value => claimFormula(value));
  const allowed = new Set(claim.premises.map(key));
  demand(allowed.size === claim.premises.length, 'schema', 'Duplicate premises.');
  // A smaller demo limit avoids expanding large shared formula DAGs in a browser.
  demand(Array.isArray(proof.formulas) && proof.formulas.length > 0 && proof.formulas.length <= 100, 'limit', 'Demo formula table limit exceeded.');
  demand(Array.isArray(proof.steps) && proof.steps.length > 0 && proof.steps.length <= 200, 'limit', 'Demo step limit exceeded.');
  const formulas = expandFormulas(proof);
  demand(formulas.every(value => key(value).length <= 10000), 'limit', 'Demo formula size limit exceeded.');
  const checked = [];
  proof.steps.forEach((row, i) => {
    demand(Array.isArray(row) && Object.hasOwn(arities, row[0]) && row.length === arities[row[0]], 'schema', 'Invalid rule or rule arity.', i);
    index(row[1], formulas.length, 'conclusion', i);
    row.slice(2).forEach(parent => index(parent, i, 'parent step', i));
    const conclusion = formulas[row[1]];
    const parents = row.slice(2).map(parent => checked[parent]);
    const [a, b, c] = parents;
    let context;
    const inference = (condition, message) => demand(condition, 'inference', message, i);
    const has = (formula, connective) => Array.isArray(formula) && formula[0] === connective;
    switch (row[0]) {
      case 'assume': context = new Set([key(conclusion)]); break;
      case 'imp_intro':
        inference(has(conclusion, 'imp') && equal(a.conclusion, conclusion[2]), 'Implication introduction must discharge the antecedent from a derivation of the consequent.');
        context = remove(a.context, conclusion[1]); break;
      case 'imp_elim':
        inference(has(a.conclusion, 'imp') && equal(a.conclusion[1], b.conclusion) && equal(a.conclusion[2], conclusion), 'Implication elimination requires a matching antecedent and consequent.');
        context = union(a.context, b.context); break;
      case 'and_intro':
        inference(has(conclusion, 'and') && equal(a.conclusion, conclusion[1]) && equal(b.conclusion, conclusion[2]), 'Conjunction introduction requires both matching conjuncts.');
        context = union(a.context, b.context); break;
      case 'and_left': case 'and_right':
        inference(has(a.conclusion, 'and') && equal(conclusion, a.conclusion[row[0] === 'and_left' ? 1 : 2]), 'Conjunction elimination requires a conjunction and the matching conjunct.');
        context = new Set(a.context); break;
      case 'or_left': case 'or_right':
        inference(has(conclusion, 'or') && equal(a.conclusion, conclusion[row[0] === 'or_left' ? 1 : 2]), 'Disjunction introduction requires the matching disjunct.');
        context = new Set(a.context); break;
      case 'or_elim':
        inference(has(a.conclusion, 'or') && equal(b.conclusion, conclusion) && equal(c.conclusion, conclusion), 'Disjunction elimination requires both branches to establish the same conclusion.');
        context = union(a.context, remove(b.context, a.conclusion[1]), remove(c.context, a.conclusion[2])); break;
      case 'false_elim':
        inference(equal(a.conclusion, ['false']), 'Falsehood elimination requires a derivation of falsehood.');
        context = new Set(a.context); break;
    }
    demand(context.size <= 256, 'limit', 'Context limit exceeded.', i);
    checked.push({ conclusion, context });
  });
  index(proof.root, checked.length, 'root');
  const root = checked[proof.root];
  demand(equal(root.conclusion, claim.goal), 'claim', 'The conclusion does not match the independently selected claim.');
  demand([...root.context].every(value => allowed.has(value)), 'premise', 'The proof retains an undeclared assumption.');
  return { status: 'VALID', name: claim.name, checkedSteps: checked.length, openAssumptions: root.context.size, kind: root.context.size ? 'conditional' : 'closed', steps: checked };
}
