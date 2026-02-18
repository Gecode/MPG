---
name: gecode-modeling
description: "Model CP problems in Gecode with Int/Bool/Set/Float variables, constraints, MiniModel expressions, branchings, and search configuration. Use when building or refining Gecode models and solver setup."
---

# Gecode Modeling

## Core
- Define model as `Space` subclass.
- Create typed variable arrays with tight domains early.
- Post constraints via post functions (`rel`, `linear`, `distinct`, set/float variants).
- Post branching via `branch(...)`; variable strategy + value strategy define tree shape.
- Use search engines (`DFS`, `BAB`, restart/portfolio variants) per objective.
- MiniModel adds expression syntax via `expr(...)`, `rel(...)`, matrix/channel helpers.

## Key Patterns
- Prefer global constraints over manual decompositions when available.
- Keep branchings explicit and problem-specific for scale.
- Use multiple branchers intentionally; creation order matters.
- Tune search options: recomputation distance, restarts, no-goods, stop objects.
- Use tracing/Gist/CPProfiler for model diagnostics.
- Add implied constraints aggressively when semantics unchanged but propagation improves.
- Break symmetry structurally: order constraints, fixed anchors, `precede`, monotone bins.
- Match propagation level to complexity (`IPL_DOM` only where payoff > cost).
- Replace weak decompositions with stronger globals (`count` GCC, `binpacking`, `circuit`, `extensional`).
- Cache reusable heavy artifacts (tuple sets, shared arrays) keyed by shape/parameters.
- For optimization models, branch on cost-driving vars first, tie with objective structure.

## Pitfalls
- Weak domains at model start causing huge trees.
- Forgetting to update all variable members in cloning constructor.
- Assuming MiniModel nonlinear expressions stay monolithic; many decompose.
- Treating Boolean vars as subclass of integer vars.
- Ignoring exceptions from invalid arguments/overflow.
- Using domain propagation for `linear` indiscriminately (can be exponential).
- Recomputing identical tuple sets/shared maps per post.
- Leaving major value/variable symmetries unbroken.

## Source Focus
- `/Users/zayenz/gecode/MPG/docs/src/chapters/modeling/m-started.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/modeling/m-integer.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/modeling/m-set.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/modeling/m-float.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/modeling/m-minimodel.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/modeling/m-branch.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/modeling/m-search.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/case-studies/c-photo.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/case-studies/c-golomb.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/case-studies/c-golf.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/case-studies/c-magic-sequence.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/case-studies/c-nonogram.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/case-studies/c-kakuro.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/case-studies/c-warehouses.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/case-studies/c-bin-packing.tex.in`
- `/Users/zayenz/gecode/MPG/docs/src/chapters/case-studies/c-crossword.tex.in`
