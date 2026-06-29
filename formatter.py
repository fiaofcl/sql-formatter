#Contains all SQL formatting logic.

import re # regex; it is a super-powered version of str.replace() and str.find().
from keywords import ( # importing from the keywords 
    SQL_KEYWORDS,
    MULTI_WORD_KEYWORDS,
    CLAUSE_KEYWORDS,
    LOGICAL_OPERATORS,
    COMPARISON_OPERATORS
)

def uppercase_keywords(sql):
    #Convert SQL keywords to uppercase.

    for keyword in MULTI_WORD_KEYWORDS: #The loop runs once for each item.
        sql = re.sub(
            r"\b" + re.escape(keyword) + r"\b",
            keyword,
            sql,
            flags=re.IGNORECASE
        )

    for keyword in SQL_KEYWORDS: # for single sql words
        sql = re.sub( #re.sub() means substitute.
            r"\b" + re.escape(keyword) + r"\b", #It searches the string for the given pattern and replaces every match.
            keyword,
            sql,
            flags=re.IGNORECASE
        )

    return sql


def format_clauses(sql):
    #Places major SQL clauses on new lines.

    for clause in CLAUSE_KEYWORDS:

        if clause == "SELECT":
            continue

        sql = re.sub(
            r"\s*" + re.escape(clause),
            "\n" + clause,
            sql,
            flags=re.IGNORECASE
        )

    return sql.strip()


def format_operators(sql):
    #Adds spaces around comparison operators.

    # Process longer operators first
    operators = sorted(COMPARISON_OPERATORS, key=len, reverse=True)

    for operator in operators:

        escaped = re.escape(operator)

        sql = re.sub(
            rf"\s*{escaped}\s*",
            f" {operator} ",
            sql
        )

    return sql


def format_logical_operators(sql):
    #Places AND and OR on separate lines.
    for operator in LOGICAL_OPERATORS:

        sql = re.sub(
            rf"\s+{operator}\s+",
            f"\n    {operator} ",
            sql,
            flags=re.IGNORECASE
        )
    return sql


def format_select_columns(sql):
    #Formats SELECT column list.

    match = re.search(
        r"SELECT\s+(.*?)\s+FROM",
        sql,
        flags=re.IGNORECASE | re.DOTALL
    )
    if not match:
        return sql
    
    columns = match.group(1)
    columns = [c.strip() for c in columns.split(",")]
    formatted_columns = ",\n    ".join(columns)
    replacement = (
        "SELECT\n"
        f"    {formatted_columns}\n"
        "FROM\n    "
    )

    sql = re.sub(
        r"SELECT\s+.*?\s+FROM",
        replacement,
        sql,
        flags=re.IGNORECASE | re.DOTALL
    )

    return sql


def format_insert(sql):
    #Formats INSERT statements.

    if not sql.upper().startswith("INSERT"):
        return sql

    sql = re.sub(
        r"INSERT\s+INTO",
        "INSERT INTO",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"\bVALUES\b",
        "\nVALUES",
        sql,
        flags=re.IGNORECASE
    )

    sql = sql.replace("(", "\n(\n    ")
    sql = sql.replace(")", "\n)")
    sql = sql.replace(",", ",\n    ")

    return sql


def format_update(sql):
    #Formats UPDATE statements.
    if not sql.upper().startswith("UPDATE"):
        return sql

    sql = re.sub(
        r"\bSET\b",
        "\nSET\n    ",
        sql,
        flags=re.IGNORECASE
    )

    sql = sql.replace(",", ",\n    ")

    sql = re.sub(
        r"\bWHERE\b",
        "\nWHERE\n    ",
        sql,
        flags=re.IGNORECASE
    )

    return sql
def format_delete(sql):
    #Formats DELETE statements.
    
    if not sql.upper().startswith("DELETE"):
        return sql

    sql = re.sub(
        r"DELETE\s+FROM",
        "DELETE FROM",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"\bWHERE\b",
        "\nWHERE\n    ",
        sql,
        flags=re.IGNORECASE
    )

    return sql


def indent_clauses(sql):
    #Indents text after SQL clauses.

    clauses = [
        "FROM",
        "WHERE",
        "GROUP BY",
        "ORDER BY",
        "HAVING",
        "LIMIT",
        "VALUES",
        "SET"
    ]

    for clause in clauses:
        sql = re.sub(
            rf"{re.escape(clause)}\s+",
            f"{clause}\n    ",
            sql,
            flags=re.IGNORECASE
        )

    return sql


def clean_sql(sql):
    #Cleans up extra spaces and blank lines.
    # Remove multiple spaces
    sql = re.sub(r"[ \t]+", " ", sql)

    # Remove extra blank lines
    sql = re.sub(r"\n{2,}", "\n", sql)

    # Remove spaces before commas
    sql = re.sub(r"\s+,", ",", sql)

    # Remove trailing spaces on each line
    sql = "\n".join(line.rstrip() for line in sql.splitlines())

    return sql.strip()


def format_sql(sql):
    #Main formatting function.

    sql = sql.strip()

    if not sql:
        return ""

    sql = uppercase_keywords(sql)

    sql = format_clauses(sql)

    sql = format_select_columns(sql)

    sql = format_insert(sql)

    sql = format_update(sql)

    sql = format_delete(sql)

    sql = format_operators(sql)

    sql = format_logical_operators(sql)

    sql = indent_clauses(sql)

    sql = clean_sql(sql)

    return sql