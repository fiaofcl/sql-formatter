#keywords.py
#Contains all SQL keywords supported by the Basic SQL Formatter.

# Single-word SQL keywords
SQL_KEYWORDS = [
    "SELECT",
    "FROM",
    "WHERE",
    "INSERT",
    "INTO",
    "VALUES",
    "UPDATE",
    "SET",
    "DELETE",
    "CREATE",
    "TABLE",
    "ALTER",
    "DROP",
    "JOIN",
    "INNER",
    "LEFT",
    "RIGHT",
    "FULL",
    "OUTER",
    "ON",
    "AS",
    "DISTINCT",
    "HAVING",
    "LIMIT",
    "OFFSET",
    "UNION",
    "ALL",
    "CASE",
    "WHEN",
    "THEN",
    "ELSE",
    "END",
    "LIKE",
    "IN",
    "BETWEEN",
    "IS",
    "NULL",
    "NOT",
    "EXISTS",
    "AND",
    "OR",
    "ASC",
    "DESC"
]

# Multi-word SQL keywords( These will be checked before single-word keywords )
MULTI_WORD_KEYWORDS = [
    "ORDER BY",
    "GROUP BY",
    "INNER JOIN",
    "LEFT JOIN",
    "RIGHT JOIN",
    "FULL OUTER JOIN",
    "LEFT OUTER JOIN",
    "RIGHT OUTER JOIN",
    "UNION ALL",
    "CREATE TABLE",
    "ALTER TABLE",
    "INSERT INTO",
    "DELETE FROM"
]

# Keywords that should start on a new line
CLAUSE_KEYWORDS = [
    "SELECT",
    "FROM",
    "WHERE",
    "GROUP BY",
    "HAVING",
    "ORDER BY",
    "LIMIT",
    "INSERT INTO",
    "VALUES",
    "UPDATE",
    "SET",
    "DELETE FROM",
    "INNER JOIN",
    "LEFT JOIN",
    "RIGHT JOIN",
    "FULL OUTER JOIN",
    "ON"
]

# Logical operators that should appear on new lines
LOGICAL_OPERATORS = [
    "AND",
    "OR"
]

# Comparison operators
COMPARISON_OPERATORS = [
    ">=",
    "<=",
    "<>",
    "!=",
    "=",
    ">",
    "<"
]