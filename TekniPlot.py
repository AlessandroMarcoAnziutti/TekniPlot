import matplotlib.pyplot as plt
import pyodbc
import pandas as pd
import tkinter as tk
from tkinter import filedialog


# Inizio GUI
def on_button_click():
    batch = int(entry_batch.get())
    toll = float(entry_toll.get())

    # Ottieni il file del database dal campo di testo
    file_db = entry_file.get()

    # Verifica che un file sia stato selezionato
    if not file_db:
        print("Error: no file selected!")
        return

    try:
        # connection with the database
        conn = pyodbc.connect(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + file_db)

        # Asks for all readings
        sql = """SELECT Packages.Progressive, Batch, Average, DateTime FROM Packages LEFT JOIN Readings ON Packages.[Progressive] = Readings.[Progressive] WHERE Packages.Batch = ?;"""
        df = pd.read_sql_query(sql, conn, params=[batch])

        # Asks for the progressive number and the first time they appear in terms of daytime
        sql = """SELECT Readings.Progressive, min(DateTime) AS [first] FROM Readings LEFT JOIN Packages ON Readings.[Progressive] = Packages.[Progressive] WHERE Batch = ? GROUP BY Readings.Progressive;"""
        bobine = pd.read_sql(sql, conn, params=[batch])

        # Asks for the Nominal Value of the product
        sql = """SELECT DISTINCT NominalValue FROM Packages WHERE Batch = ?;"""
        nominal_value = pd.read_sql(sql, conn, params=[batch])

        # Collects the readings
        average = df['Average'].tolist()
        datetime = df['DateTime'].tolist()

        # Collects the time of the progressive number
        progressive = bobine['Progressive'].tolist()
        time = bobine['first'].tolist()

        # Collects the nominal value of the product from the batch
        nominal_value = nominal_value.iloc[0, 0]  # Prendi il primo valore della colonna

        # Calculation of the limits
        inf_limit = nominal_value - toll
        sup_limit = nominal_value + toll

        # Plot
        plt.figure(figsize=(80, 30))
        plt.plot(datetime, average, color='black')
        plt.ylim(sup_limit + toll, inf_limit - toll)
        plt.axhline(y=inf_limit, color='r', linestyle='--', label=inf_limit)
        plt.axhline(y=sup_limit, color='g', linestyle='--', label=sup_limit)
        for index, value in enumerate(progressive):
            if index % 10 == 0:
                plt.axvline(x=time[index], color='red', linestyle='solid')
            else:
                plt.axvline(x=time[index], color='b', linestyle='--')
        plt.xlabel('Tempo')
        plt.ylabel('Misurazione')
        plt.legend()
        plt.grid(False)
        plt.show()

    except Exception as e:
        # throws an axception if the database fails to connect
        print(f"Error during the connection with the database: {e}")


# Selection of the file
def load_file():
    file_path = filedialog.askopenfilename(title="Seleziona il file del database",
                                           filetypes=[("Microsoft Access Database", "*.mdb;*.accdb")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)


root = tk.Tk()
root.title("Esempio di GUI con Tkinter")
root.geometry("500x300")

label_toll = tk.Label(root, text="Inserisci tolleranza")
label_toll.pack(pady=5)
entry_toll = tk.Entry(root)
entry_toll.pack(pady=10)

label_batch = tk.Label(root, text="Inserisci numero commessa")
label_batch.pack(pady=5)
entry_batch = tk.Entry(root)
entry_batch.pack(pady=10)

label_file = tk.Label(root, text="Seleziona il file del database")
label_file.pack(pady=5)
entry_file = tk.Entry(root, width=50)
entry_file.pack(pady=10)

button_load_file = tk.Button(root, text="Carica file", command=load_file)
button_load_file.pack(pady=5)

button = tk.Button(root, text="Mostra Grafico", command=on_button_click)
button.pack(pady=10)

root.mainloop()
