#Entry point for the Basic SQL Formatter.


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
    """
    Reads SQL from the user, formats it, and displays the result.
    """

    sql = input("\nEnter your SQL query:\n\n")

    # Check if the user entered anything
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


def main():
    """
    Main application loop.
    """

    while True:

        print_header()
        display_menu()

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            format_query()
            pause()

        elif choice == "2":
            about()
            pause()

        elif choice == "3":
            print("\nThank you for using Basic SQL Formatter!")
            print("Goodbye!")
            break

        else:
            print_error("Invalid choice. Please select 1, 2, or 3.")
            pause()


if __name__ == "__main__":
    main()