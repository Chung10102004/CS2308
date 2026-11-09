# BioRerank Luna-only completion plan

**Goal:** Finish the remaining project work using GPT-6 Luna as the only paid model, with a reviewable cost estimate before additional paid experiments.

**Scope:** Existing local rerankers remain comparators. Do not run Jev or GPT-6.1 Sol. Reuse the completed E1 runs and cache. Never generate relevance labels with an LLM, tune on test, or invent missing metadata/results.

**Execution:** Continue in the existing checkout to preserve the user's uncommitted results and local data. No branch, commit, push, or new worktree is needed for the requested experiment and artifact work.

- [ ] Estimate E2 criteria/query/metadata/order variants, E3 SciFact-Open, E4 candidate-count/cascade, and a small demo allowance. Distinguish exact input-token estimates from approximations. Save assumptions and a contingency amount.
- [ ] Restore missing data-loading modules and data sources with fixture tests. Correct the ignore pattern that also excludes `src/data/`. Preserve existing runs and verify baseline metrics and split identity.
- [ ] Add a Luna-only execution path with budget enforcement and tests proving that unselected models are never scheduled. Restore reusable evaluation commands rather than depending on ignored operational scripts.
- [ ] Finish work that does not require paid calls: audit BiLSTM seeds/artifact availability, generate error cases, prepare report updates and demo checks.
- [ ] Present the additional API cost for approval under NLP_PROJECT_PLAN.md section 16 before running a job estimated above USD 5. No additional paid requests until the estimate is reviewed.
- [ ] After approval, run selected experiments with cache, usage logs and candidate-coverage checks; refresh statistics, tables and figures.
- [ ] Validate the demo and prepare final report/slides from verified results; clearly list any compute/account/data blockers.

**Verification:** Unit tests with synthetic/local fixtures, existing API mock tests, baseline-score reproduction, raw permutation/candidate identity checks, complete experiment logs, and visual inspection of report/deck figures.

**Current evidence:** E1 completed: 673 queries, 5,182 API calls, USD 3.7783738 from logs. Missing `src/data/`, E2 narrative/metadata files, SciFact-Open corpus/claims, and some BiLSTM seed outputs. Existing draft and slide work depend on completing or explicitly qualifying these items.

## Execution record 09/11/2026

- [x] Remaining API estimate produced without model calls: E2 USD 7.9662, E3 USD 2.0132 on restored real text, E4 USD 0.4973, subtotal USD 10.4766. Three metadata variants still use abstract-only token proxies.
- [x] User explicitly declined new paid API work. E2/E3/E4 new GPT runs remain unexecuted; no further approval is pending.
- [x] Restored BEIR ZIP readers, NIST topics/qrels and SciFact-Open readers; fixed `/data/` ignore scope. Public SciFact-Open archive has 500,000 abstracts; the inference pack contains only the 23,039 documents needed by saved candidates.
- [x] Safe CLI defaults: estimate only and GPT-small only; explicit execution and estimate ceiling tested; missing metadata rejected.
- [x] Full test suite: 23 passing before slide generation. Existing E1 statistics, E3 and E4 rerun without model calls. E3 TREC now includes GPT from E1; historic E2 metadata analyses preserved and only known GPT baseline values added.
- [x] Error cases regenerated; abstract, conclusions, scope limitations and stale E3 ranks corrected in report. Release copy: `report/BioRerank.md`.
- [x] Offline demo implemented and checked in the browser, including dataset switching and before/after query scores. It never loads an API key or model client.
- [x] User changed slide format to HTML. Created `report/slides/BioRerank.html` and reusable `scripts/build_slides.py`; 17 slides checked for overflow at 16:9, with navigation/overview/notes and three saved-result examples checked. No PowerPoint export was performed after the user declined it.
- [ ] Original processed metadata, exact training split IDs, embeddings/checkpoints and Kaggle GPU access remain missing. Extra BiLSTM ablation seeds cannot be honestly completed from this checkout alone.

Browser limitation: automatic `file://` navigation is blocked by the browser policy; HTML was verified over the local HTTP server. No workaround for that blocked action was attempted.
