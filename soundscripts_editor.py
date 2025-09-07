import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from tksheet import Sheet

# Основные константы на чтение
ABOUT_TOOL_VERSION = "0.0.2"
ABOUT_TOOL_NAME = f"Soundscripts Editor v{ABOUT_TOOL_VERSION}"
ABOUT_TOOL_DESCRIPTION = "This tool helps to edit soundscripts files used on Source Engine."
ABOUT_TOOL_AUTHOR = "Shitcoded by Ambiabstract (Sergey Shavin)."
ABOUT_TOOL_REQUESTED = "Requested by Aptekarr."
ABOUT_TOOL_LINK = "Github: https://github.com/Ambiabstract/soundscripts_editor"
ABOUT_TOOL_DISCORD = "Discord: @Ambiabstract"
WINDOW_SIZE = "1024x720"
COLUMN_WIDTHS = [(0, 200), (1, 100), (2, 100), (3, 100), (4, 100), (5, 385)]
HEADERS = ["entry.name", "channel", "soundlevel", "volume", "pitch", "sounds"]
DEFAULT_CHANNEL = "CHAN_AUTO"
DEFAULT_SOUNDLEVEL = "SNDLVL_NORM"
DEFAULT_VOLUME = "VOL_NORM"
DEFAULT_PITCH = "PITCH_NORM"
CACHE_PATH = "soundscripts_editor_cache.json"

class App(TkinterDnD.Tk):
    # Конструктор класса - метод, который задаёт начальное состояние объекта сразу после его создания
    def __init__(self):
        super().__init__() # вызывает конструктор родительского класса TkinterDnD.Tk чтобы всё работало
        
        # Основные переменные класса
        self.title(f"{ABOUT_TOOL_NAME}")
        self.geometry(WINDOW_SIZE)
        self.resizable(False, False)
        self.items = []  # ???
        self.gameinfo_path = None
        self.project_name = None

        # Строим визуалочку окна, тулбара, нижней строчки
        self.build_main_ui()

    # Метод для создания основной визуальной части интерфейса (тулбар, кнопки, нижняя часть со статусной надписью)
    def build_main_ui(self):
        # Виджет тулбара
        self.toolbar = ttk.Frame(self, padding=(2, 2, 2, 2)) # слева, сверху, справа, снизу
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Кнопки тулбара
        self.btn_new_ss = ttk.Button(self.toolbar, text="New Soundscript", command=self.about_window, state="disabled")
        self.btn_new_ss.pack(
            side=tk.LEFT, padx=(0, 0)
        )
        self.btn_open_ss = ttk.Button(self.toolbar, text="Open Soundscript", command=self.about_window, state="disabled")
        self.btn_open_ss.pack(
            side=tk.LEFT, padx=(0, 0)
        )
        self.btn_save_ss = ttk.Button(self.toolbar, text="Save Soundscript", command=self.about_window, state="disabled")
        self.btn_save_ss.pack(
            side=tk.LEFT, padx=(0, 0)
        )
        self.btn_add_sounds = ttk.Button(self.toolbar, text="Add Sounds", command=self.about_window, state="disabled")
        self.btn_add_sounds.pack(
            side=tk.LEFT, padx=(0, 0)
        )
        self.btn_set_gi = ttk.Button(self.toolbar, text="Set Gameinfo.txt", command=self.set_gameinfo)
        self.btn_set_gi.pack(
            side=tk.LEFT, padx=(0, 0)
        )
        self.btn_about = ttk.Button(self.toolbar, text="About", command=self.about_window)
        self.btn_about.pack(
            side=tk.RIGHT, padx=(0, 0)
        )
        
        # Анонсируем и размещаем статусную надпись со всякими подсказками
        self.status_var = tk.StringVar(value="Please set up Gameinfo!")
        ttk.Label(self, textvariable=self.status_var, anchor="w", padding=(4, 2)).pack(
            side=tk.BOTTOM, fill=tk.X
        )

    # Метод для создания таблицы
    def build_table_ui(self):
        # Виджет таблицы
        table_frame = ttk.Frame(self, padding=(4, 0, 4, 0))
        table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.sheet = Sheet(
            table_frame,
            headers=HEADERS,
            data=[],
            show_x_scrollbar=False,
            show_y_scrollbar=True,
            height=1, # ?????
            width=1, # ?????
        )
        self.sheet.pack(fill=tk.BOTH, expand=True)

        # Всякие разрешения для таблицы
        try:
            self.sheet.enable_bindings(
                (
                    "single_select",
                    "row_select",
                    "column_select",
                    "drag_select",
                    "copy",
                    "arrowkeys",
                    "right_click_popup_menu",
                    # "rc_select",
                )
            )
            # print(f"Bindings enabled!")
        except Exception as e:
            print(f"Cant enable bindings!")
            print(f"{e}")
            pass

        # Настройка ширины столбцов
        for column, width in COLUMN_WIDTHS:
            self.sheet.column_width(column, width)

        # Бинды на всякие приколы контроля таблицы
        self.sheet.bind("<Double-1>", self.on_double_click)
        # self.sheet.bind("<<SheetModified>>", self.on_sheet_modified)

    # Метод для настройки правил драг н дропа
    def setup_dnd(self):
        # Всё окно должно принимать драг н дропом именно файлы (не текст и не ссылки)*
        self.drop_target_register(DND_FILES)
        
        # Бинды
        self.dnd_bind("<<Drop>>", self.on_drop)
        self.sheet.drop_target_register(DND_FILES) # * - то же самое для виджета таблицы
        self.sheet.dnd_bind("<<Drop>>", self.on_drop)
        self.sheet.dnd_bind("<<DragEnter>>", lambda e: self.status_var.set("debug DragEnter"))
        self.sheet.dnd_bind("<<DragLeave>>", lambda e: self.status_var.set("debug DragLeave"))
        # лямбда с буквой "е" это короче штука которая создаёт заглушечную функцию которая мепняет статусную надпись

    # Метод визуальной перерисовки/апдейта таблицы для разных версий tksheet
    def redraw_sheet(self):
        # Настройка ширины столбцов
        for column, width in COLUMN_WIDTHS:
            self.sheet.column_width(column, width)

        try:
            # Явное обновление заголовков
            if hasattr(self.sheet, "headers"):
                self.sheet.headers(HEADERS)
        except Exception:
            pass
        try:
            # Дефолт для новых версий
            if hasattr(self.sheet, "refresh"):
                self.sheet.refresh()
                return
        except Exception:
            pass
        try:
            # Старые версии
            if hasattr(self.sheet, "redraw"):
                self.sheet.redraw()
                return
        except Exception:
            pass
        # На крайний случай — update_idletasks, чтобы форсировать отрисовку
        self.update_idletasks()
    
    # Метод для обновления данных таблицы (содержания), в конце ещё ссылка на апдейт визуала
    def update_table(self):
        data = []
        print(f"update_table self.items: {self.items}")
        for index, file_info in enumerate(self.items, start=1):
            print(f"index: {index}")
            print(f"file_info: {file_info}")
            
            # Временное
            entry_name = file_info["entry_name"]
            sounds = file_info["sounds"]

            # имя канал саундлевел волюм питч путь
            data.append([entry_name, DEFAULT_CHANNEL, DEFAULT_SOUNDLEVEL, DEFAULT_VOLUME, DEFAULT_PITCH, sounds])
        # У разных версий сигнатура отличается — используем безопасный вызов
        try:
            self.sheet.set_sheet_data(data, redraw=False)
        except TypeError:
            # В старых версиях нет аргументов redraw/*_positions
            self.sheet.set_sheet_data(data)
        
        # Апдейт визуала таблицы
        self.redraw_sheet()
        # Апдейт статусной надписи
        self.status_var.set(f"Строк: {len(self.items)}")

    # Метод для добавления в таблицу файлов которые были кинуты драг н дропом
    def add_files(self, paths):
        files_count = 0
        for path in paths:
            path = os.path.abspath(path)
            name = os.path.basename(path) or path
            self.items.append({"entry_name": name, "sounds": path})
            files_count += 1

        self.update_table()
        self.status_var.set(f"Added {files_count} WAV files." if files_count else f"WAV files not found!")

    # Метод для очистки всех файлов из таблицы
    def clear_all(self):
        if not self.items:
            return
        if messagebox.askyesno("Clear all", "Remove all sounds?"):
            self.items.clear()
            self.update_table()

    # Метод с описанием программы
    def about_window(self):
        about_tool_full = ABOUT_TOOL_NAME + "\n\n" + ABOUT_TOOL_DESCRIPTION + "\n\n" + ABOUT_TOOL_AUTHOR + "\n" + ABOUT_TOOL_REQUESTED + "\n\n" + ABOUT_TOOL_LINK + "\n" + ABOUT_TOOL_DISCORD
        messagebox.showinfo("About", about_tool_full)

    # Универсальный метод для файлового браузера
    def open_files_dialog(self, title, filter_str="All Files (*.*)", start_dir=".", multi=True):
        print(f"open_files_dialog start")
        print(f"self: {self}")
        print(f"title: {title}")
        print(f"filter_str: {filter_str}")
        print(f"start_dir: {start_dir}")
        print(f"multi: {multi}")

        # Система фильтра расширений файлов
        filetypes = []
        if filter_str:
            for f in filter_str.split(";;"):
                parts = f.split("(", 1)
                if len(parts) == 2:
                    desc = parts[0].strip()
                    patterns = parts[1].rstrip(")").strip()
                    filetypes.append((desc, patterns))
    
        # Стартовая папка если указана (start_dir), либо последняя открытая папка (last_dir)
        if start_dir == "." and not hasattr(self, "last_dir"): initial_dir = "."
        elif start_dir == "." and hasattr(self, "last_dir"): initial_dir = self.last_dir
        else: initial_dir = start_dir
    
        if multi:
            files = filedialog.askopenfilenames(
                parent=self,
                title=title,
                initialdir=initial_dir,
                filetypes=filetypes or [("All Files", "*.*")]
            )
            if files:
                self.last_dir = str(files[0]).rsplit("/", 1)[0]  # обновляем опследнюю папку (last_dir)
            return list(files)
        else:
            file = filedialog.askopenfilename(
                parent=self,
                title=title,
                initialdir=initial_dir,
                filetypes=filetypes or [("All Files", "*.*")]
            )
            if file:
                self.last_dir = str(file).rsplit("/", 1)[0]
                return [file]
            return []
    
    # Метод для сетапа гейминфо
    def set_gameinfo(self):
        # тут логика чтобы выбрать гейминфо через браузер
        self.gameinfo_path = self.open_files_dialog(title="Open Gameinfo.txt", filter_str="Text (gameinfo.txt);;All (*)", multi=False)

        # Если гейминфо выбран и назначен удачно то идём дальше 
        if not self.gameinfo_path: return
        print(f"self.gameinfo_path: {self.gameinfo_path}")
        print(f"self.project_name: {self.project_name}")
        print(f"self.last_dir: {self.last_dir}")

        # Если таблица не существует - анфризим кнопки, создаём таблицу и настраиваем дрег н дроп
        if not hasattr(self, "sheet"):
            self.unfreeze_control() # Активация контроля кнопок тулбара
            self.build_table_ui() # Постройка и активация таблицы
            self.setup_dnd() # Активация драг н дропа файлов в окно и таблицу
        
        # Обновляем статусную строчку
        self.status_var.set(f"Ready for work! Add new WAV files or open an existing soundscript file.")
    
    # Метод для анфриза кнопок на тулбаре
    def unfreeze_control(self):
        self.btn_new_ss.state(["!disabled"])
        self.btn_open_ss.state(["!disabled"])
        self.btn_save_ss.state(["!disabled"])
        self.btn_add_sounds.state(["!disabled"])

    # Метод который происходит при драг н дропе файлов на окно или таблицу
    def on_drop(self, event):
        paths = self.tk.splitlist(event.data)
        wav_files = [p for p in paths if p.lower().endswith(".wav")] # нам нужны только wav файлы
        if wav_files:
            self.add_files(wav_files)
        else:
            messagebox.showwarning("Warning", f"No WAV files found!")

    # Метод для дабл клика ЛКМ по любому месту в таблице
    def on_double_click(self, event=None):
        print(f"Double click!")
        sel = self.sheet.get_currently_selected()
        print(f"sel: {sel}")
        row = sel.get("row")
        print(f"row: {row}")

def main():
    app = App()
    app.mainloop()

try:
    if __name__ == '__main__':
        main()
except Exception as e:
    import traceback
    # from tkinter import messagebox
    print(f"An error occurred: {e}")
    traceback_error = traceback.format_exc()
    print(traceback_error)
    messagebox.showerror("ERROR", f"{traceback_error}")
    # input("\nPress Enter to exit...")
finally:
    pass