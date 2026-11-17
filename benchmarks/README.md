# Benchmarks

## Token efficiency

`results/token-efficiency.md` is the report produced by TOON's own token benchmark, with Jot added. It needs no API keys, and anyone can reproduce it.

### How it was produced
- **Datasets:** the 8 datasets in TOON's `benchmarks/src/datasets.ts`, generated from a fixed random seed.
- **Encoders:** TOON's own encoder for TOON, and `jot.py` (`jot from-json`) for Jot.
- **Tokenizer:** `o200k_base` (GPT-4o), as used by TOON's benchmark.
- **TOON repository:** commit `22caca377f08d737789a2ca60ab02c425a3aa947`.

### Reading the report
The report is written from TOON's side: `vs Jot (+53.5%)` means TOON uses 53.5% *more* tokens than Jot. The main README turns these into savings for Jot.

### Reproduce it

Requirements: git, Node.js 22.18 or newer, pnpm and Python 3.9 or newer.

```
git clone https://github.com/toon-format/toon.git
cd toon
git checkout 22caca377f08d737789a2ca60ab02c425a3aa947
git apply ../toon-benchmark.patch
pnpm install
cd benchmarks
pnpm benchmark:tokens
```

On Windows, set `$env:PYTHONUTF8="1"` first. If Python isn't on your PATH as `python3` (or `python` on Windows), set `PYTHON` to its full path.

### What the patch does
- Adds `benchmarks/jot/jot.py`, a copy of this release.
- Registers three formats in `src/formats.ts`: `jot` (compact), `jot-balanced` and `jot-readable`.
- Adds Jot to the token report's comparison list.
- Adds `scripts/jot-check.ts`, a free self-check. For every dataset it confirms that the Jot output converts back to identical JSON, and that Jot's parser catches each kind of corrupted table (missing rows, extra rows, a dropped cell).
- Extends the structural-corruption code and adds a `BENCH_FORMATS` filter to the accuracy script, so Jot can also be included in TOON's LLM accuracy benchmark. That benchmark needs API keys, and its results aren't published with this release.

TOON's benchmark code is MIT-licensed (Copyright (c) 2025-present Johann Schopplich). The patch modifies that code, and the same license applies to those changes.
