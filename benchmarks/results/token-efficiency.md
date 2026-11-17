#### Mixed-Structure Track

Datasets with nested or semi-uniform structures. CSV excluded as it cannot properly represent these structures.

```
🛒 E-commerce orders with nested structures  ┊  Tabular: 33%
   │
   TOON                █████████████░░░░░░░    73,550 tokens
   ├─ vs Jot           (+49.9%)                49,055 tokens
   ├─ vs Jot balanced  (+0.1%)                 73,452 tokens
   ├─ vs Jot readable  (−6.4%)                 78,551 tokens
   ├─ vs JSON          (−33.4%)               110,425 tokens
   ├─ vs JSON compact  (+5.1%)                 69,990 tokens
   ├─ vs YAML          (−14.6%)                86,105 tokens
   └─ vs XML           (−40.8%)               124,317 tokens

🧾 Semi-uniform event logs  ┊  Tabular: 50%
   │
   TOON                █████████████████░░░   154,090 tokens
   ├─ vs Jot           (+74.9%)                88,098 tokens
   ├─ vs Jot balanced  (+74.9%)                88,098 tokens
   ├─ vs Jot readable  (+67.3%)                92,097 tokens
   ├─ vs JSON          (−15.0%)               181,215 tokens
   ├─ vs JSON compact  (+19.9%)               128,530 tokens
   ├─ vs YAML          (−0.8%)                155,404 tokens
   └─ vs XML           (−25.2%)               205,876 tokens

🧩 Deeply nested configuration  ┊  Tabular: 0%
   │
   TOON                █████████████░░░░░░░       584 tokens
   ├─ vs Jot           (+19.7%)                   488 tokens
   ├─ vs Jot balanced  (+2.5%)                    570 tokens
   ├─ vs Jot readable  (−9.9%)                    648 tokens
   ├─ vs JSON          (−35.5%)                   905 tokens
   ├─ vs JSON compact  (+6.0%)                    551 tokens
   ├─ vs YAML          (−11.0%)                   656 tokens
   └─ vs XML           (−41.3%)                   995 tokens

📊 Feature flags keyed by name  ┊  Tabular: 100%
   │
   TOON                █████████░░░░░░░░░░░    10,549 tokens
   ├─ vs Jot           (+10.6%)                 9,542 tokens
   ├─ vs Jot balanced  (+10.6%)                 9,542 tokens
   ├─ vs Jot readable  (+0.1%)                 10,543 tokens
   ├─ vs JSON          (−54.5%)                23,193 tokens
   ├─ vs JSON compact  (−32.8%)                15,687 tokens
   ├─ vs YAML          (−41.3%)                17,985 tokens
   └─ vs XML           (−63.3%)                28,709 tokens

📊 Contacts with nested address and plan groups  ┊  Tabular: 100%
   │
   TOON                ███████░░░░░░░░░░░░░    26,991 tokens
   ├─ vs Jot           (+3.8%)                 25,991 tokens
   ├─ vs Jot balanced  (+3.8%)                 25,991 tokens
   ├─ vs Jot readable  (−0.0%)                 26,992 tokens
   ├─ vs JSON          (−66.3%)                80,006 tokens
   ├─ vs JSON compact  (−42.6%)                47,018 tokens
   ├─ vs YAML          (−51.6%)                55,748 tokens
   └─ vs XML           (−70.2%)                90,539 tokens

──────────────────────────────────── Total ────────────────────────────────────
   TOON                ████████████████████   265,764 tokens
   ├─ vs Jot           (+53.5%)               173,174 tokens
   ├─ vs Jot balanced  (+34.5%)               197,653 tokens
   ├─ vs Jot readable  (+27.3%)               208,831 tokens
   ├─ vs JSON          (−32.8%)               395,744 tokens
   ├─ vs JSON compact  (+1.5%)                261,776 tokens
   ├─ vs YAML          (−15.9%)               315,898 tokens
   └─ vs XML           (−41.0%)               450,436 tokens
```

#### Flat-Only Track

Datasets with flat, fully tabular-eligible data where CSV is applicable.

```
👥 Uniform employee records  ┊  Tabular: 100%
   │
   CSV                 ███████████████████░    47,402 tokens
   TOON                ████████████████████    50,225 tokens   (+6.0% vs CSV)
   ├─ vs Jot           (+8.7%)                 46,225 tokens
   ├─ vs Jot balanced  (+8.7%)                 46,225 tokens
   ├─ vs Jot readable  (−0.0%)                 50,226 tokens
   ├─ vs JSON          (−60.6%)               127,353 tokens
   ├─ vs JSON compact  (−36.7%)                79,349 tokens
   ├─ vs YAML          (−50.0%)               100,449 tokens
   └─ vs XML           (−65.8%)               146,887 tokens

📈 Time-series analytics data  ┊  Tabular: 100%
   │
   CSV                 ██████████████████░░     8,385 tokens
   TOON                ████████████████████     9,117 tokens   (+8.7% vs CSV)
   ├─ vs Jot           (+8.7%)                  8,388 tokens
   ├─ vs Jot balanced  (+8.7%)                  8,388 tokens
   ├─ vs Jot readable  (−0.0%)                  9,119 tokens
   ├─ vs JSON          (−59.0%)                22,247 tokens
   ├─ vs JSON compact  (−35.9%)                14,213 tokens
   ├─ vs YAML          (−49.0%)                17,860 tokens
   └─ vs XML           (−65.7%)                26,618 tokens

⭐ Top 100 GitHub repositories  ┊  Tabular: 100%
   │
   CSV                 ███████████████████░     8,711 tokens
   TOON                ████████████████████     8,937 tokens   (+2.6% vs CSV)
   ├─ vs Jot           (+2.5%)                  8,716 tokens
   ├─ vs Jot balanced  (+2.5%)                  8,716 tokens
   ├─ vs Jot readable  (+0.2%)                  8,917 tokens
   ├─ vs JSON          (−41.7%)                15,337 tokens
   ├─ vs JSON compact  (−23.2%)                11,640 tokens
   ├─ vs YAML          (−33.0%)                13,337 tokens
   └─ vs XML           (−48.3%)                17,294 tokens

──────────────────────────────────── Total ────────────────────────────────────
   CSV                 ███████████████████░    64,498 tokens
   TOON                ████████████████████    68,279 tokens   (+5.9% vs CSV)
   ├─ vs Jot           (+7.8%)                 63,329 tokens
   ├─ vs Jot balanced  (+7.8%)                 63,329 tokens
   ├─ vs Jot readable  (+0.0%)                 68,262 tokens
   ├─ vs JSON          (−58.6%)               164,937 tokens
   ├─ vs JSON compact  (−35.1%)               105,202 tokens
   ├─ vs YAML          (−48.1%)               131,646 tokens
   └─ vs XML           (−64.2%)               190,799 tokens
```

Token counts use `gpt-tokenizer` with `o200k_base` encoding (GPT-5 tokenizer). Other providers tokenize differently, so absolute counts are tokenizer-specific; relative differences between formats hold directionally.

<details>
<summary><strong>Show detailed examples</strong></summary>

#### 📈 Time-series analytics data

**Savings:** 13,130 tokens (59.0% reduction vs JSON)

**JSON** (22,247 tokens):

```json
{
  "metrics": [
    {
      "date": "2025-01-01",
      "views": 6867,
      "clicks": 435,
      "conversions": 54,
      "revenue": 3959.77,
      "bounceRate": 0.67
    },
    {
      "date": "2025-01-02",
      "views": 7554,
      "clicks": 246,
      "conversions": 17,
      "revenue": 3034.85,
      "bounceRate": 0.32
    },
    {
      "date": "2025-01-03",
      "views": 5032,
      "clicks": 142,
      "conversions": 21,
      "revenue": 4536.93,
      "bounceRate": 0.48
    },
    {
      "date": "2025-01-04",
      "views": 5750,
      "clicks": 241,
      "conversions": 16,
      "revenue": 3630,
      "bounceRate": 0.46
    },
    {
      "date": "2025-01-05",
      "views": 4195,
      "clicks": 131,
      "conversions": 12,
      "revenue": 1970.95,
      "bounceRate": 0.53
    }
  ]
}
```

**TOON** (9,117 tokens):

```
metrics[5]{date,views,clicks,conversions,revenue,bounceRate}:
  2025-01-01,6867,435,54,3959.77,0.67
  2025-01-02,7554,246,17,3034.85,0.32
  2025-01-03,5032,142,21,4536.93,0.48
  2025-01-04,5750,241,16,3630,0.46
  2025-01-05,4195,131,12,1970.95,0.53
```

---

#### ⭐ Top 100 GitHub repositories

**Savings:** 6,400 tokens (41.7% reduction vs JSON)

**JSON** (15,337 tokens):

```json
{
  "repositories": [
    {
      "id": 132750724,
      "name": "build-your-own-x",
      "repo": "codecrafters-io/build-your-own-x",
      "description": "Master programming by recreating your favorite technologies from scratch.",
      "createdAt": "2018-05-09T12:03:18Z",
      "updatedAt": "2026-07-23T18:57:15Z",
      "pushedAt": "2026-07-14T19:25:58Z",
      "stars": 530712,
      "watchers": 6778,
      "forks": 50205,
      "defaultBranch": "master"
    },
    {
      "id": 21737465,
      "name": "awesome",
      "repo": "sindresorhus/awesome",
      "description": "😎 Awesome lists about all kinds of interesting topics",
      "createdAt": "2014-07-11T13:42:37Z",
      "updatedAt": "2026-07-23T18:57:24Z",
      "pushedAt": "2026-06-30T18:21:16Z",
      "stars": 488074,
      "watchers": 8292,
      "forks": 36010,
      "defaultBranch": "main"
    },
    {
      "id": 28457823,
      "name": "freeCodeCamp",
      "repo": "freeCodeCamp/freeCodeCamp",
      "description": "freeCodeCamp.org's open-source codebase and curriculum. Learn math, programming,…",
      "createdAt": "2014-12-24T17:49:19Z",
      "updatedAt": "2026-07-22T07:01:33Z",
      "pushedAt": "2026-07-21T18:00:51Z",
      "stars": 452380,
      "watchers": 8590,
      "forks": 45624,
      "defaultBranch": "main"
    }
  ]
}
```

**TOON** (8,937 tokens):

```
repositories[3]{id,name,repo,description,createdAt,updatedAt,pushedAt,stars,watchers,forks,defaultBranch}:
  132750724,build-your-own-x,codecrafters-io/build-your-own-x,Master programming by recreating your favorite technologies from scratch.,"2018-05-09T12:03:18Z","2026-07-23T18:57:15Z","2026-07-14T19:25:58Z",530712,6778,50205,master
  21737465,awesome,sindresorhus/awesome,😎 Awesome lists about all kinds of interesting topics,"2014-07-11T13:42:37Z","2026-07-23T18:57:24Z","2026-06-30T18:21:16Z",488074,8292,36010,main
  28457823,freeCodeCamp,freeCodeCamp/freeCodeCamp,"freeCodeCamp.org's open-source codebase and curriculum. Learn math, programming,…","2014-12-24T17:49:19Z","2026-07-22T07:01:33Z","2026-07-21T18:00:51Z",452380,8590,45624,main
```

</details>
