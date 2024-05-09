import sqlite3
import os
from datetime import datetime, timedelta


def generate_tracking_dates(periodicity):
    """ Generate predefined tracking dates for habits based on their periodicity """
    if periodicity == 1:  # Daily habit
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Track for the last 30 days
        tracking_dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(31)]
    else:  # Weekly habit
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Track for the last 30 days
        tracking_dates = [(start_date + timedelta(weeks=i)).strftime('%Y-%m-%d') for i in range(5)]  # 5 weeks
    return tracking_dates


def close_connection(conn):
    """ Close the database connection """
    if conn:
        conn.close()


class Database:
    def __init__(self, db_file):
        self.db_file = db_file

    def execute(self, sql):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def initialize_database(self):
        try:
            if os.path.exists(self.db_file):
                print("Database file already exists. Deleting existing data...")

            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM habit_tracking")
            cursor.execute("DELETE FROM habit_type")
            cursor.execute("DELETE FROM habits")
            cursor.execute("DELETE FROM users")

            # Create tables if they don't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    email TEXT NOT NULL,
                                    username TEXT NOT NULL,
                                    password TEXT NOT NULL,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS habits (
                       user_id INTEGER NOT NULL,
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL,
                       description TEXT NOT NULL,
                       periodicity TEXT NOT NULL,
                       creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (user_id) REFERENCES users(id)
                   )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS habit_tracking (
                                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                                   habit_id INTEGER NOT NULL,
                                   checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                   FOREIGN KEY (habit_id) REFERENCES habits(id)
                               )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS habit_type (
                                   id INTEGER PRIMARY KEY,
                                   description TEXT NOT NULL,
                                   frequency INTEGER NOT NULL
                                )''')

            # Commit changes and close connection
            conn.commit()
            conn.close()

            return "Database initialized successfully"
        except sqlite3.Error as e:
            return f"Error initializing database: {e}"

    def populate_tables(self):
        """ Add admin user, add habit types: daily, weekly, add 6 habits for admin user"""
        try:
            # Check if data already exists
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]

            if count > 0:
                print("Data already exists in the tables. Skipping population.")
                return

            # Insert admin user
            sql = '''INSERT INTO users(email,username,password,created_at)
                     VALUES('admin@gmail.com','admin','admin',strftime('%s','now'));'''
            cursor.execute(sql)

            # Insert habit types
            sql = '''INSERT INTO habit_type(id,description,frequency)
                     VALUES(1,'daily',1);'''
            cursor.execute(sql)
            sql = '''INSERT INTO habit_type(id,description,frequency)
                     VALUES(2,'weekly',7);'''
            cursor.execute(sql)

            # Insert habits
            habit_data = [
                ('Drink 1 lt of water', 'Drink 1 liter of water every day', 1),
                ('Walk 30 minutes', 'Walk 30 minutes every day', 1),
                ('Read 20 pages', 'Read 20 pages of a book every day', 1),
                ('Go to the pub', 'Go to the pub with friends every week', 2),
                ('Swim', 'Swim every week', 2),
                ('Have a shower', 'Have a shower every day', 1)
            ]

            for name, description, periodicity in habit_data:
                cursor.execute('''INSERT INTO habits(name, description, creation_date, user_id, periodicity)
                                  VALUES(1, ?,?, ?, strftime('%s','now'))''',
                               (name, description, periodicity))

                # Get the habit_id of the inserted habit
                habit_id = cursor.lastrowid

                # Generate predefined tracking data for each habit
                tracking_dates = generate_tracking_dates(periodicity)
                for checked_at in tracking_dates:
                    cursor.execute('''INSERT INTO habit_tracking (habit_id, checked_at)
                                      VALUES(?, ?)''',
                                   (habit_id, checked_at))

            conn.commit()
            conn.close()

            print("Tables populated successfully.")
        except sqlite3.Error as e:
            print(f"Error populating tables: {e}")

    def get_habits_by_user_id(self, user_id):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM habits WHERE user_id=?", (user_id,))
            habits = cursor.fetchall()
            conn.close()
            return habits
        except sqlite3.Error as e:
            print(f"Error getting habits by user ID: {e}")
            return []

    def get_habit_tracking_by_habit_id(self, habit_id):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM habit_tracking WHERE habit_id=?", (habit_id,))
            tracking = cursor.fetchall()
            conn.close()
            return tracking
        except sqlite3.Error as e:
            print(f"Error getting habit tracking by habit ID: {e}")
            return []

    def create_connection(self):
        """ Create a database connection to the SQLite database specified by db_file """
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except sqlite3.Error as e:
            print(e)
            return None

    def init_db(self):
        """ Initialize the database """
        print("Initializing database...")
        conn = self.create_connection()
        if conn is not None:
            self.populate_tables()
            close_connection(conn)
            print("Database initialized successfully")


# Example usage:
if __name__ == "__main__":
    db = Database("main_db.db")
    db.initialize_database()
    db.init_db()