Important implementation rule:
For every small feature or module you add, also add focused unit tests.

Do not postpone tests until the end.
Implement in this order for each feature:

1. schema or utility
2. test for that unit
3. service/tool logic
4. test for that logic
5. API/component integration
6. test for behavior

Prefer many small tests over a few large tests.

Examples:

* if you add `pricing_tool.py`, also add `test_pricing_tool.py`
* if you add `SeverityFilter.tsx`, also add `SeverityFilter.test.tsx`
* if you add a parser utility, add parser tests immediately
