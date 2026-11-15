# Contributing

Small, reproducible contributions are especially useful:

- A scene where the current skill misses an important look, action, reaction or attention change.
- An original example with a clearly readable setup and consequence.
- A translation that preserves evidence boundaries and user scope.
- A backend adapter for a concrete operation, with tested inputs and outputs.

For a behavior report, include the request, relevant input, actual assistant output, host/model/version when available, what was accessible, and why the decision is wrong or uncertain. A synthetic text case is welcome; label it as such. Distinguish your interpretation from what the input actually shows.

Share only material you can distribute. Use a small original substitute when the source is private or belongs to another creator. Avoid credentials, local machine paths, household photos and task receipts containing private data.

Instruction changes should fix a demonstrated problem. Avoid adding universal frame counts, mandatory micro-expressions, model-specific syntax, or unsupported success claims to the general skill.

Run the package checks before a pull request:

```bash
python scripts/check_package.py
python -m unittest discover -s tests
```

For substantive behavior changes, run a fresh evaluation on the affected cases without showing the evaluator the oracle. Record actual outcomes rather than editing the oracle to fit the response. For media claims, provide moving evidence and clear candidate/interval references.

Contributions to the repository are provided under its [MIT license](LICENSE); third-party materials retain their own terms and need explicit attribution and compatible distribution scope. Linking a useful source is preferable to copying a whole collection.
