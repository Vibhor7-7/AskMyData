import sqlite3

# Create/connect to database with full path
db_path = 'c:\\Users\\divya\\Desktop\\Projects\\AskMyData\\backend\\users.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

try:
    # Check if table exists first
    c.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='users'
    """)
    if c.fetchone() is None:
        print("Table 'users' does not exist!")
    else:
        # Fetch and print users
        c.execute("SELECT fullname, username, email, password FROM users")
        rows = c.fetchall()
        if len(rows) == 0:
            print("No users found in database")
        else:
            for user in rows:
                print(f"Name: {user[0]}, Username: {user[1]}, Email: {user[2]}, Password Hash: {user[3]}")

except sqlite3.Error as e:
    print(f"Database error occurred: {e}")

finally:
    conn.close()
