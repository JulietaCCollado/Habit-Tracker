from datetime import datetime


class Analytics:
    def __init__(self, habits):
        self.habits = habits

    def get_all_tracked_habits(self):
        """Return a list of all currently tracked habits."""
        return [habit.name for habit in self.habits]

    def get_habits_by_periodicity(self, periodicity):
        """Return a list of habits with the specified periodicity."""
        return [habit.name for habit in self.habits if habit.periodicity == periodicity]

    def get_longest_streak(self):
        """Return the longest run streak of all defined habits."""
        longest_streak = 0
        for habit in self.habits:
            current_streak = 0
            for i in range(1, len(habit.tracking_data)):
                # Calculate the difference between consecutive dates
                time_diff = habit.tracking_data[i] - habit.tracking_data[i - 1]
                # If the difference is exactly one day, increase the streak
                if time_diff.days == 1:
                    current_streak += 1
                else:
                    # If the streak is broken, update the longest streak if needed
                    longest_streak = max(longest_streak, current_streak)
                    # Reset the current streak
                    current_streak = 0
            # Update the longest streak for this habit after iterating through all tracking data
            longest_streak = max(longest_streak, current_streak)
        return longest_streak

    def get_longest_streak_for_habit(self, habit_name):
        """Return the longest run streak for a given habit."""
        habit = None
        for h in self.habits:
            if h.name == habit_name:
                habit = h
                break

        if not habit:
            return 0

        longest_streak = 0
        current_streak = 0
        for i in range(1, len(habit.tracking_data)):
            # Calculate the difference between consecutive dates
            time_diff = habit.tracking_data[i] - habit.tracking_data[i - 1]
            # If the difference is exactly one day, increase the streak
            if time_diff.days == 1:
                current_streak += 1
            else:
                # If the streak is broken, update the longest streak if needed
                longest_streak = max(longest_streak, current_streak)
                # Reset the current streak
                current_streak = 0
        # Update the longest streak for this habit after iterating through all tracking data
        longest_streak = max(longest_streak, current_streak)
        return longest_streak
