# MPG Case-Study Skill Audit

Scope: `/Users/zayenz/gecode/MPG/docs/src/chapters/case-studies/*.tex.in`

## Per-Case Findings

| Case study | Important issues / patterns | Category | Skill mapping | Coverage before | Action |
|---|---|---|---|---|---|
| `c-photo.tex.in` | Objective via `cost()`, propagation-level alignment (`distinct` BND), reversal symmetry break | Optimization + symmetry | `gecode-modeling` | Partial | Added symmetry + propagation-level guidance |
| `c-golomb.tex.in` | Tight bounds to avoid overflow risk, implied constraints, symmetry break, cost-driven branching | Modeling strength | `gecode-modeling` | Partial | Added implied-constraint and symmetry bullets |
| `c-golf.tex.in` | Set-model symmetry reduction + extra symmetry breaking (`precede`, ordering) | Symmetry design | `gecode-modeling` | Weak | Added structural symmetry guidance |
| `c-magic-sequence.tex.in` | Individual `count` vs global counting, implied linear constraints, value-order heuristic | Global-vs-decomposition | `gecode-modeling` | Partial | Added global-constraint replacement rule |
| `c-nonogram.tex.in` | Regex/extensional modeling, AFC branching, propagation-only vs custom branching need | Search/branching fit | `gecode-modeling`, `gecode-brancher-implementation` | Partial | Added brancher heuristic emphasis |
| `c-knights.tex.in` | `circuit(..., IPL_DOM)`, symmetry via fixed move, custom Warnsdorff brancher | Problem-specific brancher | `gecode-brancher-implementation`, `gecode-modeling` | Partial | Added heuristic-brancher pattern |
| `c-kakuro.tex.in` | Naive `distinct+linear` decomposition weak, `IPL_DOM` linear cost tradeoff, extensional tuple-set surrogate, tuple-set cache opportunity | Propagation strength + modeling perf | `gecode-modeling`, `gecode-propagator-implementation` | Gap | Added decomposition-warning + cache guidance |
| `c-warehouses.tex.in` | `count` + `element` + `linear` composition, mixed int/bool cost expression, two-stage branching | Optimization modeling | `gecode-modeling` | Partial | Added cost-driven branching guidance |
| `c-bin-packing.tex.in` | Naive vs `binpacking` global, CDBF custom brancher, symmetry in branching, heap choice payload + `AP_DISPOSE`, region scratch, shared arrays | High-impact full-stack pattern | `gecode-modeling`, `gecode-brancher-implementation`, `gecode-memory-handling`, `gecode-general-knowledge` | Gap/partial | Added all four skills |
| `c-crossword.tex.in` | Memory reductions (variable elimination/shared arrays), branch print hooks, restart+no-goods+AFC robustness | Search robustness + memory | `gecode-modeling`, `gecode-memory-handling`, `gecode-general-knowledge` | Partial | Added memory + iterative tuning guidance |

## Priority Synthesis

### P0 (applied)
- Symmetry as mandatory design axis in modeling and branching.
- Global-constraint substitution for weak decompositions.
- Propagation-level cost awareness (`IPL_DOM` selectively).
- Problem-specific branchers for structure-heavy problems.

### P1 (applied)
- Memory patterns from case studies: shared arrays, region scratch, `AP_DISPOSE` lifecycle discipline.
- Iterative optimization loop: baseline -> propagation -> branching -> restart/no-good tuning.

### P2 (applied lightly)
- Propagator skill now explicitly calls out decomposition weakness and cacheable support data.

## Skill Updates Applied

- Updated `/Users/zayenz/gecode/MPG/skills/gecode-general-knowledge/SKILL.md`
- Updated `/Users/zayenz/gecode/MPG/skills/gecode-modeling/SKILL.md`
- Updated `/Users/zayenz/gecode/MPG/skills/gecode-propagator-implementation/SKILL.md`
- Updated `/Users/zayenz/gecode/MPG/skills/gecode-brancher-implementation/SKILL.md`
- Updated `/Users/zayenz/gecode/MPG/skills/gecode-memory-handling/SKILL.md`

No new skill created: existing five skills cover all extracted case-study learnings after update.
