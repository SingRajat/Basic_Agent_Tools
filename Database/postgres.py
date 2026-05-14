import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL configuration

try:
    connection = psycopg2.connect(
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "password"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )
    
    cursor = connection.cursor()

    # Drop table if exists (PostgreSQL doesn't support 'if not exists' in the same way for creation in older scripts)
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

    # Insert records
    records = [
        ('Ram', 'DevOPS', 'A', 90),
        ('Rajat', 'Data Science', 'A', 94),
        ('Raghav', 'Data Science', 'A', 96),
        ('Rahul', 'DevOPS', 'A', 93)
    ]
    
    for record in records:
        cursor.execute("INSERT INTO STUDENT (NAME, CLASS, SECTION, MARKS) VALUES (%s, %s, %s, %s)", record)

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
    print(f"Error connecting to PostgreSQL: {e}")
