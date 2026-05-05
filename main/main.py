import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Файл для избранного
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()

        # GUI компоненты
        self.setup_ui()

        # Загрузка избранных при старте
        self.display_favorites()

    def setup_ui(self):
        # Рамка для поиска
        search_frame = ttk.Frame(self.root, padding="10")
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Поиск пользователя GitHub:").pack(side=tk.LEFT, padx=5)

        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_users())

        search_btn = ttk.Button(search_frame, text="Найти", command=self.search_users)
        search_btn.pack(side=tk.LEFT, padx=5)

        # Рамка для результатов
        results_frame = ttk.LabelFrame(self.root, text="Результаты поиска", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Список результатов
        columns = ("username", "user_id", "url")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)

        self.results_tree.heading("username", text="Имя пользователя")
        self.results_tree.heading("user_id", text="ID")
        self.results_tree.heading("url", text="URL профиля")

        self.results_tree.column("username", width=200)
        self.results_tree.column("user_id", width=100)
        self.results_tree.column("url", width=350)

        # Скроллбар для результатов
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)

        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки под результатами
        results_btn_frame = ttk.Frame(results_frame)
        results_btn_frame.pack(fill=tk.X, pady=5)

        add_fav_btn = ttk.Button(results_btn_frame, text="Добавить в избранное", command=self.add_to_favorites)
        add_fav_btn.pack(side=tk.LEFT, padx=5)

        # Рамка для избранного
        favorites_frame = ttk.LabelFrame(self.root, text="Избранные пользователи", padding="10")
        favorites_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Список избранных
        fav_columns = ("username", "user_id", "url", "added_date")
        self.favorites_tree = ttk.Treeview(favorites_frame, columns=fav_columns, show="headings", height=6)

        self.favorites_tree.heading("username", text="Имя пользователя")
        self.favorites_tree.heading("user_id", text="ID")
        self.favorites_tree.heading("url", text="URL профиля")
        self.favorites_tree.heading("added_date", text="Дата добавления")

        self.favorites_tree.column("username", width=150)
        self.favorites_tree.column("user_id", width=80)
        self.favorites_tree.column("url", width=280)
        self.favorites_tree.column("added_date", width=120)

        # Скроллбар для избранных
        fav_scrollbar = ttk.Scrollbar(favorites_frame, orient=tk.VERTICAL, command=self.favorites_tree.yview)
        self.favorites_tree.configure(yscrollcommand=fav_scrollbar.set)

        self.favorites_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        fav_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки для избранного
        fav_btn_frame = ttk.Frame(favorites_frame)
        fav_btn_frame.pack(fill=tk.X, pady=5)

        remove_fav_btn = ttk.Button(fav_btn_frame, text="Удалить из избранного", command=self.remove_from_favorites)
        remove_fav_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(fav_btn_frame, text="Очистить избранное", command=self.clear_favorites)
        clear_btn.pack(side=tk.LEFT, padx=5)

    def search_users(self):
        """Поиск пользователей на GitHub"""
        query = self.search_entry.get().strip()

        # Проверка корректности ввода
        if not query:
            messagebox.showwarning("Предупреждение", "Поле поиска не должно быть пустым!")
            return

        # Очистка предыдущих результатов
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        try:
            # Запрос к GitHub API
            url = f"https://api.github.com/search/users?q={query}&per_page=20"
            headers = {"Accept": "application/vnd.github.v3+json"}
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                users = data.get("items", [])

                if not users:
                    messagebox.showinfo("Информация", "Пользователи не найдены")
                    return

                for user in users:
                    self.results_tree.insert("", tk.END, values=(
                        user["login"],
                        user["id"],
                        user["html_url"]
                    ))
            else:
                messagebox.showerror("Ошибка", f"Ошибка API: {response.status_code}")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка подключения: {str(e)}")

    def load_favorites(self):
        """Загрузка избранных из JSON файла"""
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_favorites(self):
        """Сохранение избранных в JSON файл"""
        with open(self.favorites_file, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)

    def add_to_favorites(self):
        """Добавление выбранного пользователя в избранное"""
        selected = self.results_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из результатов поиска")
            return

        for item in selected:
            values = self.results_tree.item(item, "values")
            username = values[0]
            user_id = values[1]
            url = values[2]

            # Проверка, не добавлен ли уже пользователь
            if any(fav["username"] == username for fav in self.favorites):
                messagebox.showinfo("Информация", f"Пользователь {username} уже в избранном")
                continue

            favorite = {
                "username": username,
                "user_id": user_id,
                "url": url,
                "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.favorites.append(favorite)

        self.save_favorites()
        self.display_favorites()
        messagebox.showinfo("Успех", "Пользователь(и) добавлен(ы) в избранное")

    def display_favorites(self):
        """Отображение избранных пользователей"""
        for item in self.favorites_tree.get_children():
            self.favorites_tree.delete(item)

        for fav in self.favorites:
            self.favorites_tree.insert("", tk.END, values=(
                fav["username"],
                fav["user_id"],
                fav["url"],
                fav.get("added_date", "Не указана")
            ))

    def remove_from_favorites(self):
        """Удаление выбранного пользователя из избранного"""
        selected = self.favorites_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из избранного")
            return

        for item in selected:
            values = self.favorites_tree.item(item, "values")
            username = values[0]

            self.favorites = [fav for fav in self.favorites if fav["username"] != username]

        self.save_favorites()
        self.display_favorites()
        messagebox.showinfo("Успех", "Пользователь(и) удален(ы) из избранного")

    def clear_favorites(self):
        """Очистка всего списка избранного"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить всех пользователей из избранного?"):
            self.favorites = []
            self.save_favorites()
            self.display_favorites()
            messagebox.showinfo("Успех", "Избранное очищено")

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
