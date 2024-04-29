import pandas as pd
import customtkinter as ctk
from tkinter import messagebox
from rpe_percentages import rpe_chart
import os

# Importiert benötigte Bibliotheken und Module.
print("Aktuelles Arbeitsverzeichnis:", os.getcwd())


# Gibt an von wo main.py ausgeführt wird
class RPEScript:
    def __init__(self, rpe_chart):
        # Konstruktor
        self.rpe_chart = rpe_chart
        # übergebenes Dictionary, enthält RPE Werte

    def calculate(self, reps, rpe, weight_kg):
        # Berechnet E1RM auf Basis von Benutzereingabe
        # reps = Wdh.
        # rpe = Rate of Perceived Exertion (Subjektiv)
        # weight_kg = Gewicht in kg
        rpe = int(rpe)  # RPE zu int
        # Überprüft ob reps und rpe in rpe_chart vorhanden sind
        if reps in self.rpe_chart and rpe in self.rpe_chart[reps]:
            # Berechnet Prozentsatz des E1RM
            e1rm_percentage = self.rpe_chart[reps][rpe]
            # Berechnet E1RM Wert und gibt aus
            e1rm_value = weight_kg / (e1rm_percentage / 100.0)
            return e1rm_value
        else:
            # Gibt None zurück wenn reps oder rpe nicht in rpe_chart vorhanden sind
            return None


def compare_with_dataset(e1rm_value, dataset, lift_type, age, weight_class):
    # Vergleicht das berechnete E1RM mit den Daten aus der openpowerliftingdata.csv.
    # e1rm_value = E1RM
    # dataset = Datensatz für Vergleich
    # lift_type = ARt der Übung
    # age = alter
    # weight_class = Gewichtsklasse
    lift_column = {
        # Definiert Zuordnung von Übungsarten zu SPalten im Datensatz
        "Squat": "Best3SquatKg",
        "Bench": "Best3BenchKg",
        "Deadlift": "Best3DeadliftKg",
    }.get(lift_type)
    # Überprüft ob Übungsart vorhanden ist
    if not lift_column:
        return "Comparison not available"

    # Alter und Gewichtsklassen Filterung
    if age.is_integer():
        dataset = dataset[(dataset["Age"] == age) | (dataset["Age"] == age + 0.5)]
    else:
        possible_ages = [int(age), int(age) + 1]
        dataset = dataset[dataset["Age"].isin(possible_ages)]
        # Gewichtsklassen Filterung
    if "+" in weight_class:
        weight_limit = float(weight_class.replace("+", ""))
        dataset = dataset[dataset["WeightClassKg"] > weight_limit]
    else:
        weight_limit = float(weight_class)
        dataset = dataset[dataset["WeightClassKg"] <= weight_limit]

    # Berechnung des Perzentils im Vergleich zu anderen Sportlern aus dem Datensatz
    lifters_above_user = dataset[dataset[lift_column] > e1rm_value][lift_column].count()
    total_lifters = dataset[lift_column].count()
    percentile = (
        (1 - (lifters_above_user / total_lifters)) * 100 if total_lifters else 0
    )
    percentile_text = f"You're in the top {100 - percentile:.2f}% of lifters"
    return percentile_text


class App(ctk.CTk):
    # Definiert die GUI-Elemente und deren Funktionalitäten, wie Dropdown-Menüs, Eingabefelder und Buttons. Implementiert die Logik für die Berechnung und Anzeige des E1RM sowie den Vergleich mit den Powerlifting-Daten.

    def __init__(self):
        super().__init__()
        self.title("E1RM Rechner")
        self.geometry("800x600")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.dataset = pd.read_csv("openpowerliftingdata.csv", low_memory=False)

        # Konvertiert 'WeightClassKg' zu float
        self.dataset["WeightClassKg"] = pd.to_numeric(
            self.dataset["WeightClassKg"], errors="coerce"
        )

        # Filtert Datensatz
        self.dataset = self.dataset[self.dataset["Tested"] == "Yes"]

        # Main Frame
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Layout
        main_frame.grid_columnconfigure((0, 3), weight=1)
        main_frame.grid_columnconfigure((1, 2), weight=2)
        for i in range(8):
            main_frame.grid_rowconfigure(i, weight=1)
        # Geschlecht
        self.male_female_combobox = ctk.CTkComboBox(
            main_frame, values=["Male", "Female", "Neutral"]
        )
        self.male_female_combobox.grid(
            row=0, column=1, columnspan=2, pady=10, sticky="ew"
        )
        self.male_female_combobox.set("Male")
        # Überschrift
        self.e1rm_label = ctk.CTkLabel(
            main_frame, text="E1RM Rechner", font=("Helvetica", 20, "normal")
        )
        self.e1rm_label.grid(row=1, column=1, columnspan=2)
        # Übungsauswahl
        self.lift_type_combobox = ctk.CTkComboBox(
            main_frame, values=["Squat", "Bench", "Deadlift"]
        )
        self.lift_type_combobox.grid(
            row=2, column=1, columnspan=2, pady=10, sticky="ew"
        )
        self.lift_type_combobox.set("Squat")
        # Wiederholungen
        self.reps_entry = ctk.CTkEntry(main_frame, placeholder_text="Wiederholungen")
        self.reps_entry.grid(row=3, column=1, pady=5, sticky="ew")
        # RPE
        self.rpe_entry = ctk.CTkEntry(main_frame, placeholder_text="RPE")
        self.rpe_entry.grid(row=3, column=2, pady=5, sticky="ew")
        # Gewicht
        self.weight_entry = ctk.CTkEntry(main_frame, placeholder_text="Gewicht (kg)")
        self.weight_entry.grid(row=4, column=1, columnspan=2, pady=5, sticky="ew")
        self.weight_entry.insert(0, "100")

        self.age_entry = ctk.CTkEntry(
            main_frame, placeholder_text="Alter (ggf. mit .5 für approximativ)"
        )
        self.age_entry.grid(row=5, column=1, pady=5, sticky="ew")

        self.weight_class_entry = ctk.CTkEntry(
            main_frame, placeholder_text="Gewichtsklasse (z.B. 90, 90+)"
        )
        self.weight_class_entry.grid(row=5, column=2, pady=5, sticky="ew")
        # Calculate Button
        self.calculate_button = ctk.CTkButton(
            main_frame, text="Berechnen", command=self.calculate_e1rm
        )
        self.calculate_button.grid(row=6, column=1, columnspan=2, pady=10, sticky="ew")
        # Schrift
        self.result_label = ctk.CTkLabel(
            main_frame, text="", font=("Helvetica", 14, "bold")
        )
        self.result_label.grid(row=7, column=1, columnspan=2)

        self.rpe_script = RPEScript(rpe_chart)
        # Hilfe
        self.help_button = ctk.CTkButton(
            main_frame, text="Hilfe", command=self.show_help
        )
        self.help_button.grid(row=8, column=1, pady=10, sticky="ew")

    def show_help(self):
        # Öffnet Hilfe Fenster mit Erklärung siehe Unten
        help_window = ctk.CTkToplevel(self)
        help_window.title("Hilfe")
        help_window.geometry("400x300")

        help_window.grab_set()

        help_text = """
        Anleitung:
        - Wiederholungen: Anzahl der ausgeführten Wiederholungen.
        - RPE: 'Rate of Perceived Exertion', ein Maß für die Anstrengung.
        - Gewicht (kg): Gewicht, das gehoben wird.
        - Alter: Dein Alter.
        - Gewichtsklasse: Deine Gewichtsklasse.

        Wähle deine Angaben und klicke auf 'Berechnen', um deinen E1RM zu sehen.
        """
        help_label = ctk.CTkLabel(help_window, text=help_text, wraplength=350)
        help_label.pack(pady=20, padx=20)

    def calculate_e1rm(self):
        # E1RM Rechnungsdurchführung
        try:
            # Eingaben aus GUI holen
            sex = self.male_female_combobox.get()  # Geschlecht
            lift_type = self.lift_type_combobox.get()  # Übung
            reps = int(self.reps_entry.get())  # Reps
            rpe = float(self.rpe_entry.get())  # RPE
            weight_kg = float(self.weight_entry.get())  # Weight
            # Berechnet E1RM mit RPEScript-Klasse
            e1rm_value = self.rpe_script.calculate(reps, rpe, weight_kg)
            if e1rm_value is not None:
                # Prüft auf gültigen E1RM Wert
                e1rm_rounded = round(e1rm_value / 2.5) * 2.5
                # Rundet Wert auf nächste Vielfache von 2,5
                formatted_e1rm = (
                    # Formatiert E1RM Wert für Output in GUI
                    "{:.1f}".format(e1rm_rounded)
                    if e1rm_rounded % 1
                    else "{:.0f}".format(e1rm_rounded)
                )
                # Mehr Benutzerangaben für Leistungsvergleich
                age = float(self.age_entry.get())
                weight_class = self.weight_class_entry.get()
                # Führt Vergleich aus und gibt Text für Prozentil-Ausgabe
                percentile_text = compare_with_dataset(
                    e1rm_rounded, self.dataset, lift_type, age, weight_class
                )
                # Aktualisiert Label mit E1RM und Vergleichstext
                self.result_label.configure(
                    text=f"{sex} {lift_type} E1RM = {formatted_e1rm} kg\n{percentile_text}"
                )
            else:
                # Falls kein gültiger E1RM = Fehlermeldung
                self.result_label.configure(text="Invalid input")
        except ValueError as e:
            # Fehldermeldung für EIngabeverarbeitungsfehler
            messagebox.showerror("Invalid Input", f"Invalid input: {e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
