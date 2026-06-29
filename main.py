# Entry point for the Basic SQL Formatter.
from formatter import format_sql
from utils import (
    print_header,
    display_menu,
    about,
    pause,
    print_success,
    print_error,
)


def format_query():
    #Reads SQL from the user, formats it, and displays the result.
    sql = input("\nEnter your SQL query:\n\n")
    if not sql.strip():
        print_error("SQL query cannot be empty.")
        return

    print("\nFormatting SQL...\n")
    formatted_sql = format_sql(sql)

    print("=" * 45)
    print("FORMATTED SQL")
    print("=" * 45)
    print(formatted_sql)
    print("=" * 45)

    print_success()


def format_transaction_query():
    print("\nTransaction Formatter")
    print("-" * 45)
    print("Tip: Enter a full transaction block, e.g.:")
    print("  BEGIN TRANSACTION; UPDATE ... SET ...; COMMIT;")
    print()

    sql = input("Enter your transaction SQL:\n\n")
    if not sql.strip():
        print_error("SQL query cannot be empty.")
        return

    print("\nFormatting transaction...\n")
    formatted_sql = format_sql(sql)

    print("=" * 45)
    print("FORMATTED TRANSACTION")
    print("=" * 45)
    print(formatted_sql)
    print("=" * 45)

    print_success()


def format_view_query():
    print("\nView / CTE Formatter")
    print("-" * 45)
    print("Tip: Enter a CREATE VIEW statement or a WITH ... AS (...) CTE, e.g.:")
    print("  CREATE VIEW vw_sales AS SELECT region, SUM(amount) FROM orders GROUP BY region;")
    print("  WITH cte AS (SELECT ...) SELECT * FROM cte;")
    print()

    sql = input("Enter your View / CTE SQL:\n\n")
    if not sql.strip():
        print_error("SQL query cannot be empty.")
        return

    print("\nFormatting View / CTE...\n")
    formatted_sql = format_sql(sql)

    print("=" * 45)
    print("FORMATTED VIEW / CTE")
    print("=" * 45)
    print(formatted_sql)
    print("=" * 45)

    print_success()


def main():
    """Main application loop."""

    while True:

        print_header()
        display_menu()

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            format_query()
            pause()

        elif choice == "2":
            format_transaction_query()
            pause()

        elif choice == "3":
            format_view_query()
            pause()

        elif choice == "4":
            about()
            pause()

        elif choice == "5":
            print("\nThank you for using Basic SQL Formatter!")
            print("Goodbye!")
            break

        else:
            print_error("Invalid choice. Please select 1–5.")
            pause()


if __name__ == "__main__":
    main()