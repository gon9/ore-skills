---
name: test-value-review
description: Review or simplify a repository's tests by checking observable behavior, invariants, and execution evidence. Use when asked to reduce low-value tests or apply an invariant-first testing approach; not for routine feature work.
---

# Test value review

Use the repository's requirements, current behavior, and risk boundaries to decide what each test proves. Treat the existing test suite as evidence to inspect, not as a deletion target.

For each candidate test, ask:

1. What user-visible result, durable state, or security/architecture invariant would fail if the code regressed?
2. Would the test fail for that regression and keep passing after a behavior-preserving refactor?
3. Is the same claim already covered by a stronger check through the real entry point?

Keep or improve tests that demonstrate behavior, failure handling, state changes, integration boundaries, or security properties. Prefer types, schemas, linters, and repository validators for constraints they can prove deterministically. Use a real CLI, dry run, doctor command, or other execution path for behavior those checks cannot prove. External services may be replaced at their boundary while the internal path stays real.

Flag tests that only assert internal calls, mock arrangements, copied implementation logic, or literal script/prompt text. Before removing one, identify its unique regression claim and a replacement check, or explicitly report the lost coverage. Do not use test count or line count as a quality metric. Do not delete tests in bulk solely because they use mocks or seem redundant.

For a change, report: the behavior or invariant, the chosen check, what was run, the observed result, and any coverage removed or still unverified. Keep production and device acceptance distinct from local automated evidence. Follow the target repository's own safety, ownership, and deployment rules.
