# JSON Input Schema

Required fields:

- `id`: string
- `original_code`: string
- `repaired_code`: string

Optional fields:

- `prompt`: string
- `static_findings`: object
- `validation`: object
- `apparent_cues`: object
- `metadata`: object

## `static_findings`

```json
{
  "before_count": 2,
  "after_count": 0,
  "before_types": ["SQL_INJECTION"],
  "after_types": []
}
```

## `validation`

```json
{
  "original_vulnerability_closed": false,
  "exploit_path_reachable_after": true,
  "functionality_preserved": true,
  "new_vulnerability_introduced": false,
  "related_new_vulnerability": false,
  "input_scope_narrowed": false,
  "notes": "Dynamic oracle still triggers the original exploit."
}
```

## `apparent_cues`

```json
{
  "warning_disappeared": true,
  "defensive_syntax_added": true,
  "explicit_security_claim": true,
  "narrower_input_handling": false,
  "user_facing_assurance": false,
  "other": ["assistant says the vulnerability is fixed"]
}
```
