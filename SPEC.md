# Jot specification

Version 0.1 (matches `jot-format` 0.1.0). This document defines the syntax and meaning of Jot text. The reference implementation is `jot.py`.

## Contents
- Files, comments, keys, separators
- Values (all types)
- Unquoted text
- Tables (list, keyed, field groups, row counts)
- References
- Limits
- Mapping to JSON
- Errors
- Grammar


## Files
UTF-8 only. A leading BOM is ignored and CRLF is treated as LF. An empty file means `{}`. A file holds either one value, or `key: value` entries with no surrounding braces.

## Comments
`# line`, `// line` and `/* block */`. After unquoted text, a comment must be preceded by a space: `a: C#` is the text `C#`, while `a: x #note` is `x` followed by a comment.

## Keys
A key is either bare (`[A-Za-z_][A-Za-z0-9_.-]*`) or `"quoted"`. Dots are just characters: `editor.fontSize` is one flat key. Duplicate keys are an error.

## Separators
Entries and items are separated by a comma, a newline, or both. Trailing commas are fine. These are errors:
- a doubled comma
- a leading comma
- two values on one line without a comma, like `[1 2]`

## Values

| Kind | Examples | Notes |
|---|---|---|
| unquoted text | `admin`, `Priya Reddy`, `C:\x`, `https://a.b/c` | See the rules below |
| string | `"text\n"` | JSON escapes |
| multiline | `"""` … `"""` | Leading newline and a closing line of only whitespace are dropped; common indent removed. `\` at the end of a line joins it to the next |
| raw | `r"C:\x"`, `r"""…"""` | No escapes |
| f-string | `f"${base}/users"` | `${name}` inserts a reference, `${env:NAME}` an environment variable (opt-in), `\$` a literal `$` |
| integer | `42`, `-7`, `1_000`, `0xFF`, `0o755`, `0b101` | Arbitrary precision. No leading zeros |
| float | `1.5`, `2e-3`, `1.0` | No NaN or infinity |
| date / datetime | `2026-11-17`, `2026-11-17T09:30:15.5+05:30` | `T` is required between date and time |
| duration | `30s`, `1h30m`, `500ms`, `1.5s`, `2d`, `250us` | Units are `d h m s ms us`, largest first, each used once |
| size | `10MB`, `512KiB`, `1.5GB` | `KB`/`MB` = 1000ⁿ, `KiB`/`MiB` = 1024ⁿ; case-sensitive; must come out to whole bytes |
| bool / null | `true`, `false`, `null` | |
| object | `{ a: 1, b: 2 }` | |
| array | `[1, 2, 3]` | |
| table | `[:id,name` + rows + `]`, `{:a,b` + `key: row` lines + `}` | See below |
| reference | `*name` | Deep copy of a referenced value |

## Unquoted text
Text may be written without quotes when **all** of these hold:
- It doesn't start with a digit or any of `+ - . " ' { } [ ] , : # * & ;`.
- It doesn't contain `, { } [ ] " ;`, a newline, or `: ` (colon followed by a space).
- It isn't `true`, `false` or `null`, and doesn't start with one of them followed by a space.

The text runs to the end of the line, a separator, or a comment; trailing spaces are dropped.

These are **errors** rather than text, because they're probably mistakes:
- `yes`, `no`, `on`, `off` → use `true` or `false`, or quote them
- `True`, `None`, `NaN` → use the lowercase keyword, or quote them
- a number followed by text, like `12 MG Road` → quote it

So `version: 1.4.2` and `ip: 10.0.0.1` need quotes. Jot never guesses a type.

## Tables
A table is a list of objects written as a header plus rows. `[:` starts one; the header names the fields, and each row gives the cells in header order:

```
users: [:id,name,role
  1,Asha,admin
  2,"Rao, R.",viewer      # quote cells that contain commas
  3,Ravi,                 # empty cell = field is absent (not null)
]
```

**Keyed tables.** `{:` makes an object whose values are rows. Each row starts with its key:

```
flags: {:enabled,rollout,owner
  dark_mode: true,80,Asha
  new_checkout: false,0,
}
```

**Field groups.** `name{a,b}` in the header turns several columns into a nested object. Groups can nest. If all of a group's cells are empty, that object is absent:

```
contacts: [:name,address{city,geo{lat,lng}},plan{name,price}
  Asha,Hyderabad,17.4,78.5,pro,40
  Ravi,,,,free,0              # no address
]
```

**Declared row counts.** `[20:id,name` and `{40:enabled,rollout` state how many rows follow. The parser checks the count, so a file that was cut off or had rows pasted in fails with a clear error instead of silently loading partial data. A reader (or an LLM) can also see the size at a glance. `jot.dumps` writes counts on multi-line tables by default; `counts=False` turns them off, and `counts="all"` adds them to one-line tables too.

**General rules**
- A cell can hold any value, including a one-line table: `1,[:sku,qty;A,2;B,1]`.
- Rows end at a newline or `;`, so `[:a,b;1,2;3,4]` is a one-line table.
- Every row has exactly one cell per column.

## References
- `&name: value` defines a reference. It can appear in any object.
- `*name` is a deep copy of the value.
- `...*name` spreads an object into an object, or an array into an array. Later entries win, so `{ ...*defaults, timeout: 60s }` overrides one field.
- All references share one namespace and must be defined before use. A name can't be defined twice.
- References don't appear in the output.
- Objects and arrays can't be interpolated into f-strings.

## Limits (security)
- Nesting deeper than 200 levels is an error.
- References may expand to at most 1,000,000 units (one per value plus one per character). This stops "billion laughs" style files that are tiny on disk but explode in memory.
- Both limits are configurable: `jot.loads(text, max_depth=..., max_expansion=...)`.
- Environment variables are only read with `env=True` (`--env` on the CLI).

## Mapping to JSON
- Dates and datetimes become ISO-8601 strings: `Z` for UTC, and milliseconds when the fraction is whole milliseconds.
- Durations become seconds (`1m30s` → `90`, `250ms` → `0.25`).
- Sizes become bytes.
- References are resolved.

## Errors
Every error reports line and column, shows the source line with a caret, and gives a hint where one helps.

## Grammar

This is informal PEG. `/` is ordered choice. `_` is spaces, tabs and comments; `NL` is a newline.

```
document   <- ws (members / value)? ws EOF
members    <- entry (sep entry)* sep?
entry      <- key ws ':' ws value  /  '&' ident ws ':' ws value  /  '...*' ident
object     <- '{' ws (members ws)? '}'
array      <- '[' ws (item (sep item)* sep?)? ws ']'
item       <- value / '...*' ident
table      <- '[' count? ':' header (rowend ws row)* ws rowend? ws ']'
keyedtable <- '{' count? ':' header (rowend ws key _ ':' row)* ws rowend? ws '}'
count      <- [0-9]+                            # must equal the number of rows
header     <- _ field (_ ',' _ field)* _
field      <- key (_ '{' _ field (_ ',' _ field)* _ '}')?
row        <- _ cell? (_ ',' _ cell?)*          # exactly one cell per leaf field
rowend     <- NL / ';'
sep        <- (ws ',' ws) / (_ NL ws)
value      <- keyedtable / object / table / array / string / ref / number_like / bare
ref        <- '*' ident
key        <- ident / dqstring
ident      <- [A-Za-z_] [A-Za-z0-9_.-]*
string     <- ('r' / 'f')? ('"""' block '"""' / dqstring)
number_like<- datetime / size / duration / hex / oct / bin / decimal   # then must end the value
bare       <- !start_bad (!stop char)+          # see "Unquoted text"
```
