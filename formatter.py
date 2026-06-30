import re
from keywords import (
    SQL_KEYWORDS,
    MULTI_WORD_KEYWORDS,
    CLAUSE_KEYWORDS,
    LOGICAL_OPERATORS,
    COMPARISON_OPERATORS,
)


# ── Helpers ──────────────────────────────────────────────────────────

def _detect_statement_type(sql):
    """Return the leading SQL statement keyword in uppercase, or '' if unknown."""
    first = sql.strip().split()[0].upper() if sql.strip() else ""
    return first


def _indent_block(text, spaces=4):
    """Indent every line of *text* by *spaces* spaces."""
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line for line in text.splitlines())


# ── Spacing normalisation ─────────────────────────────────────────────────────

def normalize_spacing(sql):
    # Keywords too short / common to split safely
    SKIP = {
        "IN", "AS", "OR", "BY", "ON", "OF", "IS", "AT", "DO",
        "IF", "GO", "NO", "TO", "UP", "ID", "ALL", "AND", "NOT",
        "SET", "ROW", "END", "FOR", "KEY", "NEW", "OLD", "OUT",
        "ADD", "USE",
    }

    all_keywords = sorted(
        set(MULTI_WORD_KEYWORDS) | set(SQL_KEYWORDS),
        key=len,
        reverse=True,
    )

    keyword_pattern = "|".join(
        re.escape(k) for k in all_keywords
    )

    sql = re.sub(
        rf"\)(?=\s*(?:{keyword_pattern})\b)",
        ")\n",
        sql,
        flags=re.IGNORECASE,
    )

    return sql
    all_keywords = sorted(
        set(MULTI_WORD_KEYWORDS) | set(SQL_KEYWORDS),
        key=len,
        reverse=True,
    )

    for keyword in all_keywords:
        if keyword in SKIP:
            continue
        if len(keyword) < 4:
            continue

        escaped = re.escape(keyword)


        sql = re.sub(
            r"(?<=[a-z0-9])(" + escaped + r")\b",
            r" \1",
            sql,
        )

        sql = re.sub(
            r"(?<=[a-z])(" + escaped + r")(?=\s|$|\W)",
            r" \1",
            sql,
        )

        sql = re.sub(
            r"\b(" + escaped + r")(?=[a-z])",
            r"\1 ",
            sql,
        )

    return sql


def uppercase_keywords(sql):

    def _not_sigil_prefixed(keyword):
        return r"(?<![@#])\b" + re.escape(keyword) + r"\b"

    # Multi-word first to avoid partial matches
    for keyword in sorted(MULTI_WORD_KEYWORDS, key=len, reverse=True):
        sql = re.sub(
            _not_sigil_prefixed(keyword),
            keyword,
            sql,
            flags=re.IGNORECASE,
        )

    for keyword in SQL_KEYWORDS:
        sql = re.sub(
            _not_sigil_prefixed(keyword),
            keyword,
            sql,
            flags=re.IGNORECASE,
        )

    return sql


# ── CTE formatting ────────────────────────────────────────────────────────────

def format_cte(sql):
    if not re.match(r"^\s*WITH\b", sql, re.IGNORECASE):
        return sql

    # Put each comma-separated CTE on its own line
    # Only split commas that are followed by an identifier then AS (
    sql = re.sub(
        r"\)\s*,\s*(?=\s*\w)",
        "),\n",
        sql,
    )

    # Ensure WITH / WITH RECURSIVE is at the start of its line
    sql = re.sub(r"\bWITH\s+RECURSIVE\b", "WITH RECURSIVE", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\bWITH\b(?!\s+RECURSIVE)", "WITH", sql, flags=re.IGNORECASE)

    # Put AS ( on same line as CTE name, opening paren on new line
    sql = re.sub(r"\bAS\s*\(", "AS (\n", sql, flags=re.IGNORECASE)

    return sql


# ── Transaction formatting ────────────────────────────────────────────────────

def format_transaction(sql):

    # Multi-word transaction keywords — longest first
    transaction_keywords = [
        "BEGIN TRANSACTION",
        "BEGIN WORK",
        "START TRANSACTION",
        "COMMIT TRANSACTION",
        "COMMIT WORK",
        "ROLLBACK TRANSACTION",
        "ROLLBACK WORK",
        "ROLLBACK TO SAVEPOINT",
        "ROLLBACK TO",
        "RELEASE SAVEPOINT",
        "SET TRANSACTION",
        "ISOLATION LEVEL",
        "READ COMMITTED",
        "READ UNCOMMITTED",
        "REPEATABLE READ",
    ]

    single_transaction_keywords = [
        "COMMIT",
        "ROLLBACK",
        "SAVEPOINT",
        "BEGIN",
    ]

    for kw in transaction_keywords:
        sql = re.sub(
            r"\s*\b" + re.escape(kw) + r"\b\s*",
            f"\n{kw} ",
            sql,
            flags=re.IGNORECASE,
        )

    for kw in single_transaction_keywords:
        sql = re.sub(
            r"\s*\b" + re.escape(kw) + r"\b\s*",
            f"\n{kw} ",
            sql,
            flags=re.IGNORECASE,
        )

    return sql.strip()


_PROC_TOKEN_RE = re.compile(
    r"""
    (?P<string>'(?:[^']|'')*')          |
    (?P<paren_open>\()                   |
    (?P<paren_close>\))                  |
    (?P<endnamed>\bEND\s+(?:IF|LOOP|WHILE|FOR|CASE)\b) |
    (?P<begin>\bBEGIN\b)                 |
    (?P<case>\bCASE\b)                   |
    (?P<end>\bEND\b)                     |
    (?P<semicolon>;)
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _is_procedure_definition(sql):
    """True if *sql* is a CREATE/ALTER PROCEDURE/FUNCTION/TRIGGER definition."""
    stmt_type = _detect_statement_type(sql)
    if stmt_type not in ("CREATE", "ALTER"):
        return False
    return bool(re.search(r"\b(PROCEDURE|FUNCTION|TRIGGER)\b", sql, re.IGNORECASE))


def _find_matching_end(sql, start):
    stack = ["BEGIN"]
    paren_depth = 0

    for m in _PROC_TOKEN_RE.finditer(sql, start):
        if m.group("string"):
            continue
        if m.group("paren_open"):
            paren_depth += 1
            continue
        if m.group("paren_close"):
            paren_depth = max(paren_depth - 1, 0)
            continue
        if paren_depth > 0:
            continue

        if m.group("begin") or m.group("case"):
            stack.append("BEGIN" if m.group("begin") else "CASE")
        elif m.group("endnamed"):
            # Closes an IF/LOOP/WHILE/FOR/CASE construct, not BEGIN.
            if stack and stack[-1] == "CASE" and m.group(0).upper().endswith("CASE"):
                stack.pop()
        elif m.group("end"):
            if stack:
                stack.pop()
            if not stack:
                return m.start(), m.start("end"), m.end("end")

    return None


def _split_top_level_statements(body):
    statements = []
    stack = []
    paren_depth = 0
    start = 0

    for m in _PROC_TOKEN_RE.finditer(body):
        if m.group("string"):
            continue
        if m.group("paren_open"):
            paren_depth += 1
            continue
        if m.group("paren_close"):
            paren_depth = max(paren_depth - 1, 0)
            continue
        if paren_depth > 0:
            continue

        if m.group("begin") or m.group("case"):
            stack.append("BEGIN" if m.group("begin") else "CASE")
        elif m.group("endnamed"):
            if stack and stack[-1] == "CASE" and m.group(0).upper().endswith("CASE"):
                stack.pop()
        elif m.group("end"):
            if stack:
                stack.pop()
        elif m.group("semicolon"):
            if not stack:
                chunk = body[start:m.end()]
                if chunk.strip():
                    statements.append(chunk.strip())
                start = m.end()

    tail = body[start:].strip()
    if tail:
        statements.append(tail)

    return statements


def _format_statement_chunk(stmt):
    stmt = stmt.strip()
    if not stmt:
        return stmt

    has_trailing_semicolon = stmt.endswith(";")
    core = stmt[:-1].strip() if has_trailing_semicolon else stmt

    try:
        formatted = _format_inner_statement(core)
    except Exception:
        formatted = core

    if has_trailing_semicolon:
        formatted += ";"

    return formatted


def _format_inner_statement(sql):
    sql = format_merge(sql)
    sql = format_case(sql)
    sql = format_window(sql)
    sql = format_clauses(sql)
    sql = format_select_columns(sql)
    sql = format_insert(sql)
    sql = format_update(sql)
    sql = format_delete(sql)
    sql = format_grouping_sets(sql)
    sql = format_operators(sql)
    sql = format_logical_operators(sql)
    sql = indent_clauses(sql)
    sql = clean_sql(sql)
    return sql


def _format_block_body(body, depth):
    pieces = []

    for stmt in _split_top_level_statements(body):
        pieces.extend(_format_chunk_with_possible_nesting(stmt))

    indented = [_indent_block(p, spaces=4) for p in pieces]
    result = "\n".join(indented)

    if depth > 1:
        result = _indent_block(result, spaces=4 * (depth - 1))

    return result


def _format_chunk_with_possible_nesting(stmt):
    begin_match = re.search(r"\bBEGIN\b", stmt, re.IGNORECASE)
    if not begin_match:
        return [_format_statement_chunk(stmt)]

    header = stmt[:begin_match.start()].rstrip()

    match = _find_matching_end(stmt, begin_match.end())
    if match is None:
        # Malformed / unmatched block — fall back to returning as-is.
        return [stmt]

    body_end, end_start, end_end = match
    inner_body = stmt[begin_match.end():body_end]
    remainder = stmt[end_end:].strip()

    inner_formatted = _format_block_body(inner_body, depth=1)

    lines = []
    if header:
        lines.append(header)
    lines.append("BEGIN")
    if inner_formatted:
        lines.append(inner_formatted)
    lines.append("END")

    pieces = ["\n".join(lines)]

    if remainder:
        # Whatever follows this block's END (no semicolon separated it
        # from END, otherwise the splitter would already have cut here)
        # is one or more further sibling statements at the same level.
        for sub_stmt in _split_top_level_statements(remainder):
            pieces.extend(_format_chunk_with_possible_nesting(sub_stmt))

    return pieces


def format_procedure(sql):
    if not _is_procedure_definition(sql):
        return sql

    begin_match = re.search(r"\bBEGIN\b", sql, re.IGNORECASE)
    if not begin_match:
        # No BEGIN...END body (e.g. a single-expression function) —
        # nothing structural to do beyond putting AS on its own line.
        return re.sub(r"\bAS\b(?!\s*\()", "\nAS", sql, flags=re.IGNORECASE).strip()

    header = sql[:begin_match.start()].rstrip()
    header = re.sub(r"\bAS\b(?!\s*\()", "\nAS", header, flags=re.IGNORECASE)

    match = _find_matching_end(sql, begin_match.end())
    if match is None:
        # Unmatched BEGIN — bail out gracefully rather than mangling it.
        return sql

    body_end, end_start, end_end = match
    body = sql[begin_match.end():body_end]
    trailer = sql[end_end:].strip()

    formatted_body = _format_block_body(body, depth=1)

    lines = [header.strip(), "BEGIN"]
    if formatted_body:
        lines.append(formatted_body)
    end_line = "END" + (" " + trailer if trailer else "")
    lines.append(end_line)

    return "\n".join(lines)


# ── MERGE formatting ──────────────────────────────────────────────────────────

def format_merge(sql):
    if not re.match(r"^\s*MERGE\b", sql, re.IGNORECASE):
        return sql

    merge_clauses = [
        "WHEN NOT MATCHED BY SOURCE",
        "WHEN NOT MATCHED BY TARGET",
        "WHEN NOT MATCHED",
        "WHEN MATCHED",
        "MERGE INTO",
        "USING",
    ]

    for clause in merge_clauses:
        sql = re.sub(
            r"\s*\b" + re.escape(clause) + r"\b",
            f"\n{clause}",
            sql,
            flags=re.IGNORECASE,
        )

    # THEN on same line, action indented below
    sql = re.sub(r"\bTHEN\b\s*", "THEN\n    ", sql, flags=re.IGNORECASE)

    return sql.strip()


# ── CASE formatting ───────────────────────────────────────────────────────────

def format_case(sql):
    # CASE on its own line
    sql = re.sub(r"\bCASE\b", "\nCASE", sql, flags=re.IGNORECASE)

    # Each WHEN on its own indented line
    sql = re.sub(r"\s*\bWHEN\b", "\n    WHEN", sql, flags=re.IGNORECASE)

    # THEN stays on the same line as WHEN — just ensure one space
    sql = re.sub(r"\bTHEN\b\s*", "THEN ", sql, flags=re.IGNORECASE)

    # ELSE on its own indented line
    sql = re.sub(r"\s*\bELSE\b", "\n    ELSE", sql, flags=re.IGNORECASE)

    # END on its own line (but not END IF / END LOOP etc.)
    sql = re.sub(r"\s*\bEND\b(?!\s+(?:IF|LOOP|WHILE|FOR|CASE))", "\nEND", sql, flags=re.IGNORECASE)

    return sql


# ── Window function formatting ────────────────────────────────────────────────

def format_window(sql):
    result = []
    i = 0
    upper = sql.upper()

    while i < len(sql):
        # Detect OVER followed by optional whitespace then (
        over_match = re.match(r"OVER\s*\(", upper[i:], re.IGNORECASE)
        if over_match:
            # Consume "OVER ("
            consumed = over_match.group(0)
            result.append("OVER (")
            i += len(consumed)

            # Collect everything inside the matching closing paren
            depth = 1
            inner = []
            while i < len(sql) and depth > 0:
                ch = sql[i]
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                if depth > 0:
                    inner.append(ch)
                i += 1

            # Reformat the interior of OVER(...)
            inner_sql = "".join(inner).strip()

            # PARTITION BY on its own indented line
            inner_sql = re.sub(
                r"\s*\bPARTITION\s+BY\b",
                "\n    PARTITION BY",
                inner_sql,
                flags=re.IGNORECASE,
            )

            # ORDER BY inside OVER on its own indented line
            inner_sql = re.sub(
                r"\s*\bORDER\s+BY\b",
                "\n    ORDER BY",
                inner_sql,
                flags=re.IGNORECASE,
            )

            # Frame clauses (ROWS/RANGE/GROUPS BETWEEN) on their own line
            inner_sql = re.sub(
                r"\s*\b(ROWS|RANGE|GROUPS)\s+BETWEEN\b",
                r"\n    \1 BETWEEN",
                inner_sql,
                flags=re.IGNORECASE,
            )

            inner_sql = inner_sql.strip()
            if inner_sql:
                result.append("\n    " + inner_sql + "\n)")
            else:
                result.append(")")
        else:
            result.append(sql[i])
            i += 1

    return "".join(result)

def format_clauses(sql):
    sorted_clauses = sorted(CLAUSE_KEYWORDS, key=len, reverse=True)

    for clause in sorted_clauses:
        if clause == "SELECT":
            # SELECT is handled by format_select_columns
            continue

        if clause in ("BEGIN", "END"):
            # Handled by format_procedure / format_transaction
            continue

        # Match the keyword only when it appears as a whole word
        # preceded by whitespace or start-of-string — never mid-identifier.
        sql = re.sub(
            r"(?<![@#\w])(" + re.escape(clause) + r")(?!\w)",
            r"\n\1",
            sql,
            flags=re.IGNORECASE,
        )

    return sql.strip()


# ── SELECT column list formatting ─────────────────────────────────────────────

def format_select_columns(sql):
    match = re.search(
        r"SELECT\s+(.*?)\s+FROM",
        sql,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return sql

    columns_raw = match.group(1)

    # Split on commas that are NOT inside parentheses (protects functions)
    columns = []
    depth = 0
    current = []
    for char in columns_raw:
        if char == "(":
            depth += 1
            current.append(char)
        elif char == ")":
            depth -= 1
            current.append(char)
        elif char == "," and depth == 0:
            columns.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        columns.append("".join(current).strip())

    formatted_columns = ",\n    ".join(columns)
    replacement = f"SELECT\n    {formatted_columns}\nFROM\n    "

    sql = re.sub(
        r"SELECT\s+.*?\s+FROM",
        replacement,
        sql,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )

    return sql

def format_insert(sql):
    stmt = _detect_statement_type(sql)
    if stmt != "INSERT":
        return sql

    # Normalise INSERT variants
    sql = re.sub(r"INSERT\s+OR\s+REPLACE", "INSERT OR REPLACE", sql, flags=re.IGNORECASE)
    sql = re.sub(r"INSERT\s+OR\s+IGNORE", "INSERT OR IGNORE", sql, flags=re.IGNORECASE)
    sql = re.sub(r"INSERT\s+IGNORE", "INSERT IGNORE", sql, flags=re.IGNORECASE)
    sql = re.sub(r"INSERT\s+INTO", "INSERT INTO", sql, flags=re.IGNORECASE)

    # VALUES on new line
    sql = re.sub(r"\s*\bVALUES\b", "\nVALUES", sql, flags=re.IGNORECASE)

    # ON CONFLICT on new line
    sql = re.sub(r"\s*\bON\s+CONFLICT\b", "\nON CONFLICT", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*\bDO\s+UPDATE\b", "\n    DO UPDATE", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*\bDO\s+NOTHING\b", "\n    DO NOTHING", sql, flags=re.IGNORECASE)

    # RETURNING on new line
    sql = re.sub(r"\s*\bRETURNING\b", "\nRETURNING", sql, flags=re.IGNORECASE)

    # Format column list and values list inside parentheses
    # Only reformat parens that directly follow INTO ... or VALUES
    sql = _format_paren_list(sql)

    return sql


def _format_paren_list(sql):
    result = []
    i = 0
    paren_count = 0

    while i < len(sql):
        ch = sql[i]

        if ch == "(" and paren_count == 0:
            # Collect the content of this paren group
            paren_count += 1
            inner = []
            i += 1
            while i < len(sql) and paren_count > 0:
                if sql[i] == "(":
                    paren_count += 1
                elif sql[i] == ")":
                    paren_count -= 1
                if paren_count > 0:
                    inner.append(sql[i])
                i += 1
            inner_str = "".join(inner).strip()
            # Only reformat if it looks like a column/value list (has commas)
            if "," in inner_str:
                items = [item.strip() for item in inner_str.split(",")]
                formatted = ",\n    ".join(items)
                result.append(f"(\n    {formatted}\n)")
            else:
                result.append(f"({inner_str})")
            continue

        result.append(ch)
        i += 1

    return "".join(result)


# ── UPDATE formatting ─────────────────────────────────────────────────────────

def format_update(sql):
    if _detect_statement_type(sql) != "UPDATE":
        return sql

    sql = re.sub(r"\s*\bSET\b", "\nSET\n    ", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*\bWHERE\b", "\nWHERE\n    ", sql, flags=re.IGNORECASE)

    # Split SET assignments by comma (not inside parens)
    def split_set(match):
        content = match.group(1)
        parts = [p.strip() for p in content.split(",")]
        return "SET\n    " + ",\n    ".join(parts)

    sql = re.sub(
        r"SET\n\s+(.*?)\n(?=WHERE|\Z)",
        split_set,
        sql,
        flags=re.IGNORECASE | re.DOTALL,
    )

    return sql


# ── DELETE formatting ─────────────────────────────────────────────────────────

def format_delete(sql):

    if _detect_statement_type(sql) != "DELETE":
        return sql

    sql = re.sub(r"DELETE\s+FROM", "DELETE FROM", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*\bWHERE\b", "\nWHERE\n    ", sql, flags=re.IGNORECASE)

    return sql


# ── GROUPING SETS / ROLLUP / CUBE formatting ──────────────────────────────────

def format_grouping_sets(sql):
    for keyword in ("GROUPING SETS", "ROLLUP", "CUBE"):
        pattern = re.escape(keyword) + r"\s*\("
        replacement = f"{keyword} (\n    "
        sql = re.sub(pattern, replacement, sql, flags=re.IGNORECASE)

    return sql


# ── Operator formatting ───────────────────────────────────────────────────────

def format_operators(sql):
    skip_in_context = {"->>", "->", "#>>", "#>", "@>", "<@", "&&", "||"}

    regular_ops = [op for op in COMPARISON_OPERATORS if op not in skip_in_context]
    context_ops = [op for op in skip_in_context if op in COMPARISON_OPERATORS]

    def _by_len_desc(ops):
        return sorted(set(ops), key=len, reverse=True)

    if context_ops:
        pattern = "|".join(re.escape(op) for op in _by_len_desc(context_ops))
        sql = re.sub(
            rf"(?<=\w)[ \t]*(?:{pattern})[ \t]*(?=\w)",
            lambda m: f" {m.group(0)} ",
            sql,
        )

    if regular_ops:
        pattern = "|".join(re.escape(op) for op in _by_len_desc(regular_ops))
        sql = re.sub(
            rf"[ \t]*(?:{pattern})[ \t]*",
            lambda m: f" {m.group(0)} ",
            sql,
        )
        # An operator right after a newline shouldn't gain a leading
        # space (it should stay at the start of its line); an operator
        # right before a newline shouldn't leave a trailing space
        # dangling before the line break.
        sql = re.sub(
            rf"\n [ \t]*(?:{pattern})",
            lambda m: "\n" + m.group(0).lstrip(" \t")[1:],
            sql,
        )
        sql = re.sub(
            rf"(?:{pattern})[ \t]* \n",
            lambda m: m.group(0)[:-2] + "\n",
            sql,
        )

    return sql


# ── Logical operator formatting ───────────────────────────────────────────────

def format_logical_operators(sql):
    for operator in LOGICAL_OPERATORS:
        sql = re.sub(
            rf"\s+\b{operator}\b\s+",
            f"\n    {operator} ",
            sql,
            flags=re.IGNORECASE,
        )
    return sql


# ── Clause indentation ────────────────────────────────────────────────────────

def indent_clauses(sql):
    sorted_clauses = sorted(CLAUSE_KEYWORDS, key=len, reverse=True)

    for clause in sorted_clauses:
        # (?:^|\n) ensures we only match at line boundaries
        sql = re.sub(
            r"(?m)^(" + re.escape(clause) + r")\s+",
            r"\1\n    ",
            sql,
            flags=re.IGNORECASE,
        )

    return sql


# ── Final cleanup ─────────────────────────────────────────────────────────────

def clean_sql(sql):
    """Cleans up extra spaces, blank lines, and trailing whitespace."""
    # Collapse runs of interior spaces/tabs to one space, but preserve
    # leading indentation on each line — that whitespace encodes the
    # indent level set by earlier formatting passes (e.g. 4-space nesting
    # inside procedure bodies) and must not be flattened to one space.
    def _collapse_interior(line):
        stripped = line.lstrip(" \t")
        leading = line[: len(line) - len(stripped)]
        collapsed = re.sub(r"[ \t]+", " ", stripped)
        return leading + collapsed

    sql = "\n".join(_collapse_interior(line) for line in sql.splitlines())

    # Remove more than one consecutive blank line
    sql = re.sub(r"\n{3,}", "\n\n", sql)

    # Remove spaces before commas
    sql = re.sub(r"[ \t]+,", ",", sql)

    # Remove spaces before semicolons
    sql = re.sub(r"[ \t]+;", ";", sql)

    # Remove trailing whitespace on each line
    sql = "\n".join(line.rstrip() for line in sql.splitlines())

    # Remove leading blank lines
    sql = sql.lstrip("\n")

    return sql.strip()


# ── Main entry point ──────────────────────────────────────────────────────────

def format_sql(sql):
    sql = sql.strip()

    if not sql:
        return ""

    sql = uppercase_keywords(sql)
    sql = normalize_spacing(sql)

    if _is_procedure_definition(sql):
        sql = format_procedure(sql)
        return clean_sql(sql)

    sql = format_cte(sql)
    sql = format_transaction(sql)
    sql = format_merge(sql)
    sql = format_case(sql)
    sql = format_window(sql)
    sql = format_clauses(sql)
    sql = format_select_columns(sql)
    sql = format_insert(sql)
    sql = format_update(sql)
    sql = format_delete(sql)
    sql = format_grouping_sets(sql)
    sql = format_operators(sql)
    sql = format_logical_operators(sql)
    sql = indent_clauses(sql)
    sql = clean_sql(sql)

    return sql
