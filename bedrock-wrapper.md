Analyze this billing record using the provided deterministic findings.
Do not recompute the entire record unless needed to explain an inconsistency.
Return strict JSON only following the required schema.

record:
{{NORMALIZED_RECORD_JSON}}

deterministic_findings:
{{FINDINGS_JSON}}

computed_values:
{{COMPUTED_VALUES_JSON}}

missing_fields:
{{MISSING_FIELDS_JSON}}
