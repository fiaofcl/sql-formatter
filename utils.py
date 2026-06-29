#Helper functions used throughout the Basic SQL Formatter.


def print_header():
    #Displays the application header.
    print("=" * 45)
    print("         BASIC SQL FORMATTER")
    print("=" * 45)


def display_menu():
    #Displays the main menu.
    print("\n1. Format SQL")
    print("2. About")
    print("3. Exit")


def about():
    #Displays information about the application.
    print("\nAbout")
    print("-" * 45)
    print("Basic SQL Formatter")
    print("Version : 1.0")
    print("Language : Python")
    print("\nFeatures:")
    print("• Formats SQL queries for better readability")
    print("• Converts SQL keywords to uppercase")
    print("• Adds proper indentation")
    print("• Adds spaces around operators")
    print("• Interactive command-line interface")
    print("\nThis project is intended for learning and educational purposes.")


def pause():
    #Pauses the program until the user presses Enter.
    input("\nPress Enter to continue...")

def print_success():
    #Displays a success message.
    print("\n✓ SQL formatted successfully!")

def print_error(message):
    #Displays an error message.
    #Parameters:message (str): Error description.
    print(f"\nError: {message}")