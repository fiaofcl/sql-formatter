# SQL Formatter

A rule-based SQL Formatter built using **Python** that automatically formats SQL queries into a clean and readable structure.

This project is designed to improve the readability of SQL statements by applying common formatting conventions such as keyword capitalization, indentation, clause separation, and operator spacing.

> **Note:** This formatter uses rule-based string processing and regular expressions. It is intended for learning purposes and supports common SQL statements rather than the complete SQL language.

---

## Features

- Converts SQL keywords to uppercase
- Formats `SELECT` statements
- Formats `INSERT` statements
- Formats `UPDATE` statements
- Formats `DELETE` statements
- Places SQL clauses on separate lines
- Formats column lists
- Adds proper spacing around comparison operators
- Places logical operators (`AND`, `OR`) on separate lines
- Indents SQL clauses for improved readability
- Removes unnecessary spaces and blank lines
- Interactive command-line interface

---

## Supported SQL Statements

- SELECT
- INSERT
- UPDATE
- DELETE

Supported clauses include:

- FROM
- WHERE
- GROUP BY
- ORDER BY
- HAVING
- LIMIT
- VALUES
- SET

---

## Project Structure

```text
sql-formatter/
│
├── main.py
├── formatter.py
├── keywords.py
├── utils.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/your-username/sql-formatter.git
```

Move into the project

```bash
cd sql-formatter
```

No external libraries are required since the project uses only Python's standard library.

---

## Running the Project

Run the program using:

```bash
python main.py
```

The program starts in interactive mode.

Example:

```
Enter SQL Query:
select id,name from student where age>=18;
```

Output:

```sql
SELECT
    id,
    name
FROM
    student
WHERE
    age >= 18;
```

---

## Example Queries

### SELECT

Input

```sql
select id,name from student where age>=18;
```

Output

```sql
SELECT
    id,
    name
FROM
    student
WHERE
    age >= 18;
```

---

### INSERT

Input

```sql
insert into student(id,name,age) values(1,'John',20);
```

Output

```sql
INSERT INTO student
(
    id,
    name,
    age
)
VALUES
(
    1,
    'John',
    20
);
```

---

### UPDATE

Input

```sql
update employee set salary=50000,department='IT' where id=5;
```

Output

```sql
UPDATE employee
SET
    salary = 50000,
    department = 'IT'
WHERE
    id = 5;
```

---

### DELETE

Input

```sql
delete from employee where id=10;
```

Output

```sql
DELETE FROM
    employee
WHERE
    id = 10;
```

---

## How It Works

The formatter processes the SQL query in multiple stages:

1. Converts SQL keywords to uppercase.
2. Places SQL clauses on separate lines.
3. Formats SELECT column lists.
4. Formats INSERT statements.
5. Formats UPDATE statements.
6. Formats DELETE statements.
7. Adds spacing around comparison operators.
8. Formats logical operators (`AND`, `OR`).
9. Indents SQL clauses.
10. Removes unnecessary whitespace.

Each formatting task is handled by a separate function inside `formatter.py`, making the code modular and easy to maintain.

---

## Technologies Used

- Python 3
- Regular Expressions (`re` module)

---

## Concepts Demonstrated

This project demonstrates:

- Functions
- Modular Programming
- String Manipulation
- Regular Expressions (Regex)
- Loops
- Lists
- Conditional Statements
- Pattern Matching
- Interactive Command-Line Applications

---

## Current Limitations

This formatter is designed for basic SQL statements and does **not** fully support:

- Nested queries
- Complex JOIN operations
- Common Table Expressions (CTEs)
- Window Functions
- Stored Procedures
- Triggers
- Views
- SQL Dialect-specific syntax

---

## Future Improvements

- SQL syntax validation
- Automatic indentation levels
- JOIN formatting
- Nested query formatting
- SQL file formatting
- Export formatted SQL to a file
- GUI using Tkinter or Streamlit
- Web version using Flask

---

## License

This project is intended for learning and educational purposes.