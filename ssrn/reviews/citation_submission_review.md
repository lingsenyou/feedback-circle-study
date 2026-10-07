# Citation, authorship metadata and staged-release review

Date: 2026-10-06. Scope: read-only inspection of the SSRN manuscript, submission metadata and `github-release` staging directory. The reviewer created this evidence file only; no manuscript or repository files were edited. This is an AI-assisted internal check, not external peer review, an authorship investigation, or a guarantee of platform acceptance.

## Inspected version

- Manuscript version: v0.2.5, 26-page PDF, seven figures and 21 references.
- Final staged PDF SHA256: `e5e49eeaeca6cba054fbeb07c27b410cc74f90c3e7eda86aafae345744ef4b4b`.
- The staged and local submission PDFs have identical SHA256 hashes.
- All 12 entries in the staged `ssrn/MANIFEST.sha256.json` matched the inspected files.

## Passed checks

The PDF, readable manuscript, README, CITATION.cff and submission metadata agree on the seven-author order: Lingsen You, Yujun Guo, Xinyu Zhong, Zisu Peng, Wentong Wang, Li Shen and Junbo Ge. The first five are joint first authors. Only Li Shen and Junbo Ge are corresponding authors. The title-page contact block now contains only those two corresponding-author contacts. All seven user-provided email addresses and six keywords are present in the private submission metadata.

The PDF and source contain the expanded material-AI-use disclosure. The abstract-with-AI metadata contains the same disclosure with real paragraph breaks. The statement accurately lists literature retrieval, drafting and editing, programming and execution, mathematical checks and figure preparation, and distinguishes internal AI checks from external peer review. Actual human review, grant applicability and individual authorship contributions remain human-author attestations, not independently established by this audit.

Reference numbering now follows first appearance: [7] is Comaniciu and Meer; [21] is the Biomarker Research cohort. Reference [7] has the correct title, author pair, IEEE TPAMI volume 24 issue 5, pages 603-619, year 2002 and DOI 10.1109/34.1000236. The publisher abstract explicitly establishes the relation of mean shift to robust location M-estimation, supporting the manuscript's restrained related-work claim. The manuscript does not transfer that paper's convergence guarantee to its own stochastic process.

Reference [21] has the correct ten authors, title, Biomarker Research 2026 volume 14 article 97 and DOI 10.1186/s40364-026-00993-1. The official paper describes treatment-propensity weighting and sensitivity analyses; the manuscript correctly distinguishes treatment-allocation confounding from feedback participation and does not claim clinical validation. The prior citation audit verified the central retention, performative learning, weighting, selective-label and LLM-background references against primary sources. No fabricated reference was identified.

Key numerical strings agree across the staged source, readable manuscript and PDF, including the primary rounded contrast and interval (0.734; 0.516-0.897), both exploratory response-law contrasts (0.736484 and 0.451047), six weighting-regret values, the finite-run quota regret (0.00000373) and analytic stationary benchmark (0.000003561). The unchanged unrounded original contrast remains in the root README. The PDF explicitly defines Z(w) and the population-weighted optimum. This is a consistency check, not a new independent execution of all simulations.

All seven intended web figure paths resolve to real staged image files. Intended PDF, Word, readable manuscript, reproduction-protocol and review-directory links resolve. The rendered web manuscript contains no unresolved FIGURE placeholders.

## One required webpage correction found

The inspected plain-text monitoring derivation contains `[phi(L_g)-phi(L_h)](L_g-L_h)`. In a Markdown-rendered manuscript this is parsed as a link rather than a product: it hides the multiplier and points at a nonexistent path. The PDF retains the complete product. The release preparer has now added a spacing correction in the public packager for both `ssrn/manuscript.md` and `ssrn/manuscript_ssrn.md`; the packager must be rerun and the resulting files/manifest checked. Historical `v2/theory_notes.md` products with adjacent bracket/parenthesis syntax are inside backtick code spans and do not have this display defect. Other apparent nonexistent link targets from the simple scan are mathematical expressions, not missing figure or document assets.

## Release condition

After the current webpage correction, rehash the staged manifest. Copy this review into the staged review evidence only if desired, and include it in the manifest. Confirm the exact v0.2.5 GitHub release is actually public before submission: at the time of this audit it is still staged and the manuscript's claimed release availability has not been verified. Publishing a GitHub tag does not establish Research Square/SSRN posting or a DOI.

Within the declared scalar-mechanism scope, no remaining citation or author-metadata inconsistency was found. This review supports accurate preprint preparation; it does not certify frontier novelty or a high-impact journal standard.

## Official sources checked

- SSRN submission requirements: https://www.elsevier.support/ssrn/answer/get-started (AI declaration required with the abstract and in the PDF; all author names, affiliations and valid emails required).
- SSRN AI policy: https://www.elsevier.support/ssrn/answer/AI (material use must identify the tool, use and extent; human oversight and accountability required).
- SSRN cross-posting: https://www.elsevier.support/ssrn/news/welcome-to-ssrn-elseviers-preprint-server (cross-posting permitted; multiple records may complicate metrics).
- IEEE publisher reference: https://ieeexplore.ieee.org/document/1000236/.
- Biomarker Research publisher reference: https://link.springer.com/article/10.1186/s40364-026-00993-1.
