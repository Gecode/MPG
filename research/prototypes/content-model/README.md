# Format-neutral MPG content-model prototype

This isolated prototype makes the model proposed in
`research/current-pipeline-audit.md` concrete without choosing MDX, MyST,
AsciiDoc, or another authoring syntax.

## Files

- `content-model.schema.json` is a JSON Schema 2020-12 structural contract for
  `Publication`, `Page`, `CodeArtifact`, `CodeRegion`/`CodeProjection`,
  `ValidationProfile`, and `FigureAsset`.
- `sample-publication.json` maps the current `less` propagator from
  `docs/src/chapters/programming/p-started.tex.in`, its `test/less.cpp` wrapper,
  its named literate regions, and two page projections.
- `validate.py` is a Python-standard-library semantic checker. JSON Schema can
  describe shapes but cannot conveniently enforce cross-document references,
  parent-graph acyclicity, or honest run-mode claims.
- `tests/test_validate.py` exercises those invariants.

The sample intentionally improves one known defect in the current pipeline.
It declares `less` as `test-harness` with `-test ^Less` and requires at least
one registered test. The production pipeline currently passes `-help`, which
exits before executing tests; the checker rejects that as a dishonest
`test-harness` profile. Compile-only and interactive profiles remain valid
first-class modes, but cannot claim runtime expectations they did not execute.

## Commands

Run from this directory:

```sh
python3 validate.py sample-publication.json --check-paths
python3 -m unittest discover -s tests -p 'test_*.py'
```

Expected result:

```text
OK: 1 page(s), 1 artifact(s), 1 validation profile(s), 0 figure asset(s).
........
----------------------------------------------------------------------
Ran 8 tests in ...

OK
```

The checker validates:

- globally unique, syntactically stable entity/projection IDs;
- artifact-local unique region IDs, exactly one root, valid parents, and no
  parent cycles;
- navigation, projection, figure, artifact, region, and validation-profile
  references;
- reciprocal artifact/profile ownership;
- valid source spans and optionally existing repository paths;
- runtime declarations for `run`, `test-harness`, and `expected-failure`;
- no runtime claim on `compile-only`;
- non-automated declaration for `interactive`; and
- actual test selection plus a registered-test-count assertion for
  `test-harness` (help-only invocation is rejected).

This checker is deliberately small rather than a general JSON Schema engine.
Consumers should validate structure with any Draft 2020-12 implementation and
then run this semantic checker. The standard-library checker performs the
cross-reference and honesty rules even when a schema package is unavailable.
