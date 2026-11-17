"""Tests for jot.py. Run with:  python -m unittest test_jot.py  (or pytest)."""

import contextlib
import datetime as dt
import io
import json
import os
import sys
import tempfile
import unittest

import jot


class JsonCompatibility(unittest.TestCase):
    """Every valid JSON document must parse to the same value."""

    DOCS = [
        '{}', '[]', '"hello"', '42', '-0', '3.14', '1e10', '-2.5E-3', 'true', 'false', 'null',
        '{"a": 1, "b": [1, 2, {"c": null}], "d": "x"}',
        '{"esc": "quote \\" slash \\\\ \\/ \\b\\f\\n\\r\\t \\u00e9 \\ud83d\\ude00"}',
        '[1, -1, 0.5, 100000000000000000000, "", " ", "${notref}"]',
        '{\n  "nested": {\n    "deep": {\n      "list": [true, false, null]\n    }\n  }\n}',
        '{"": "empty key", "with space": 1, "true": 2}',
        '{"a":1,"b":"x","c":[1,2],"d":{"e":null}}',
        '[{"id":1,"v":"a"},{"id":2,"v":"b"}]',
        '  [ ]  ',
    ]

    def test_json_docs(self):
        for doc in self.DOCS:
            with self.subTest(doc=doc):
                self.assertEqual(jot.loads(doc), json.loads(doc))


class Syntax(unittest.TestCase):
    def test_comments(self):
        text = """
        # hash comment
        a: 1   // slash comment
        /* block
           comment */ b: 2
        """
        self.assertEqual(jot.loads(text), {"a": 1, "b": 2})

    def test_bare_and_dotted_keys(self):
        self.assertEqual(jot.loads('name: "x"\nmy-key_2: true\neditor.fontSize: 14'),
                         {"name": "x", "my-key_2": True, "editor.fontSize": 14})

    def test_optional_and_trailing_commas(self):
        text = """
        list: [
          1
          2,
          3,
        ]
        obj: { a: 1, b: 2, }
        """
        self.assertEqual(jot.loads(text), {"list": [1, 2, 3], "obj": {"a": 1, "b": 2}})

    def test_empty_file_is_empty_object(self):
        self.assertEqual(jot.loads(""), {})
        self.assertEqual(jot.loads("# only a comment\n"), {})

    def test_bom_and_crlf(self):
        self.assertEqual(jot.loads('\ufeffa: 1\r\nb: "x"\r\n'), {"a": 1, "b": "x"})


class UnquotedText(unittest.TestCase):
    def test_basic(self):
        d = jot.loads("""
        mode: fast
        name: Priya Reddy
        email: priya@example.com
        url: https://example.com/a?b=c
        path: C:\\Users\\me\\logs
        home: ~/.cache/tool
        sku: SKU-100
        note: version 2 is out   # comment after text
        """)
        self.assertEqual(d["mode"], "fast")
        self.assertEqual(d["name"], "Priya Reddy")
        self.assertEqual(d["email"], "priya@example.com")
        self.assertEqual(d["url"], "https://example.com/a?b=c")
        self.assertEqual(d["path"], r"C:\Users\me\logs")
        self.assertEqual(d["home"], "~/.cache/tool")
        self.assertEqual(d["sku"], "SKU-100")
        self.assertEqual(d["note"], "version 2 is out")

    def test_in_arrays_and_inline_objects(self):
        self.assertEqual(jot.loads("a: [red, green, dark blue]\nb: {x: hi, y: there}"),
                         {"a": ["red", "green", "dark blue"], "b": {"x": "hi", "y": "there"}})

    def test_keywords_still_work(self):
        self.assertEqual(jot.loads("a: true\nb: null # c"), {"a": True, "b": None})


class Tables(unittest.TestCase):
    def test_basic_table(self):
        text = """
        users: [:id,name,role,active
          1,Asha Rao,admin,true
          2,Ravi,viewer,false
        ]
        """
        self.assertEqual(jot.loads(text)["users"], [
            {"id": 1, "name": "Asha Rao", "role": "admin", "active": True},
            {"id": 2, "name": "Ravi", "role": "viewer", "active": False},
        ])

    def test_empty_cells_mean_missing(self):
        text = "logs: [:ts,level,err\n 2026-11-17T10:00:00Z,INFO,\n 2026-11-17T10:00:01Z,ERROR,E101\n]"
        rows = jot.loads(text)["logs"]
        self.assertNotIn("err", rows[0])
        self.assertEqual(rows[1]["err"], "E101")

    def test_quoted_and_null_cells(self):
        rows = jot.loads('t: [:a,b\n "x, y",null\n "",1\n]')["t"]
        self.assertEqual(rows, [{"a": "x, y", "b": None}, {"a": "", "b": 1}])

    def test_one_line_table(self):
        self.assertEqual(jot.loads("t: [:a,b;1,2;3,4]"), {"t": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]})

    def test_comments_and_blank_lines(self):
        text = "t: [:a,b  # header\n\n 1,2  # first\n // between\n 3,4\n]"
        self.assertEqual(jot.loads(text)["t"], [{"a": 1, "b": 2}, {"a": 3, "b": 4}])

    def test_keyed_table(self):
        text = """
        flags: {:enabled,rollout,owner
          dark_mode: true,80,Asha
          "new checkout": false,0,
        }
        """
        self.assertEqual(jot.loads(text)["flags"], {
            "dark_mode": {"enabled": True, "rollout": 80, "owner": "Asha"},
            "new checkout": {"enabled": False, "rollout": 0},
        })
        self.assertEqual(jot.loads("f: {:a,b;x:1,2;y:3,4}"),
                         {"f": {"x": {"a": 1, "b": 2}, "y": {"a": 3, "b": 4}}})

    def test_field_groups(self):
        text = """
        contacts: [:name,address{city,geo{lat,lng}},plan{name,price}
          Asha,Hyderabad,17.4,78.5,pro,40
          Ravi,,,,free,0
          Meera,Pune,,,,
        ]
        """
        self.assertEqual(jot.loads(text)["contacts"], [
            {"name": "Asha", "address": {"city": "Hyderabad", "geo": {"lat": 17.4, "lng": 78.5}},
             "plan": {"name": "pro", "price": 40}},
            {"name": "Ravi", "plan": {"name": "free", "price": 0}},
            {"name": "Meera", "address": {"city": "Pune"}},
        ])

    def test_nested_values_in_cells(self):
        text = "orders: [:id,items,meta\n 1,[:sku,qty;A,2;B,1],{gift:true}\n 2,[],null\n]"
        self.assertEqual(jot.loads(text)["orders"], [
            {"id": 1, "items": [{"sku": "A", "qty": 2}, {"sku": "B", "qty": 1}], "meta": {"gift": True}},
            {"id": 2, "items": [], "meta": None},
        ])

    def test_declared_counts(self):
        self.assertEqual(len(jot.loads("t: [3:a\n 1\n 2\n 3\n]")["t"]), 3)
        self.assertEqual(len(jot.loads("t: {2:a;x:1;y:2}")["t"]), 2)
        for text, word in (("t: [3:a\n 1\n 2\n]", "missing"), ("t: [1:a\n 1\n 2\n]", "extra")):
            with self.assertRaises(jot.JotError) as cm:
                jot.loads(text)
            self.assertIn("declares", cm.exception.message)
            self.assertIn(word, cm.exception.hint)

    def test_writer_counts_option(self):
        rows = {"t": [{"a": 1}, {"a": 2}], "n": [{"x": [{"b": 1}, {"b": 2}]}, {"x": [{"b": 3}, {"b": 4}]}]}
        self.assertIn("[2:a", jot.dumps(rows))
        self.assertIn("[:a", jot.dumps(rows, counts=False))
        self.assertIn("[2:b;", jot.dumps(rows, compact=True, counts="all"))
        self.assertIn("[:b;", jot.dumps(rows, compact=True))

    def test_header_errors(self):
        with self.assertRaises(jot.JotError) as cm:
            jot.loads("t: [:a,b{}\n 1\n]")
        self.assertIn("at least one field", cm.exception.message)
        with self.assertRaises(jot.JotError) as cm:
            jot.loads("t: [:a,b{c,d\n 1,2,3\n]")
        self.assertIn("close the field group", cm.exception.message)
        with self.assertRaises(jot.JotError) as cm:
            jot.loads("t: {:a\n x: 1\n x: 2\n}")
        self.assertIn("duplicate key", cm.exception.message)

    def test_row_errors(self):
        with self.assertRaises(jot.JotError) as cm:
            jot.loads("t: [:a,b,c\n 1,2\n]")
        self.assertIn("2 value(s)", cm.exception.message)
        with self.assertRaises(jot.JotError) as cm:
            jot.loads("t: [:a,b\n 1,2,3\n]")
        self.assertIn("more values", cm.exception.message)


class Strings(unittest.TestCase):
    def test_multiline_dedent(self):
        text = '''
        note: """
          Hello,
            indented line
          bye
          """
        '''
        self.assertEqual(jot.loads(text)["note"], "Hello,\n  indented line\nbye")

    def test_line_continuation(self):
        text = 'a: """\n  one long \\\n    sentence\n  """'
        self.assertEqual(jot.loads(text)["a"], "one long sentence")

    def test_multiline_inline(self):
        self.assertEqual(jot.loads('a: """one line"""')["a"], "one line")

    def test_raw_string(self):
        self.assertEqual(jot.loads(r'p: r"C:\Users\me\new"')["p"], r"C:\Users\me\new")

    def test_raw_multiline(self):
        text = 'rx: r"""\n  ^\\d+\\.\\d+$\n  """'
        self.assertEqual(jot.loads(text)["rx"], r"^\d+\.\d+$")


class NumbersDatesUnits(unittest.TestCase):
    def test_numbers(self):
        d = jot.loads("a: 1_000_000\nb: 0xFF\nc: 0o755\nd: 0b1010\ne: 1.0\nf: -3\ng: +4")
        self.assertEqual(d, {"a": 1000000, "b": 255, "c": 493, "d": 10, "e": 1.0, "f": -3, "g": 4})
        self.assertIsInstance(d["e"], float)

    def test_big_int_keeps_precision(self):
        self.assertEqual(jot.loads("id: 9007199254740993")["id"], 9007199254740993)

    def test_dates(self):
        d = jot.loads("a: 2026-11-17\nb: 2026-11-17T09:30\nc: 2026-11-17T09:30:15.5Z\n"
                      "d: 2026-11-17T09:30:00+05:30")
        self.assertEqual(d["a"], dt.date(2026, 11, 17))
        self.assertEqual(d["b"], dt.datetime(2026, 11, 17, 9, 30))
        self.assertEqual(d["c"], dt.datetime(2026, 11, 17, 9, 30, 15, 500000, dt.timezone.utc))
        self.assertEqual(d["d"].utcoffset(), dt.timedelta(hours=5, minutes=30))

    def test_durations(self):
        d = jot.loads("a: 30s\nb: 1h30m\nc: 500ms\nd: 1.5s\ne: 2d\nf: -10m\ng: 250us")
        self.assertEqual(d["a"], dt.timedelta(seconds=30))
        self.assertEqual(d["b"], dt.timedelta(hours=1, minutes=30))
        self.assertEqual(d["c"], dt.timedelta(milliseconds=500))
        self.assertEqual(d["d"], dt.timedelta(seconds=1.5))
        self.assertEqual(d["e"], dt.timedelta(days=2))
        self.assertEqual(d["f"], dt.timedelta(minutes=-10))
        self.assertEqual(d["g"], dt.timedelta(microseconds=250))

    def test_sizes(self):
        d = jot.loads("a: 10MB\nb: 512KiB\nc: 1.5GB\nd: 0B\ne: 2TiB")
        self.assertEqual(d, {"a": 10_000_000, "b": 524_288, "c": 1_500_000_000, "d": 0,
                             "e": 2 * 2**40})

    def test_json_output_of_units_and_dates(self):
        out = json.loads(jot.to_json("due: 2026-12-01\nt: 1m30s\nfast: 250ms\ns: 1KB"))
        self.assertEqual(out, {"due": "2026-12-01", "t": 90, "fast": 0.25, "s": 1000})


class References(unittest.TestCase):
    def test_reference_value_and_fstring(self):
        text = """
        &base: "https://api.example.com"
        &port: 8080
        &defaults: { retries: 3 }
        users: f"${base}/users"
        addr: f"localhost:${port}"
        price: f"costs \\$5"
        a: *defaults
        b: *defaults
        """
        d = jot.loads(text)
        self.assertEqual(d["users"], "https://api.example.com/users")
        self.assertEqual(d["addr"], "localhost:8080")
        self.assertEqual(d["price"], "costs $5")
        self.assertNotIn("base", d)
        d["a"]["retries"] = 99
        self.assertEqual(d["b"]["retries"], 3)

    def test_spread_object(self):
        text = """
        &defaults: { retries: 3, timeout: 30s, region: ap-south-1 }
        prod: { ...*defaults, timeout: 60s }
        """
        self.assertEqual(jot.loads(text)["prod"],
                         {"retries": 3, "timeout": dt.timedelta(seconds=60), "region": "ap-south-1"})

    def test_spread_array(self):
        self.assertEqual(jot.loads("&base: [a, b]\nall: [...*base, c]")["all"], ["a", "b", "c"])

    def test_spread_type_errors(self):
        with self.assertRaises(jot.JotError):
            jot.loads("&x: [1]\no: { ...*x }")
        with self.assertRaises(jot.JotError):
            jot.loads("&x: {a: 1}\no: [...*x]")

    def test_env(self):
        os.environ["JOT_TEST_VAR"] = "s3cret"
        self.assertEqual(jot.loads('p: f"${env:JOT_TEST_VAR}"', env=True)["p"], "s3cret")
        with self.assertRaises(jot.JotError) as cm:
            jot.loads('p: f"${env:JOT_TEST_VAR}"')
        self.assertIn("turned off", cm.exception.message)

    def test_plain_strings_are_not_interpolated(self):
        self.assertEqual(jot.loads('&x: "1"\na: "${x}"')["a"], "${x}")


class Limits(unittest.TestCase):
    def test_deep_nesting_is_a_clean_error(self):
        with self.assertRaises(jot.JotError) as cm:
            jot.loads("[" * 5000 + "]" * 5000)
        self.assertIn("too deep", cm.exception.message)
        jot.loads("[" * 150 + "]" * 150)  # within the limit: fine

    def test_billion_laughs(self):
        lines = ["&a0: [x, x, x, x, x, x, x, x, x, x]"]
        for i in range(1, 10):
            lines.append(f"&a{i}: [" + ", ".join([f"*a{i-1}"] * 10) + "]")
        lines.append("boom: *a9")
        with self.assertRaises(jot.JotError) as cm:
            jot.loads("\n".join(lines))
        self.assertIn("too much data", cm.exception.message)

    def test_fstring_blowup(self):
        lines = ['&s0: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"']
        for i in range(1, 40):
            lines.append(f'&s{i}: f"${{s{i-1}}}${{s{i-1}}}"')
        with self.assertRaises(jot.JotError):
            jot.loads("\n".join(lines))


class Errors(unittest.TestCase):
    def err(self, text):
        with self.assertRaises(jot.JotError) as cm:
            jot.loads(text)
        return cm.exception

    def test_duplicate_key(self):
        e = self.err("a: 1\nb: 2\na: 3")
        self.assertEqual((e.line, e.col), (3, 1))
        self.assertIn("line 1", e.hint)

    def test_unclosed_points_to_opener(self):
        e = self.err('a: {\n  b: 1\n  c: [1, 2]\n')
        self.assertEqual(e.line, 1)

    def test_mismatched_bracket(self):
        self.assertIn("needs ']'", self.err("a: [1, 2}").message)

    def test_missing_close_bracket_before_key(self):
        e = self.err("a: {\n  b: [1, 2\n  c: 3\n}")
        self.assertEqual(e.line, 3)
        self.assertIn("']' missing", e.hint)

    def test_ambiguous_words(self):
        self.assertIn("true", self.err("enabled: yes").hint)
        self.assertIn("lowercase", self.err("enabled: True").hint)
        self.assertIn("quotes", self.err("a: true story").message)

    def test_text_after_number(self):
        self.assertIn("after this value", self.err("line1: 12 MG Road").message)
        self.assertIn("after this value", self.err("a: [1 2]").message)
        self.assertIn("after this value", self.err("a: 1 b: 2").message)

    def test_colon_in_text_catches_missing_separator(self):
        self.assertIn("': '", self.err("{a: x b: y}").message)

    def test_double_comma(self):
        self.assertIn("unexpected comma", self.err("a: [1,,2]").message)

    def test_numbers(self):
        self.assertIn("leading zeros", self.err("a: 007").hint)
        self.assertIn("versions", self.err("version: 1.4.2").hint)
        self.assertIn("0.5", self.err("a: .5").hint)
        self.assertIn("NaN", self.err("a: NaN").hint)
        self.assertIn("case-sensitive", self.err("a: 10mb").hint)
        self.assertIn("largest to smallest", self.err("a: 30m1h").message)

    def test_single_quotes(self):
        self.assertIn("double quotes", self.err("a: 'x'").hint)

    def test_equals_instead_of_colon(self):
        self.assertIn("':'", self.err("a = 1").hint)

    def test_missing_value(self):
        self.assertIn("missing value for 'a'", self.err("a:\nb: 1").message)
        self.assertIn("missing value", self.err("x: { a: }").message)

    def test_dates(self):
        self.assertIn("'T'", self.err("at: 2026-11-17 10:30").message)
        self.assertIn("invalid date", self.err("at: 2026-02-30").message)

    def test_unknown_escape_hints_raw_string(self):
        e = self.err(r'p: "C:\Users\me"')
        self.assertIn("raw string", e.hint)
        self.assertEqual(e.col, 7)

    def test_references(self):
        self.assertIn("unknown reference", self.err("a: *nope").message)
        self.assertIn("already defined", self.err("&x: 1\n&x: 2").message)
        self.assertIn("inside a string", self.err('&o: {}\na: f"${o}"').message)

    def test_error_text_has_caret(self):
        text = str(self.err("a: 1\nb: [oops: 1]"))
        self.assertIn("^", text)


class Writer(unittest.TestCase):
    SAMPLES = [
        {"name": "x", "n": 1, "f": 1.5, "t": True, "nil": None},
        {"nested": {"list": [1, 2, {"a": "b"}], "empty": {}, "e2": []}},
        {"date": dt.date(2026, 1, 2), "when": dt.datetime(2026, 1, 2, 3, 4, 5)},
        {"text": "line one\n  indented\n\nlast"},
        {"tricky": 'has """ quotes\nand \\ backslash'},
        {"ends_newline": "a\nb\n"},
        {"all_indented": "  a\n  b"},
        {"ws_line": "a\n   \nb"},
        {"weird key": 1, "true": 2, "9lives": 3, "editor.fontSize": 4},
        [1, "two", [3]],
        "just a string",
        {"strs": ["yes", "no", "True", "true story", "a: b", "x,y", "a;b", "#tag", "a #b",
                  "-v", "007", "1.4.2", "", " pad ", "C:\\path", "https://x.y/z", "10MB", "30s",
                  "2026-11-17", "null", "{x}", "say \"hi\"", "end:", "Priya Reddy", "tab\there"]},
        {"durations": [dt.timedelta(seconds=90), dt.timedelta(milliseconds=1500),
                       dt.timedelta(days=-1), dt.timedelta(0)]},
        {"table": [{"id": 1, "name": "A, B", "x": None}, {"id": 2, "name": "", "y": True},
                   {"id": 3, "name": "multi\nline", "x": 2.5}]},
        {"users": [{"id": i, "name": f"User {i}", "role": "admin" if i % 2 else "viewer"}
                   for i in range(5)]},
    ]

    def test_round_trip(self):
        for obj in self.SAMPLES:
            for kw in ({}, {"compact": True}, {"bare": False, "tables": False}):
                with self.subTest(obj=obj, kw=kw):
                    self.assertEqual(jot.loads(jot.dumps(obj, **kw)), obj)

    def test_uses_tables_and_bare_text(self):
        out = jot.dumps({"users": [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]})
        self.assertIn("[2:id,name", out)
        self.assertIn("1,A", out)

    def test_writer_picks_table_shapes(self):
        flags = {"flags": {f"f{i}": {"on": i % 2 == 0, "pct": i * 10} for i in range(3)}}
        self.assertIn("{3:on,pct", jot.dumps(flags))
        contacts = {"c": [{"n": "A", "addr": {"city": "X", "pin": 1}},
                          {"n": "B", "addr": {"city": "Y", "pin": 2}}]}
        self.assertIn("[2:n,addr{city,pin}", jot.dumps(contacts))
        orders = {"o": [{"id": 1, "items": [{"s": "a"}, {"s": "b"}]},
                        {"id": 2, "items": [{"s": "c"}, {"s": "d"}]}]}
        self.assertIn("[:s;a;b]", jot.dumps(orders, compact=True))
        self.assertNotIn("[:id", jot.dumps(orders))   # readable mode keeps cells simple
        for obj in (flags, contacts, orders):
            for kw in ({}, {"compact": True}):
                self.assertEqual(jot.loads(jot.dumps(obj, **kw)), obj)

    def test_balanced_mode(self):
        orders = {"o": [{"id": 1, "items": [{"s": "a"}, {"s": "b"}], "meta": {"x": 1}},
                        {"id": 2, "items": [{"s": "c"}, {"s": "d"}], "meta": {"x": 2}}]}
        out = jot.dumps(orders, balanced=True)
        self.assertNotIn("[:s;", out)          # no tables inside cells
        self.assertIn("[2:s\n", out)            # nested lists still become tables
        self.assertNotIn("{x:1}", out)         # no objects squeezed onto one line
        flat = {"u": [{"a": i, "b": f"n{i}"} for i in range(5)]}
        self.assertEqual(jot.dumps(flat, balanced=True), jot.dumps(flat, compact=True))
        for obj in (orders, flat):
            self.assertEqual(jot.loads(jot.dumps(obj, balanced=True)), obj)

    def test_from_json_is_lossless(self):
        src = json.dumps({
            "events": [{"at": "2025-05-29T09:09:53.479Z", "day": "2025-05-29", "tag": "x"},
                       {"at": "2025-05-29T09:09:53Z", "day": "2025-5-29", "tag": "y"},
                       {"at": "2025-05-29T09:09:53+00:00", "day": "2025-02-30", "tag": "z"}],
            "plain": "2025-01-01",
        })
        out = jot.from_json(src, compact=True)
        self.assertIn("2025-05-29T09:09:53.479Z", out)          # unquoted, survives exactly
        self.assertIn('"2025-05-29T09:09:53+00:00"', out)       # would change, so quoted
        self.assertEqual(json.loads(jot.to_json(out)), json.loads(src))

    def test_from_json(self):
        src = '{"a": {"b": [1, 2]}, "c": "x", "rows": [{"k": 1}, {"k": 2}]}'
        self.assertEqual(jot.loads(jot.from_json(src)), json.loads(src))
        self.assertEqual(jot.loads(jot.from_json(src, compact=True)), json.loads(src))


class CommandLine(unittest.TestCase):
    """The CLI layer: exit codes, file output, and output that isn't ASCII."""

    DATA = {
        "repo": "awesome",
        "desc": "\N{SMILING FACE WITH SUNGLASSES} lists",
        "who": "Jos\N{LATIN SMALL LETTER E WITH ACUTE} M\N{LATIN SMALL LETTER U WITH DIAERESIS}ller",
        "jp": "\N{CJK UNIFIED IDEOGRAPH-65E5}\N{CJK UNIFIED IDEOGRAPH-672C}",
    }

    def _run(self, *argv):
        """Runs main() with a cp1252 stdout, as on a default Windows console."""
        raw = io.BytesIO()
        err = io.StringIO()
        stdout = io.TextIOWrapper(raw, encoding="cp1252", newline="")
        real = sys.stdout
        sys.stdout = stdout
        try:
            with contextlib.redirect_stderr(err):
                code = jot.main(list(argv))
        finally:
            sys.stdout.flush()
            sys.stdout = real
        return code, raw.getvalue().decode("utf-8"), err.getvalue()

    @contextlib.contextmanager
    def _file(self, name, text):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, name)
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            yield path, d

    def test_non_ascii_survives_a_non_utf8_console(self):
        # Regression: stdout used to be written with the console's encoding, so
        # any non-ASCII datum raised UnicodeEncodeError on Windows.
        src = json.dumps(self.DATA, ensure_ascii=False)
        with self._file("u.json", src) as (path, _):
            code, out, _ = self._run("from-json", path)
        self.assertEqual(code, 0)
        self.assertIn(self.DATA["desc"], out)
        self.assertEqual(jot.loads(out), self.DATA)

    def test_to_json_non_ascii_on_a_non_utf8_console(self):
        with self._file("u.jot", "desc: " + self.DATA["desc"]) as (path, _):
            code, out, _ = self._run("to-json", path)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"desc": self.DATA["desc"]})

    def test_error_output_keeps_the_characters(self):
        # The caret line only lines up if the source line isn't escaped.
        bad = "t: [:x,y\n  " + self.DATA["desc"] + ",1,2\n]\n"
        with self._file("bad.jot", bad) as (path, _):
            code, _, err = self._run("check", path)
        self.assertEqual(code, 1)
        self.assertIn(self.DATA["desc"], err)
        self.assertIn("^", err)

    def test_check_exit_codes(self):
        with self._file("ok.jot", "a: 1") as (path, _):
            self.assertEqual(self._run("check", path)[0], 0)
        with self._file("bad.jot", "a: yes") as (path, _):
            code, _, err = self._run("check", path)
        self.assertEqual(code, 1)
        self.assertIn("hint:", err)

    def test_output_file_is_utf8_with_unix_newlines(self):
        src = json.dumps(self.DATA, ensure_ascii=False)
        with self._file("u.json", src) as (path, d):
            out = os.path.join(d, "out.jot")
            code, _, _ = self._run("from-json", path, "-o", out)
            self.assertEqual(code, 0)
            with open(out, "rb") as f:
                raw = f.read()
        self.assertEqual(jot.loads(raw.decode("utf-8")), self.DATA)
        self.assertNotIn(b"\r", raw)

    def test_round_trip_through_the_cli(self):
        src = json.dumps(self.DATA, ensure_ascii=False)
        with self._file("u.json", src) as (path, d):
            _, jot_text, _ = self._run("from-json", path, "--compact")
            mid = os.path.join(d, "mid.jot")
            with open(mid, "w", encoding="utf-8", newline="\n") as f:
                f.write(jot_text)
            code, back, _ = self._run("to-json", mid)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(back), self.DATA)

    def test_tokens_handles_non_ascii(self):
        with self._file("u.json", json.dumps(self.DATA, ensure_ascii=False)) as (path, _):
            code, out, _ = self._run("tokens", path)
        self.assertEqual(code, 0)
        self.assertIn("Jot", out)


if __name__ == "__main__":
    unittest.main()
