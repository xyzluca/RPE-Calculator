import pandas as pd
from rpe_percentages import rpe_chart
import os

class RPEScript:
    def __init__(self, rpe_chart):
        self.rpe_chart = rpe_chart

    def calculate(self, reps, rpe, weight_kg):
        rpe = int(rpe)
        if reps in self.rpe_chart and rpe in self.rpe_chart[reps]:
            e1rm_percentage = self.rpe_chart[reps][rpe]
            e1rm_value = weight_kg / (e1rm_percentage / 100.0)
            return e1rm_value
        else:
            return None

def compare_with_dataset(e1rm_value, dataset, lift_type, age, weight_class):
    lift_column = {
        "Squat": "Best3SquatKg",
        "Bench": "Best3BenchKg",
        "Deadlift": "Best3DeadliftKg",
    }.get(lift_type)
    if not lift_column:
        return "Comparison not available"

    if age.is_integer():
        dataset = dataset[(dataset["Age"] == age) | (dataset["Age"] == age + 0.5)]
    else:
        possible_ages = [int(age), int(age) + 1]
        dataset = dataset[dataset["Age"].isin(possible_ages)]

    if "+" in weight_class:
        weight_limit = float(weight_class.replace("+", ""))
        dataset = dataset[dataset["WeightClassKg"] > weight_limit]
    else:
        weight_limit = float(weight_class)
        dataset = dataset[dataset["WeightClassKg"] <= weight_limit]

    lifters_above_user = dataset[dataset[lift_column] > e1rm_value][lift_column].count()
    total_lifters = dataset[lift_column].count()
    percentile = (
        (1 - (lifters_above_user / total_lifters)) * 100 if total_lifters else 0
    )
    percentile_text = f"You're in the top {100 - percentile:.2f}% of lifters"
    return percentile_text

class App:
    def __init__(self):
        self.dataset = pd.read_csv("openpowerliftingdata.csv", low_memory=False)
        self.dataset["WeightClassKg"] = pd.to_numeric(self.dataset["WeightClassKg"], errors="coerce")
        self.dataset = self.dataset[self.dataset["Tested"] == "Yes"]

    def calculate_e1rm(self, reps, rpe, weight_kg, age, weight_class, sex, lift_type):
        rpe_script = RPEScript(rpe_chart)
        e1rm_value = rpe_script.calculate(reps, rpe, weight_kg)
        if e1rm_value is not None:
            e1rm_rounded = round(e1rm_value / 2.5) * 2.5
            formatted_e1rm = (
                "{:.1f}".format(e1rm_rounded)
                if e1rm_rounded % 1
                else "{:.0f}".format(e1rm_rounded)
            )
            percentile_text = compare_with_dataset(
                e1rm_rounded, self.dataset, lift_type, age, weight_class
            )
            result_text = f"{sex} {lift_type} E1RM = {formatted_e1rm} kg\n{percentile_text}"
        else:
            result_text = "Invalid input"
        return result_text

if __name__ == "__main__":
    app = App()
    result = app.calculate_e1rm(5, 8, 100, 30, "90+", "Male", "Squat")
    print(result)
