import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime

class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.file_name = "weather_data.json"
        self.data = self.load_data()

        # Поля ввода
        tk.Label(root, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0)
        self.entry_date = tk.Entry(root)
        self.entry_date.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.entry_date.grid(row=0, column=1)

        tk.Label(root, text="Температура (°C):").grid(row=1, column=0)
        self.entry_temp = tk.Entry(root)
        self.entry_temp.grid(row=1, column=1)

        tk.Label(root, text="Описание:").grid(row=2, column=0)
        self.entry_desc = tk.Entry(root)
        self.entry_desc.grid(row=2, column=1)

        tk.Label(root, text="Осадки:").grid(row=3, column=0)
        self.precip_var = tk.StringVar(value="Нет")
        ttk.Combobox(root, textvariable=self.precip_var, values=["Да", "Нет"], state="readonly").grid(row=3, column=1)

        # Кнопки
        tk.Button(root, text="Добавить запись", command=self.add_entry).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Фильтры
        tk.Label(root, text="Фильтр (Т-ра выше):").grid(row=5, column=0)
        self.filter_temp = tk.Entry(root)
        self.filter_temp.grid(row=5, column=1)
        tk.Button(root, text="Применить фильтр", command=self.update_table).grid(row=6, column=0, columnspan=2)

        # Таблица
        self.tree = ttk.Treeview(root, columns=("Дата", "Темп", "Описание", "Осадки"), show='headings')
        for col in ("Дата", "Темп", "Описание", "Осадки"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

        self.update_table()

    def validate_input(self, date, temp, desc):
        try:
            datetime.strptime(date, "%d.%m.%Y")
            float(temp)
            if not desc.strip(): raise ValueError
            return True
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте формат даты (ДД.ММ.ГГГГ), температуры (число) и описание.")
            return False

    def add_entry(self):
        date = self.entry_date.get()
        temp = self.entry_temp.get()
        desc = self.entry_desc.get()
        precip = self.precip_var.get()

        if self.validate_input(date, temp, desc):
            self.data.append({"date": date, "temp": float(temp), "desc": desc, "precip": precip})
            self.save_data()
            self.update_table()
            messagebox.showinfo("Успех", "Запись добавлена!")

    def save_data(self):
        with open(self.file_name, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def load_data(self):
        if os.path.exists(self.file_name):
            with open(self.file_name, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        f_temp = self.filter_temp.get()
        for entry in self.data:
            if f_temp and entry["temp"] <= float(f_temp):
                continue
            self.tree.insert("", "end", values=(entry["date"], entry["temp"], entry["desc"], entry["precip"]))

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()
