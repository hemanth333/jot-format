# Jot

**JSON for everyday files and for LLM prompts.**

Jot is a text format with the same data model as JSON. Every valid JSON file is already valid Jot, so you can rename a `.json` file to `.jot` and start adding comments. On top of that, Jot is easier to write by hand and uses far fewer tokens when you send data to a language model.

```
# app settings
name: my-tool
released: 2026-11-17

&api: https://api.example.com
&defaults: { retries: 3, timeout: 30s }

endpoints: { users: f"${api}/users" }
http: { ...*defaults, timeout: 1m }

servers: [2:name,host,port
  alpha,"10.0.0.1",8080
  beta,"10.0.0.2",8080
]
```

## Features

**For people editing files**
- Comments: `#`, `//` and `/* */`
- No mandatory quotes on keys or plain text, no mandatory commas, trailing commas allowed
- Multiline strings with indentation stripped (`"""`), and raw strings for Windows paths and regexes (`r"C:\path"`)
- Dates (`2026-11-17`), durations (`1h30m`) and sizes (`10MB`) as real values
- References: define once with `&name`, reuse with `*name`, `...*name` or `f"${name}"`
- Strict where JSON is sloppy: duplicate keys are errors, and `yes`/`no`/`True` are rejected instead of guessed
- Errors give the line, column, a caret and a hint

**For LLM prompts**
- Tables: a list of similar objects is written as a header plus one row per item, so keys aren't repeated
- Keyed tables for maps of similar objects, and field groups (`address{city,country}`) for nested objects
- Declared row counts (`[20:...`) so truncated or padded data is caught
- A compact output mode tuned for tokenizers

## Install

```
pip install jot-format
```

Or copy `jot.py` into your project. It's a single file with no dependencies and needs Python 3.9 or newer.

## Use

### Command line

```
jot check config.jot                      # validate
jot to-json config.jot -o config.json     # for tools that need JSON
jot from-json data.json -o data.jot       # convert, readable
jot from-json data.json --compact         # fewest tokens, for prompts
jot from-json data.json --balanced        # compact, but one value per table cell
jot tokens data.json                      # compare JSON vs Jot size for your data
```

`jot tokens` shows exact token counts if `tiktoken` is installed (`pip install "jot-format[tokens]"`), and character counts otherwise.

### Python

```python
import jot

config = jot.load(open("config.jot", encoding="utf-8"))   # also reads plain JSON
text = jot.dumps(config)                                  # readable Jot
prompt_data = jot.dumps(records, compact=True)            # for an LLM prompt
json_text = jot.to_json(open("config.jot", encoding="utf-8").read())   # back to JSON
```

`load` and `loads` give dates, datetimes and durations back as `datetime` objects,
so a config that uses them isn't directly `json.dumps`-able. Use `jot.to_json` (or
the `to-json` command) when you want JSON out.

### Output modes

| Mode | Use it for | What it does |
|---|---|---|
| readable (default) | files people edit | normal indentation, simple table cells |
| `compact=True` | LLM prompts | one-space indent, small objects on one line, tables allowed inside table cells |
| `balanced=True` | LLM prompts with deeply nested data | compact, but every cell holds a single value and objects keep their own lines |

Converting from JSON and back always gives identical JSON.

## Token efficiency

Measured on the 8 datasets in [TOON](https://github.com/toon-format/toon)'s own token benchmark, which cover flat tables, nested orders, time series, event logs, deep config, keyed maps and nested groups. Each format was encoded by its own reference encoder, and tokens were counted with the `o200k_base` tokenizer (GPT-4o and GPT-5). No API calls are involved, and the numbers can be reproduced; see [`benchmarks/`](https://github.com/hemanth333/jot-format/tree/main/benchmarks).

| Dataset | JSON | JSON (minified) | TOON | Jot compact | Jot balanced |
|---|---|---|---|---|---|
| Uniform employee records | 127,353 | 79,349 | 50,225 | **46,225** | 46,225 |
| E-commerce orders (nested) | 110,425 | 69,990 | 73,550 | **49,055** | 73,452 |
| Time-series analytics | 22,247 | 14,213 | 9,117 | **8,388** | 8,388 |
| Top 100 GitHub repos | 15,337 | 11,640 | 8,937 | **8,716** | 8,716 |
| Semi-uniform event logs | 181,215 | 128,530 | 154,090 | **88,098** | 88,098 |
| Deeply nested config | 905 | 551 | 584 | **488** | 570 |
| Feature flags keyed by name | 23,193 | 15,687 | 10,549 | **9,542** | 9,542 |
| Contacts with nested groups | 80,006 | 47,018 | 26,991 | **25,991** | 25,991 |
| **Total** | **560,681** | **366,978** | **334,043** | **236,503** | **260,982** |

Compared with the other formats, compact Jot uses:

| Compared with | Compact Jot |
|---|---|
| JSON | 58% fewer tokens |
| Minified JSON | 36% fewer |
| TOON | 29% fewer |

It uses fewer tokens than TOON on every dataset. On the flat-table datasets it is level with CSV: 63,329 tokens against CSV’s 64,498 in total, and within a few tokens either way on each one.

**Where the savings come from:**
- tables with the keys written once
- optional nested objects kept inside tables as empty cells (the event logs)
- small tables inside table cells (the orders)
- no quotes on plain text
- tokenizer-aware indentation

**What these numbers don't show:**
- **How well models read the format.** Fewer tokens only helps if the model reads the data correctly, and this release doesn't publish accuracy results.
- **Other tokenizers.** Claude's tokenizer isn't public, and others will give somewhat different percentages.
- **Data with nothing to factor out.** For a small, deeply nested object, Jot is about the same size as minified JSON.

## Specification

The full format, including the grammar, is in [SPEC.md](https://github.com/hemanth333/jot-format/blob/main/SPEC.md).

## Status

This is the first public release (0.1.0). The format may still change before 1.0, based on feedback.

Not yet available:
- implementations in other languages
- editor syntax highlighting
- comment-preserving edits (`dumps` rewrites the whole file, so comments are lost)
- reporting more than one error per run

## Related formats

[JSON5](https://json5.org), [YAML](https://yaml.org), [TOML](https://toml.io) and [TOON](https://github.com/toon-format/toon). TOON pioneered tabular encodings of JSON for LLM input. Jot's keyed tables, field groups and row counts build on the same ideas, and its benchmark datasets are used here with thanks.

## Development

```
python -m unittest test_jot.py
```

## License

MIT. See [LICENSE](https://github.com/hemanth333/jot-format/blob/main/LICENSE).
