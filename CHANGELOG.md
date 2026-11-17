# Changelog

## 0.1.0 (first public release)

- JSON-compatible syntax: every valid JSON document is valid Jot.
- Comments, bare keys, unquoted text, optional and trailing commas.
- Multiline, raw and f-strings; dates, datetimes, durations and sizes.
- References (`&name`, `*name`, `...*name`) with limits on nesting depth and expansion.
- Tables, keyed tables, field groups and declared row counts.
- Readable, compact and balanced output modes; JSON → Jot → JSON gives identical JSON.
- Command line: `check`, `to-json`, `from-json`, `tokens`.
