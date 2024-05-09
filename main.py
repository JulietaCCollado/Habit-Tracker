from datetime import datetime
import questionary
from habit_tracker import HabitTracker
from database import Database
from tabulate import tabulate
from habit import User, Habit
from analytics import Analytics


def main():
    db = Database("main_db.db")
    db.initialize_database()
    db.populate_tables()
    user_logged_in = User(1, "user@example.com", "username", "password", datetime.now())
    user_id = 1
    habits_to_create = [
        ("Exercise", "Hit the gym.", "daily"),
        ("Reading", "Read for at least 30 minutes.", "weekly"),
        ("Meditation", "Practice mindfulness meditation.", "weekly"),
        ("Writing", "Write in your journal or blog.", "daily"),
        ("Walking", "for at least an hour.", "daily"),
        ("Coffee", "with the friends", "weekly"),
        ("Grocery Shopping", "Write a list", "weekly"),
        ("Clothes Shopping", "Online", "weekly"),
        ("Laundry", "Make appointment", "weekly"),
        ("Look for a job", "at least for an hour.", "daily")
    ]

    for habit_data in habits_to_create:
        name, description, periodicity = habit_data
        habit = Habit(user_logged_in.user_id, name, description, periodicity, "main_db.db")
        habit.create_habit(user_logged_in.user_id, name, description, periodicity)
        user_logged_in.add_habit(habit)

    # Creates an instance of HabitTracker
    tracker = HabitTracker(user_logged_in.user_id, "main_db.db")

    # Start an instance of Analytics with the user's habits
    analytics = Analytics(user_logged_in.habits)
    while True:
        choice = questionary.select(
            "Welcome back Admin! What would you like to do?",
            choices=[
                "Add a new habit",
                "Get habit info",
                "Update a habit",
                "Remove a habit",
                "List of all habits",
                "Mark a habit as done",
                "Worst ever streak habit",
                "Last month's worst habit",
                "List of habits with the longest streak",
                "Exit",
            ],
        ).ask()

        if choice == "Add a new habit":
            name = questionary.text("Enter the name of the habit:").ask().title()
            description = questionary.text("Write a short description:").ask().title()
            periodicity = questionary.select(
                "Select the periodicity of the habit:",
                choices=["daily", "weekly"]
            ).ask()
            tracker.create_habit(user_logged_in.user_id, name, description, periodicity)
            print("Habit added successfully!")

        elif choice == "Get habit info":
            name = questionary.text("Enter the name of the habit:").ask()
            habit_info = tracker.get_habit_info(name)
            if habit_info is not None:
                headers = ["User ID", "Habit ID", "Habit Name", "Description", "Periodicity", "Created at"]
                habit_data = [
                    (habit_info[1], habit_info[0], habit_info[2], habit_info[3], habit_info[4], habit_info[5])]
                print(tabulate(habit_data, headers=headers, tablefmt="grid"))
            else:
                print(f"No habit found with name '{name}'")
                print("Habit not found.")

        elif choice == "Update a habit":
            name = questionary.text("Enter the name of the habit to update:").ask()
            new_name = questionary.text("Enter the new name of the habit:").ask()
            new_description = questionary.text("Enter the new description of the habit:").ask()
            new_periodicity = questionary.select(
                "Select the new periodicity of the habit:",
                choices=["daily", "weekly"]
            ).ask()
            tracker.update_habit(name, new_name, new_description, new_periodicity)
            print("Habit updated successfully!")

        elif choice == "Remove a habit":
            name = questionary.text("Enter the name of the habit to remove:").ask()
            tracker.remove_habit(name)
            print("Habit removed successfully!")

        elif choice == "List of all habits":
            all_habits = tracker.get_all_habits()
            headers = ["User ID", "Habit ID", "Habit Name", "Description", "Periodicity", "Created at"]
            habit_data = [(user_logged_in.user_id, habit[0], habit[1], habit[2], habit[3],
                           habit[4], habit[5]) for habit in all_habits]
            print(tabulate(habit_data, headers=headers, tablefmt="grid"))

        elif choice == "Mark a habit as done":
            name = questionary.text("Enter the name of the habit to mark as done:").ask().title()
            tracker.mark_habit_as_done(user_logged_in.user_id, name)
            print("Habit marked as done successfully!")

        elif choice == "Worst ever streak habit":
            worst_streak_habit = tracker.get_worst_streak_habit()
            print("Habit with the worst streak:", worst_streak_habit)

        elif choice == "Last month's worst habit":
            worst_habit_last_month = tracker.get_worst_habit_last_month()
            print("Worst habit of last month:", worst_habit_last_month)

        elif choice == "List of habits with the longest streak":
            habits_with_longest_streak = tracker.get_habits_with_longest_streak()
            headers = ["Habit ID", "Name", "Description", "Periodicity", "Created at", "Streak Length", "Start Date",
                       "End Date"]
            habit_data = []
            for habit in habits_with_longest_streak:
                habit_data.append((habit[0], habit[1], habit[2], habit[3], habit[4], habit[5], habit[6], habit[7]))
            print(tabulate(habit_data, headers=headers, tablefmt="grid"))

        elif choice == "Exit":
            print("Exiting habit tracker...")
            break


if __name__ == "__main__":
    main()
