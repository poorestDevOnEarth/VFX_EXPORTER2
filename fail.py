import tkinter as tk

root = tk.Tk()

# Beispielobjekt mit Subobjekten
main_object = {
    "property1": "Wert 1",
    "property2": {
        "subproperty1": "Unterwert 1",
        "subproperty2": "Unterwert 2"
    },
    "property3": "Wert 3"
}

# Funktion zum Rekursiven Drucken des Objekts mit Einrückungen
def print_object(obj, indent=0):
    for key, value in obj.items():
        if isinstance(value, dict):
            # Wenn der Wert ein Subobjekt ist, rufen Sie die Funktion rekursiv auf
            print_object(value, indent + 1)
        else:
            # Andernfalls drucken Sie den Schlüssel-Wert-Paar mit Einrückung
            print("  " * indent + f"{key}: {value}")

# Anzeigen des eingerückten Texts in einem Label
text = tk.Text(root, wrap="word", height=10, width=40)
text.pack()

# Drucken Sie das Objekt in das Textfeld
text.insert(tk.END, "Hauptobjekt:\n")
print_object(main_object, indent=1)
text.config(state=tk.DISABLED)  # Deaktivieren Sie die Bearbeitung des Textfelds

root.mainloop()
