import sqlite3
from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime
# Initialize the database
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    # Create the records table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            phone_name TEXT NOT NULL,
            service TEXT NOT NULL,
            name TEXT NOT NULL,
            amount TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


init_db()

def view_users(conn):
    """Retrieve and display all users from the 'users' table."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password, role FROM users")
        rows = cursor.fetchall()

        if not rows:
            print("No users found in the database.")
        else:
            print("\nUsers in the database:")
            print(f"{'ID':<5} {'Username':<15} {'Password':<20} {'Role':<10}")
            print("-" * 50)
            for row in rows:
                user_id, username, password, role = row
                print(f"{user_id:<5} {username:<15} {password:<20} {role:<10}")
    except sqlite3.Error as e:
        print(f"Error retrieving users: {e}")

def add_user(conn, username, password, role):
    """Add a new user to the 'users' table."""
    try:
        cursor = conn.cursor()
        # Check if the user already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            print(f"User '{username}' already exists. Skipping insertion.")
        else:
            # Insert the new user
            cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            """, (username, password, role))
            conn.commit()
            print(f"User '{username}' added successfully.")
    except sqlite3.Error as e:
        print(f"Error adding user: {e}")

# Initialize the database connection
# conn = sqlite3.connect("users.db", timeout=10, check_same_thread=False)

# Add users only if they don't already exist
# add_user(conn, "adeniyi", generate_password_hash("1379"), "admin")
# add_user(conn, "kelvin", generate_password_hash("1111"), "admin")

# Close the connection after initialization
# conn.close()

# Initialize the database connection
def get_db_connection():
    conn = sqlite3.connect("users.db",timeout=20, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn

# get db connection using sqlalchemy
# Create the SQLAlchemy engine with WAL mode enabled
engine = create_engine("sqlite:///users.db", connect_args={"check_same_thread": False})

# Create a scoped session
db_session = scoped_session(sessionmaker(bind=engine))

def get_db_connection_with_sqlachemy():
    return db_session


Base = declarative_base()

class Record(Base):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False)
    phone_name = Column(String, nullable=False)
    service = Column(String, nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)