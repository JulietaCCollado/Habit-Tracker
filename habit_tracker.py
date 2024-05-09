import sqlite3
from datetime import datetime, timedelta
from database import Database
from habit import Habit


class HabitTracker:
    def __init__(self, user_id, db_file):
        self.user_id = user_id
        self.db_file = db_file

    def get_habit_tracking_by_id(self, habit_id):
        query = "SELECT * FROM habit_tracking WHERE habit_id = ?"
        parameters = (habit_id,)
        return self._execute_query(query, parameters)

    def _execute_query(self, query, parameters=None):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def create_habit(self, user_id, name, description, periodicity):
        habit = Habit(user_id, name, description, periodicity, self.db_file)
        return habit.create_habit(user_id, name, description, periodicity)

    def get_habit_info(self, name):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT id, user_id, name, description, periodicity, creation_date FROM habits WHERE name=?",
                           (name,))
            habit_info = cursor.fetchone()
            conn.close()
            return habit_info
        except sqlite3.Error as e:
            return f"Error getting habit info: {e}"

    def update_habit(self, name, new_name=None, new_description=None, new_periodicity=None):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            update_query = "UPDATE habits SET"
            update_values = []
            if new_name:
                update_query += " name=?,"
                update_values.append(new_name)
            if new_description:
                update_query += " description=?,"
                update_values.append(new_description)
            if new_periodicity:
                update_query += " periodicity=?,"
                update_values.append(new_periodicity)
            # Remove the trailing comma and add the condition for the WHERE clause
            update_query = update_query.rstrip(",") + " WHERE name=?"
            update_values.append(name)
            cursor.execute(update_query, tuple(update_values))
            conn.commit()
            conn.close()
            return "Habit updated successfully"
        except sqlite3.Error as e:
            return f"Error updating habit: {e}"

    def remove_habit(self, name):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM habits WHERE name=?", (name,))
            conn.commit()
            conn.close()
            return "Habit removed successfully"
        except sqlite3.Error as e:
            return f"Error removing habit: {e}"

    def get_all_habits(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM habits")
            all_habits = cursor.fetchall()
            conn.close()
            return all_habits
        except sqlite3.Error as e:
            return f"Error getting all habits: {e}"

    def mark_habit_as_done(self, user_id, name):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO habit_tracking (habit_id, checked_at) "
                           "SELECT id, ? FROM habits WHERE name=? AND user_id=?",
                           (current_time, name, self.user_id))
            conn.commit()
            conn.close()
            return "Habit marked as done successfully"
        except sqlite3.Error as e:
            return f"Error marking habit as done: {e}"

    def get_worst_streak_habit(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # Select the habit with the worst streak
            cursor.execute("""
                SELECT name FROM habits WHERE id = (
                    SELECT habit_id FROM habit_tracking
                    GROUP BY habit_id
                    ORDER BY COUNT(*) ASC
                    LIMIT 1
                )
            """)

            habit = cursor.fetchone()
            conn.close()
            return habit[0] if habit else None
        except sqlite3.Error as e:
            return f"Error getting habit with worst streak: {e}"

    def get_worst_habit_last_month(self):
        try:
            last_month = datetime.now() - timedelta(days=30)
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM habits WHERE id = (
                    SELECT habit_id FROM habit_tracking 
                    WHERE checked_at >= ? 
                    GROUP BY habit_id 
                    ORDER BY COUNT(*) DESC 
                    LIMIT 1
                )
            """, (last_month,))
            habit = cursor.fetchone()
            conn.close()
            return habit[0] if habit else None
        except sqlite3.Error as e:
            return f"Error getting worst habit last month: {e}"

    def calculate_streak(self, habit_tracking):
        """ Calculate the longest streak and its date range for a habit.

        Args:
            habit_tracking (list): A list of dictionaries representing habit tracking entries.

        Returns:
            tuple: A tuple containing the longest streak, the start date, and the end date.

        """
        if not habit_tracking:
            return 0, None, None

        longest_streak = current_streak = 1
        longest_start = longest_end = current_start = habit_tracking[0]["checked_at"]
        previous_day = current_start

        for tracking in habit_tracking[1:]:
            if tracking["checked_at"] - previous_day == timedelta(days=1):
                current_streak += 1
                if current_streak > longest_streak:
                    longest_streak = current_streak
                    longest_start = current_start
                    longest_end = tracking["checked_at"]
            else:
                current_streak = 1
                current_start = tracking["checked_at"]

            previous_day = tracking["checked_at"]

        return longest_streak, longest_start, longest_end

    def get_habits_with_longest_streak(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute("SELECT id, name, description, periodicity, creation_date FROM habits")
            habits = cursor.fetchall()

            habit_streaks = []

            for habit in habits:
                habit_id, name, description, periodicity, created_at = habit
                cursor.execute("""
                    SELECT checked_at FROM habit_tracking 
                    WHERE habit_id = ?
                    ORDER BY checked_at
                """, (habit_id,))

                habit_tracking = cursor.fetchall()

                if habit_tracking:
                    habit_tracking = [
                        {"checked_at": datetime.fromisoformat(check_in[0])}
                        for check_in in habit_tracking
                    ]

                    streak_length, start_date, end_date = self.calculate_streak(habit_tracking)

                    if streak_length > 0:
                        habit_streaks.append((
                            habit_id, name, description, periodicity,
                            created_at, streak_length, start_date, end_date
                        ))

            habit_streaks.sort(key=lambda x: x[1], reverse=True)

            conn.close()

            return habit_streaks

        except Exception as e:
            print(f"An error occurred while getting habits with longest streak: {e}")
            return []
