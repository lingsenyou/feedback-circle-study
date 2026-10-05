# Revision 2 materials

The revised manuscript contains 18 pages, seven figures, twenty references, and a derivation appendix. It is a synthetic computational mechanism study. It does not test human participants, clinical outcomes, a language model, or retained learned knowledge.

## What changed

- Preserved the original primary result and disclosed both negative parameter worlds.
- Added conditional-mean derivatives, local stability, controlled feedback-influence derivatives and a monitoring-gap identity.
- Executed 4,500 exploratory trajectories of 1,000 updates each, testing initialization, a locally matched participation law, two specified propensity errors, and model-based invitation counts.
- Distinguished direct influence from outcome loss and narrowed all developmental or general AI claims.
- Added closer methodological literature and verified the two relevant vascular-background references.

The new study was planned after the original results were inspected. Its pre-execution local protocol is not external preregistration or independent confirmation on real populations. All configured cells and contrary findings are included.

## Reproduce

From the repository root, in an isolated Python environment:

```sh
python -m pip install -r v2/requirements.txt
python v2/extension/run_extension.py --output results_reproduced
python v2/extension/verify_extension.py
python v2/theory_verify.py
python v2/theory_extension_crosscheck.py
python v2/build_revision_figures.py
```

The runner's output argument is resolved relative to the current working directory. Use a new directory; completed outputs are not overwritten. The independent verifiers inspect the published results. Simulation execution used Python 3.12.14 and NumPy 2.3.5. The recorded plotting run used NumPy 2.5.3 and Matplotlib 3.11.2; numeric conclusions agree, but font and library versions can change image bytes. The original published root `results/` remains intact; `study/results/` is a byte-identical compatibility copy preserving the new experiment's frozen relative input paths.

Original and extension hashes, complete run tables, world summaries, numerical plotting inputs, vector figures and independent calculation checks are supplied. The full new extension was also reproduced from this staged repository before publication and its numeric CSV outputs compared byte-for-byte. Time and execution metadata naturally differ.

## Version and authorship record

The historical v0.1.0 working paper retains its original seven-author byline and title. This v0.2.3 revised manuscript uses the subsequently supplied three-author byline: Lingsen You, Li Shen and Junbo Ge; the latter two are corresponding authors. Earlier release files have not been overwritten. These are versioned working-paper records, not a statement of journal acceptance or a verified priority claim.

No additional reuse license is granted in this GitHub release. AI assistance is disclosed in the manuscript. Internal multi-agent review is not external peer review.
