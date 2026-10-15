export const repository = 'https://github.com/axiomzero-qed/Lemqo';

export const content = {
  zh: {
    lang: 'zh-CN', locale: 'zh_CN', path: '/', otherPath: '/en/',
    title: 'Lemqo — 从公理出发，让数学自己生长',
    description: 'Lemqo 是开放的 AI for Math 项目。我们追求从零构建、不依赖人类数学家介入的自主数学体系，让每一个证明都能被独立验证。开源，欢迎每一位热爱数学的人。',
    skip: '跳转到正文', nav: ['理念', '体系', '验证', '参与'],
    menu: '打开导航', closeMenu: '收起导航', language: 'Switch to English',
    source: '开源代码', eyebrow: '开放的 AI FOR MATH 项目',
    heroTitle: '从公理出发，<br><em>让数学自己生长。</em>',
    heroDescription: '从零构建一个自主探索的数学体系。<br>让 AI 寻找证明，让每一步推理都经得起验证。',
    heroPrimary: '探索我们的理念', heroSecondary: '亲手验证一个证明',
    heroNote: 'v0.3 · 让核验持续，让证据可复核。',
    graphLabel: '一条可追溯的推理路径', graphAlt: '合取交换律的推导图：假设 P 且 Q，分别得到 P 和 Q，组合为 Q 且 P，再解除假设，证明合取交换律。',
    graphAssumption: '显式假设', graphClosed: '闭合推导', graphCaption: '每一个结论，都有一条回到起点的路径。',
    strip: ['从零构建', '自主探索', '独立验证', '开放协作'],
    visionLabel: '01 / 我们的理念',
    visionTitle: '数学的下一章，<br>由推理写下。',
    visionLead: '我们相信，数学可以拥有一种新的生长方式。',
    visionBody: 'Lemqo 的长期目标是构建一个完全不依赖人类数学家介入的自主数学体系。从明确的公理与推理规则开始，由 AI 提出定义、探索命题、生成证明，再由独立验证器逐步检查。',
    visionFoot: '人类不必为每个结论背书，但每个人都可以检查、复现和参与体系的构建。',
    principles: [
      { title: '从零开始', text: '把公理、规则与依赖放在明处。从最小的形式化起点构建知识，让每个结论都可追溯。', symbol: '∅' },
      { title: '证明可以验证', text: '一个看似合理的答案，还需要一份明确的证明。我们要求每一步推理都能被独立检查和重放。', symbol: '⊢' },
      { title: '数学向所有人开放', text: '开放代码、规则与讨论。数学爱好者、研究者、开发者，都可以在这里留下自己的贡献。', symbol: '∀' }
    ],
    systemLabel: '02 / 体系如何生长', systemTitle: '自由探索。<br><em>严格验证。</em>',
    systemDescription: '生成证明与验证证明，是两件不同的事。<br>AI 可以大胆探索，结论必须回到明确的规则。',
    pipeline: [
      { label: '明确起点', title: '公理与规则', text: '公开体系采用的假设、定义与推理规则。', symbol: '⊙' },
      { label: '自主探索 · 愿景', title: 'AI 寻找证明', text: '探索命题、构造推导，输出明确的证明证书。', symbol: '↗' },
      { label: '记录推导', title: '证明证书', text: '保留每一步结论、所用规则与前提依赖。', symbol: '≡' },
      { label: '独立检查', title: '可重放的验证', text: '检查每一步，并绑定到指定命题及其假设。', symbol: '✓' }
    ],
    systemFoot: '信任来自公开的规则和可复现的检查。', systemLink: '阅读验证规范',
    proofLabel: '03 / 看见一个证明', proofTitle: '别只相信结论。<br><em>检查它的每一步。</em>',
    proofDescription: '选一个命题，重放它的推导。<br>也可以篡改一步，看看验证器会如何回应。',
    labTitle: '证明实验室', local: '在你的浏览器中运行',
    examples: [
      { id: 'identity', label: '恒等律', title: 'P → P', explanation: '假设 P 成立，再解除这个假设，得到 P 蕴含 P。' },
      { id: 'conjunction', label: '合取交换律', title: '(P ∧ Q) → (Q ∧ P)', explanation: '分别取出 P 与 Q，以相反的顺序组合，再解除最初的假设。' },
      { id: 'composition', label: '蕴含的复合', title: '(P → Q) → ((Q → R) → (P → R))', explanation: '先由 P 推出 Q，再由 Q 推出 R，依次解除假设。' }
    ],
    statement: '待验证命题', step: '步骤', formula: '结论', rule: '推理规则',
    verify: '验证证明', verifying: '正在检查…', tamper: '篡改最后一步',
    tamperNote: '最后一步被改为合取消去；原命题保持不变。',
    receiptTitle: '独立检查结果', readyTitle: '等待验证', readyDescription: '验证器将依次检查推理规则、前提依赖，以及结论与命题是否一致。',
    validTitle: '证明通过验证', validDescription: '所有推理步骤通过检查，结论与指定命题一致。',
    rejectedTitle: '证明被拒绝', rejectedDescription: '最后一步不符合合取消去规则。被拒绝的是这份证书，不代表命题为假。',
    failedDescription: '证书未通过检查。请查看失败步骤和原因。',
    checked: '已检查步骤', assumptions: '未解除的假设', result: '结果', closed: '闭合推导', conditional: '有前提的推导', failedStep: '失败步骤',
    readyStatus: 'READY', proofFile: '证明证书', claimFile: '命题文件', json: '查看证书 JSON',
    labNote: '本演示重放仓库中的命题逻辑示例。完整验证与输入检查，请使用开源验证器。',
    labLink: '本地运行指南', noJs: '启用 JavaScript 后可使用交互验证；你也可以下载证书，在本地运行 Lemqo。',
    rules: { assume: '引入假设', imp_intro: '蕴含引入', imp_elim: '蕴含消去', and_intro: '合取引入', and_left: '左合取消去', and_right: '右合取消去', or_left: '左析取引入', or_right: '右析取引入', or_elim: '析取消去', false_elim: '假消去' },
    progressLabel: '04 / 从今天走向未来', progressTitle: '一个宏大的方向。<br>一个可审计的起点。',
    progressDescription: '自主数学体系是我们的长期愿景。<br>今天，Lemqo 从透明的证明验证基础开始。',
    releaseLabel: 'v0.3 / 从一次核验，到持续核验',
    releaseTitle: '让每一次检查，都能留下可靠的证据。',
    releaseDescription: '来自真实批量验证的反馈，推动我们把核验流程做得更易用、更可追溯。',
    releaseLink: '查看 v0.3 更新与下载',
    releaseFeatures: [
      { number: '01', title: '长任务，也能接着做', text: '支持多个定理一起核验，分开构建、导出和检查。单个目标失败后继续运行，已完成的导出可以复用。', link: '了解批量工作流', href: '/blob/main/docs/batch.md' },
      { number: '02', title: '证据，也值得被检查', text: '快速核对已有回执与文件的哈希和声明数。结果清楚标为“一致”，与重新验证证明分别说明。', link: '了解回执审计', href: '/blob/main/docs/batch.md#audit-receipt' },
      { number: '03', title: '让智能体接入验证器', text: '通过 MCP 接口提交证明，使用同一套验证 API。待核验命题、参考文件与可信后端由使用者预先指定。', link: '阅读接入指南', href: '/blob/main/docs/mcp.md' }
    ],
    currentTag: '当前版本 · v0.3', currentTitle: '先把“可验证”做扎实。',
    currentItems: [
      { title: '命题逻辑验证内核', text: '10 条固定的自然演绎规则，检查蕴含、合取、析取与假命题的推导。', link: '查看规范', href: '/blob/main/docs/specification.md' },
      { title: '实验性 Lean 证书路径', text: '限定语料中的 3 个选定主定理已有独立检查记录；这一流程仍处于实验阶段。', link: '查看验证记录', href: '/blob/main/corpus/openai/verification/summary.json' }
    ],
    nextTag: '下一步 · 研究方向', nextTitle: '让信任的基础更坚实。',
    nextItems: [
      { number: '01', title: '社区审计与独立实现', text: '共同审阅规则与代码，探索不同语言的第二个验证器。' },
      { number: '02', title: '形式化规范与可靠性', text: '研究规范、实现与健全性之间的可检查联系。' },
      { number: '03', title: '更丰富的数学表达', text: '在验证基础稳固后，探索量词、定义与更完整的数学体系。' }
    ],
    roadmap: '阅读完整路线图',
    joinLabel: '05 / 一起从零开始', joinTitle: '数学属于每一个<br><em>愿意追问的人。</em>',
    joinDescription: '不论你是数学爱好者、数学家、AI 研究者，还是开发者。<br>带着好奇心来，一起把想法变成可以验证的推理。',
    joinPrimary: '在 GitHub 上参与', joinSecondary: '阅读贡献指南',
    roles: [
      { title: '热爱数学', text: '运行示例，提出问题，分享你想探索的命题。' },
      { title: '研究推理', text: '审阅公理与规则，研究可靠性与形式化表达。' },
      { title: '动手构建', text: '改进验证器、工具、文档与开放协作体验。' }
    ],
    footerLine: '从零出发。每一步都有证明。', footerLicense: '开源 · MIT License', footerDocs: '文档', footerIssues: '讨论与问题', footerTrust: '信任边界', backTop: '回到顶部',
    notFoundTitle: '这条路径还没有证明。', notFoundText: '页面不存在，但探索可以从首页继续。', notFoundLink: '回到 Lemqo'
  },
  en: {
    lang: 'en', locale: 'en_US', path: '/en/', otherPath: '/',
    title: 'Lemqo — From first principles. Toward autonomous mathematics.',
    description: 'An open AI for Math project. Lemqo aims to build an autonomous mathematical system from the ground up, without relying on human mathematicians, with independently verifiable proofs. Open source and open to everyone.',
    skip: 'Skip to content', nav: ['Vision', 'System', 'Verify', 'Contribute'],
    menu: 'Open navigation', closeMenu: 'Close navigation', language: '切换到中文',
    source: 'Source code', eyebrow: 'AN OPEN AI FOR MATH PROJECT',
    heroTitle: 'From first principles.<br><em>Let mathematics<br>grow on its own.</em>',
    heroDescription: 'Building toward autonomous mathematics, from the ground up.<br> AI explores the proof. Every step can be checked.',
    heroPrimary: 'Explore the vision', heroSecondary: 'Verify a proof yourself',
    heroNote: 'v0.3 · Keep checking. Keep the evidence.',
    graphLabel: 'A traceable path of reasoning', graphAlt: 'A proof graph for conjunction commutativity: assume P and Q, extract P and Q, combine Q and P, then discharge the assumption to prove the implication.',
    graphAssumption: 'EXPLICIT ASSUMPTION', graphClosed: 'CLOSED DERIVATION', graphCaption: 'Every conclusion has a path back to its foundations.',
    strip: ['Built from zero', 'Autonomous exploration', 'Independent verification', 'Open collaboration'],
    visionLabel: '01 / OUR VISION', visionTitle: 'The next chapter of math.<br>Written by reasoning.',
    visionLead: 'We believe mathematics can grow in a new way.',
    visionBody: 'Our long-term goal is a mathematical system that develops without relying on human mathematicians. Starting with explicit axioms and inference rules, AI would propose definitions, explore statements, and produce proofs for an independent verifier to check, step by step.',
    visionFoot: 'No human endorsement should be needed for each result. Everyone should be able to inspect, reproduce, and help build the system.',
    principles: [
      { title: 'Start from zero', text: 'Make axioms, rules, and dependencies explicit. Build knowledge from a minimal formal foundation, with a traceable path for every result.', symbol: '∅' },
      { title: 'Make proofs verifiable', text: 'A plausible answer needs an explicit proof. Every inference should be open to independent checking and replay.', symbol: '⊢' },
      { title: 'Keep mathematics open', text: 'Open code, open rules, open discussion. Math enthusiasts, researchers, and developers all have a place to contribute.', symbol: '∀' }
    ],
    systemLabel: '02 / HOW THE SYSTEM GROWS', systemTitle: 'Explore freely.<br><em>Verify rigorously.</em>',
    systemDescription: 'Producing a proof and checking it are separate jobs.<br>AI can explore boldly. Results must follow explicit rules.',
    pipeline: [
      { label: 'THE FOUNDATION', title: 'Axioms & rules', text: 'Publish the assumptions, definitions, and inference rules.', symbol: '⊙' },
      { label: 'AUTONOMY · OUR GOAL', title: 'AI exploration', text: 'Explore statements and construct explicit proof certificates.', symbol: '↗' },
      { label: 'THE RECORD', title: 'Proof certificates', text: 'Record each conclusion, inference rule, and dependency.', symbol: '≡' },
      { label: 'THE CHECK', title: 'Independent replay', text: 'Check every step against a selected claim and its premises.', symbol: '✓' }
    ],
    systemFoot: 'Trust grows from open rules and reproducible checks.', systemLink: 'Read the specification',
    proofLabel: '03 / A PROOF YOU CAN INSPECT', proofTitle: 'Go beyond the conclusion.<br><em>Check every step.</em>',
    proofDescription: 'Choose a statement and replay its derivation.<br>Try altering a step. See what the checker has to say.',
    labTitle: 'Proof laboratory', local: 'Runs in your browser',
    examples: [
      { id: 'identity', label: 'Identity', title: 'P → P', explanation: 'Assume P, then discharge the assumption to derive that P implies P.' },
      { id: 'conjunction', label: 'Conjunction', title: '(P ∧ Q) → (Q ∧ P)', explanation: 'Extract P and Q, combine them in reverse order, then discharge the initial assumption.' },
      { id: 'composition', label: 'Composition', title: '(P → Q) → ((Q → R) → (P → R))', explanation: 'Derive Q from P, then R from Q. Discharge the assumptions in turn.' }
    ],
    statement: 'STATEMENT TO CHECK', step: 'Step', formula: 'Conclusion', rule: 'Inference rule',
    verify: 'Verify this proof', verifying: 'Checking…', tamper: 'Alter the last step',
    tamperNote: 'The last rule is replaced with conjunction elimination. The selected claim stays the same.',
    receiptTitle: 'INDEPENDENT CHECK', readyTitle: 'Ready to verify', readyDescription: 'The checker will inspect each inference, track open assumptions, and bind the result to the selected statement.',
    validTitle: 'Proof verified', validDescription: 'Every inference passed. The conclusion matches the selected statement.',
    rejectedTitle: 'Certificate rejected', rejectedDescription: 'The last step fails conjunction elimination. This rejects the certificate; it does not mean the statement is false.',
    failedDescription: 'The certificate failed verification. Inspect the failed step and its reason.',
    checked: 'Checked steps', assumptions: 'Open assumptions', result: 'Result', closed: 'Closed derivation', conditional: 'Conditional derivation', failedStep: 'Failed step',
    readyStatus: 'READY', proofFile: 'Proof certificate', claimFile: 'Claim file', json: 'Inspect certificate JSON',
    labNote: 'This demo replays propositional-logic examples from the repository. Use the open-source verifier for full verification and input checks.',
    labLink: 'Run it locally', noJs: 'Enable JavaScript for interactive checking, or download a certificate and run Lemqo locally.',
    rules: { assume: 'Assumption', imp_intro: 'Implication introduction', imp_elim: 'Implication elimination', and_intro: 'Conjunction introduction', and_left: 'Left conjunction elimination', and_right: 'Right conjunction elimination', or_left: 'Left disjunction introduction', or_right: 'Right disjunction introduction', or_elim: 'Disjunction elimination', false_elim: 'Falsehood elimination' },
    progressLabel: '04 / FROM TODAY TO TOMORROW', progressTitle: 'An ambitious direction.<br>An auditable beginning.',
    progressDescription: 'Autonomous mathematics is our long-term vision.<br>Today, we begin with transparent proof verification.',
    releaseLabel: 'v0.3 / FROM ONE CHECK TO A LASTING WORKFLOW',
    releaseTitle: 'Every check deserves a clear record.',
    releaseDescription: 'Feedback from real batch verification is making the workflow easier to run, recover, and inspect.',
    releaseLink: 'Explore v0.3 and download',
    releaseFeatures: [
      { number: '01', title: 'Pick up where you left off', text: 'Check multiple theorem targets. Separate build, export, and verification. Continue after a failed target and reuse completed exports.', link: 'Explore the batch workflow', href: '/blob/main/docs/batch.md' },
      { number: '02', title: 'Inspect the evidence, too', text: 'Recompute hashes and declaration counts for an existing receipt. A consistency audit is clearly distinguished from a fresh proof check.', link: 'Understand receipt audits', href: '/blob/main/docs/batch.md#audit-receipt' },
      { number: '03', title: 'Connect an agent to the checker', text: 'Submit proofs through MCP using the same verification APIs. The operator chooses the claim, reference, and trusted backends in advance.', link: 'Read the integration guide', href: '/blob/main/docs/mcp.md' }
    ],
    currentTag: 'CURRENT RELEASE · v0.3', currentTitle: 'First, make verification solid.',
    currentItems: [
      { title: 'Propositional-logic kernel', text: '10 fixed natural-deduction rules for implication, conjunction, disjunction, and falsehood.', link: 'Read the specification', href: '/blob/main/docs/specification.md' },
      { title: 'Experimental Lean certificates', text: '3 selected main theorems in a restricted corpus have independent check records. This path remains experimental.', link: 'Inspect verification records', href: '/blob/main/corpus/openai/verification/summary.json' }
    ],
    nextTag: 'NEXT · RESEARCH DIRECTIONS', nextTitle: 'Strengthen the foundations of trust.',
    nextItems: [
      { number: '01', title: 'Community audit & independent implementations', text: 'Review the calculus and code. Explore a second checker in another language.' },
      { number: '02', title: 'Formal specifications & assurance', text: 'Study checkable links between the specification, implementation, and soundness.' },
      { number: '03', title: 'Richer mathematical expression', text: 'With a solid verification base, explore quantifiers, definitions, and broader mathematics.' }
    ],
    roadmap: 'Read the full roadmap',
    joinLabel: '05 / BUILD FROM ZERO, TOGETHER', joinTitle: 'Mathematics belongs<br><em>to the curious.</em>',
    joinDescription: 'Math enthusiasts, mathematicians, AI researchers, developers.<br> Bring your curiosity. Help turn ideas into verifiable reasoning.',
    joinPrimary: 'Contribute on GitHub', joinSecondary: 'Read the contribution guide',
    roles: [
      { title: 'Explore mathematics', text: 'Run examples, ask questions, and share statements you want to explore.' },
      { title: 'Study reasoning', text: 'Review axioms and rules. Research assurance and formal expression.' },
      { title: 'Build the tools', text: 'Improve checkers, tools, documentation, and the experience of working openly.' }
    ],
    footerLine: 'Start from zero. Prove every step.', footerLicense: 'Open source · MIT License', footerDocs: 'Documentation', footerIssues: 'Issues & ideas', footerTrust: 'Trust boundary', backTop: 'Back to top',
    notFoundTitle: 'This path has no proof yet.', notFoundText: 'The page is missing. Your exploration can continue from the homepage.', notFoundLink: 'Back to Lemqo'
  }
};
