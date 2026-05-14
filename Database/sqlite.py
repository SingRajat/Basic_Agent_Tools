import sqlite3
from pathlib import Path

## Connect to SQLite database (creates student.db in the same folder as this script)
db_path = (Path(__file__).parent / "student.db").absolute()

try:
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Drop table if exists
    cursor.execute("DROP TABLE IF EXISTS STUDENT")

    # Create the table
    table_info = """
    CREATE TABLE STUDENT(
        NAME VARCHAR(25), 
        CLASS VARCHAR(25),
        SECTION VARCHAR(25),
        MARKS INT
    )
    """
    cursor.execute(table_info)

    # Insert records (slightly different from postgres.py)
    records = [
        ('Amit', 'DevOPS', 'B', 88),
        ('Priya', 'Data Science', 'A', 97),
        ('Sneha', 'Data Science', 'B', 91),
        ('Vikram', 'DevOPS', 'A', 85)
    ]

    for record in records:
        cursor.execute("INSERT INTO STUDENT (NAME, CLASS, SECTION, MARKS) VALUES (?, ?, ?, ?)", record)

    # Display all the records
    print("The inserted records are:")
    cursor.execute("SELECT * FROM STUDENT")
    data = cursor.fetchall()
    for row in data:
        print(row)

    # Commit and close
    connection.commit()
    cursor.close()
    connection.close()

except Exception as e:
    print(f"Error connecting to SQLite: {e}")
