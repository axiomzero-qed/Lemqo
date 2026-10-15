import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { verify, ProofError, expandFormulas } from '../src/checker.mjs';

const project = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const examples = join(project, 'examples');
const load = async name => JSON.parse(await readFile(join(examples, name), 'utf8'));
const proofFiles = (await readdir(examples)).filter(file => file.endsWith('.proof.json'));
for (const filename of proofFiles) {
  test(`browser checker agrees with the Python CLI on ${filename}`, async () => {
    const id = filename.replace(/(?:\.invalid)?\.proof\.json$/, '');
    const claimFilename = `${id}.claim.json`;
    const [claim, proof] = await Promise.all([load(claimFilename), load(filename)]);
    const cli = spawnSync(process.env.LEMQO_PYTHON || 'python', ['-m', 'lemqo', 'check', join(examples, filename), '--claim', join(examples, claimFilename), '--json'], { cwd: project, encoding: 'utf8', timeout: 10000 });
    assert.ifError(cli.error);
    assert.ok(cli.status === 0 || cli.status === 1, cli.stderr);
    if (cli.status === 0) {
      const reference = JSON.parse(cli.stdout);
      const receipt = verify(claim, proof);
      assert.equal(receipt.status, reference.status.toUpperCase());
      assert.equal(receipt.checkedSteps, reference.checked_steps);
      assert.equal(receipt.kind, reference.kind);
      assert.equal(receipt.openAssumptions, reference.used_premise_indices.length);
    } else assert.throws(() => verify(claim, proof), ProofError);
  });
}

for (const id of ['identity', 'conjunction', 'composition']) {
  test(`altering the final inference is rejected: ${id}`, async () => {
    const [claim, proof] = await Promise.all([load(`${id}.claim.json`), load(`${id}.proof.json`)]);
    proof.steps.at(-1)[0] = 'and_left';
    assert.throws(() => verify(claim, proof), error => error.code === 'inference' && error.step === proof.steps.length - 1);
  });
}

test('the selected claim cannot be replaced by a different proof conclusion', async () => {
  const [claim, proof] = await Promise.all([load('identity.claim.json'), load('identity.proof.json')]);
  claim.goal = 'P';
  assert.throws(() => verify(claim, proof), error => error.code === 'claim');
});

test('invalid unused nodes are checked too', async () => {
  const [claim, proof] = await Promise.all([load('identity.claim.json'), load('identity.proof.json')]);
  proof.steps.push(['and_left', 0, 0]);
  assert.throws(() => verify(claim, proof), error => error.step === 2 && error.code === 'inference');
});

test('discharging an assumption does not mutate its shared parent context', async () => {
  const proof = { format: 'lemqo-proof-v1', logic: 'ipl', formulas: [['atom', 'P'], ['imp', 0, 0]], steps: [['assume', 0], ['imp_intro', 1, 0], ['imp_elim', 0, 1, 0]], root: 2 };
  const claim = { format: 'lemqo-claim-v1', logic: 'ipl', name: 'shared_context', premises: [], goal: 'P' };
  assert.throws(() => verify(claim, proof), error => error.code === 'premise');
});

test('formula aliases have structural identity when discharging an assumption', () => {
  const proof = { format: 'lemqo-proof-v1', logic: 'ipl', formulas: [['atom', 'P'], ['atom', 'P'], ['imp', 1, 1]], steps: [['assume', 0], ['imp_intro', 2, 0]], root: 1 };
  const claim = { format: 'lemqo-claim-v1', logic: 'ipl', name: 'alias', premises: [], goal: ['imp', 'P', 'P'] };
  assert.equal(verify(claim, proof).kind, 'closed');
});

test('boolean references are rejected', async () => {
  const [claim, proof] = await Promise.all([load('identity.claim.json'), load('identity.proof.json')]);
  proof.steps[1][2] = false;
  assert.throws(() => verify(claim, proof), error => error.code === 'reference');
});

test('a shared formula DAG is bounded before expansion becomes expensive', () => {
  const formulas = [['atom', 'P']];
  for (let i = 1; i < 60; i++) formulas.push(['and', i - 1, i - 1]);
  assert.throws(() => expandFormulas({ formulas }), error => error.code === 'limit');
});
