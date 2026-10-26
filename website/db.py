
import pyodbc


def get_connection():
    """Connect to the registration database."""
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=registration;"
        "Trusted_Connection=yes;"
    )


def get_library_connection():
    """Connect to the library database."""
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=library;"
        "Trusted_Connection=yes;"
    )
