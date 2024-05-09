import sqlite3
from datetime import datetime, timedelta


class User:
    def __init__(self, user_id, email, username, password, created_at):
        self.user_id = user_id
        self.email = email
        self.username = username
        self.password = password
        self.created_at = created_at
        self.habits = []

    def add_habit(self, habit):
        self.habits.append(habit)

    def remove_habit(self, habit):
        self.habits.remove(habit)

    def get_all_habits(self):
        return self.habits


class Habit:
    def __init__(self, user_id,  name, description, periodicity, db_file):
        self.user_id = user_id
        self.name = name
        self.description = description
        self.periodicity = periodicity
        self.creation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.tracking_data = []
        self.db_file = db_file

    def create_habit(self, user_id, name, description, periodicity):
        try:
            # Connect to the database
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # Ensure that the 'user_id' column exists in the 'habits' table
            cursor.execute("PRAGMA table_info(habits)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'user_id' not in columns:
                cursor.execute("ALTER TABLE habits ADD COLUMN user_id INTEGER")

            # Insert the habit into the database
            cursor.execute("INSERT INTO habits (user_id, name, description, periodicity, creation_date) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
                           (user_id, name, description, periodicity))

            # Commit the transaction and close the connection
            conn.commit()
            conn.close()

            return "Habit created successfully"
        except sqlite3.Error as e:
            return f"Error creating habit: {e}"

    def check_off_task(self):
        completed_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.tracking_data.append(completed_time)

    def calculate_habit_streak(self):
        if not self.tracking_data:
            return 0

        self.tracking_data.sort()
        current_streak = 1
        longest_streak = 1

        for i in range(1, len(self.tracking_data)):
            time_diff = datetime.strptime(self.tracking_data[i], '%Y-%m-%d %H:%M:%S') - \
                        datetime.strptime(self.tracking_data[i - 1], '%Y-%m-%d %H:%M:%S')

            if time_diff == timedelta(days=1) or time_diff == timedelta(weeks=1):
                current_streak += 1
            else:
                current_streak = 1

            if current_streak > longest_streak:
                longest_streak = current_streak

        return longest_streak

    def retrieve_tracking_data(self):
        return self.tracking_data

    def check_habit_status(self):
        if not self.tracking_data:
            return "No tracking data available"

        last_tracking_date = datetime.strptime(self.tracking_data[-1], '%Y-%m-%d %H:%M:%S')
        time_since_last_tracking = datetime.now() - last_tracking_date

        if self.periodicity == "daily":
            periodicity_days = 1
        elif self.periodicity == "weekly":
            periodicity_days = 7
        else:
            return "Invalid periodicity"

        if time_since_last_tracking <= timedelta(days=periodicity_days):
            return "Habit is on track"
        else:
            return "Habit needs to be tracked"

    def update_habit_information(self, new_name=None, new_description=None, new_periodicity=None):
        if new_name:
            self.name = new_name
        if new_description:
            self.description = new_description
        if new_periodicity:
            self.periodicity = new_periodicity

    def delete_habit(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM habits WHERE name=?", (self.name,))
            conn.commit()
            conn.close()
            self.name = None
            self.description = None
            self.periodicity = None
            self.creation_date = None
            self.tracking_data = None
            return "Habit deleted successfully"
        except sqlite3.Error as e:
            return f"Error deleting habit: {e}"

    def __str__(self):
        return f"Habit: {self.name}, Description: {self.description}, Periodicity: {self.periodicity}"
