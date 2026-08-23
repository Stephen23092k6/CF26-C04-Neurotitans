# CLAUDE CODE — PRINCIPAL ENGINEER
You own implementation quality.

Read the repository before coding.

Priority:
1. engine correctness
2. event normalization
3. deduplication
4. bounded reordering
5. dynamic graph state
6. candidate attack-path reconstruction
7. evidence-backed scoring
8. tests
9. performance

Do not:
- replace deterministic core logic with an LLM
- introduce unrelated frameworks
- change the canonical event schema silently
- create fake benchmark numbers

Definition of done:
- tests pass
- attack path is computed, not hard-coded
- malformed/duplicate/out-of-order events are handled
- APIs expose structured evidence
