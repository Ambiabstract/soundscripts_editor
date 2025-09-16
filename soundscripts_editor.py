import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from tksheet import Sheet
import json
from pathlib import Path
import re
from typing import List, Dict, Any

# Основные константы на чтение
ABOUT_TOOL_VERSION = "0.2.5"
ABOUT_TOOL_NAME = f"Soundscripts Editor v{ABOUT_TOOL_VERSION}"
ABOUT_TOOL_DESCRIPTION = "This tool helps to edit soundscripts files used on Source Engine."
ABOUT_TOOL_AUTHOR = "Shitcoded by Ambiabstract (Sergey Shavin)."
ABOUT_TOOL_REQUESTED = "Requested by Aptekarr (Ruslan Pozdnyakov)."
ABOUT_TOOL_LINK = "Github: https://github.com/Ambiabstract/soundscripts_editor"
ABOUT_TOOL_DISCORD = "Discord: @Ambiabstract"
CACHE_PATH = "soundscripts_editor_cache.json"
WINDOW_SIZE_DEFAULT = "1024x720"
COLUMN_WIDTH_DENOMINATOR = 10 # делим ширину экрана в 10 раз чтобы получить базовую ширину столбца
ENTRY_NAME_WIDTH_MULTIPLIER = 2
CHANNEL_WIDTH_MULTIPLIER = 1
SOUNDLEVEL_WIDTH_MULTIPLIER = 1
VOLUME_WIDTH_MULTIPLIER = 1
PITCH_WIDTH_MULTIPLIER = 1
SOUNDS_WIDTH_MULTIPLIER = 3.6
HEADERS = ["entry.name", "channel", "soundlevel", "volume", "pitch", "sounds"]
BASE_ROW_HEIGHT = 22
DEFAULT_CHANNEL = "CHAN_AUTO"
DEFAULT_SOUNDLEVEL = "SNDLVL_IDLE"
DEFAULT_VOLUME = "1"
DEFAULT_PITCH = "PITCH_NORM"
CHANNELS_LIST = [
    "CHAN_AUTO", "CHAN_WEAPON", "CHAN_VOICE", "CHAN_VOICE2", "CHAN_ITEM", "CHAN_BODY", "CHAN_STREAM", "CHAN_REPLACE", "CHAN_STATIC", "CHAN_VOICE_BASE"
]
SNDLVLS_LIST  = [
    "SNDLVL_NONE", "SNDLVL_20dB", "SNDLVL_25dB", "SNDLVL_30dB", "SNDLVL_35dB", "SNDLVL_40dB",
            "SNDLVL_45dB", "SNDLVL_50dB", "SNDLVL_55dB", "SNDLVL_IDLE", "SNDLVL_TALKING", "SNDLVL_65dB",
            "SNDLVL_STATIC", "SNDLVL_70dB", "SNDLVL_NORM", "SNDLVL_75dB", "SNDLVL_80dB", "SNDLVL_85dB",
            "SNDLVL_90dB", "SNDLVL_95dB", "SNDLVL_100dB", "SNDLVL_105dB", "SNDLVL_110dB", "SNDLVL_120dB",
            "SNDLVL_130dB", "SNDLVL_GUNFIRE", "SNDLVL_140dB", "SNDLVL_150dB", "SNDLVL_180dB"
]
VOLUME_LIST = ["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1", "0.1, 0.9", "0.2, 0.8", "0.3, 0.7", "0.4, 0.6", "0.5, 1"]
PITCH_LIST = ["10", "20", "30", "40", "50", "60", "70", "80", "90", "PITCH_LOW", "PITCH_NORM", "100", "110", "PITCH_HIGH", "120", "130", "140", "150", "160", "170", "180", "190", "200", "210", "220", "230", "240", "250", "95, 100", "100, 110"]

# Класс приложения
class App(TkinterDnD.Tk):
    # Конструктор класса - метод, который задаёт начальное состояние объекта сразу после его создания
    def __init__(self):
        super().__init__() # вызывает конструктор родительского класса TkinterDnD.Tk чтобы всё работало
        
        # Основные переменные класса
        self.title(f"{ABOUT_TOOL_NAME}")
        self.geometry(WINDOW_SIZE_DEFAULT) # 1024x720
        self.resizable(True, True)
        self.minsize(800, 600)
        # self.column_widths = COLUMN_WIDTHS_DEFAULT # [(0, 200), (1, 100), (2, 100), (3, 100), (4, 100), (5, 385)]
        
        self.items = []  # список словарей в котором хранятся все нужные нам ноды
        self.gameinfo_path = None
        self.gameinfo_folder = None
        self.project_name = None
        self.soundscript_path = None
        self.soundscript_name = None
        self.soundscript_saved = True
        self.add_proj_name_to_entryname = False

        # Строим визуалочку окна, тулбара, нижней строчки
        self.build_main_ui()
        
        self.load_cache()
        if self.gameinfo_path:
            # print(f"gameinfo_path from cache: {self.gameinfo_path}")
            self.prepare_work()

    # Метод для создания основной визуальной части интерфейса (тулбар, кнопки, нижняя часть со статусной надписью)
    def build_main_ui(self):
        # Виджет тулбара
        self.toolbar = ttk.Frame(self, padding=(2, 2, 2, 2)) # слева, сверху, справа, снизу
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Кнопки тулбара
        self.btn_new_ss = ttk.Button(self.toolbar, text="New Soundscript", command=self.new_soundscript, state="disabled")
        self.btn_new_ss.pack(
            side=tk.LEFT, padx=(0, 0)
        )
        self.btn_open_ss = ttk.Button(self.toolbar, text="Open Soundscript", command=self.open_soundscript_dialog, state="disabled")
        self.btn_open_ss.pack(
            side=tk.LEFT, padx=(0, 0)
        )
        self.btn_save_ss = ttk.Button(self.toolbar, text="Save", command=lambda: self.save_soundscript(same_file=True), state="disabled")
        self.btn_save_ss.pack(
            side=tk.LEFT, padx=(0, 0)
        )
        self.btn_save_ss_as = ttk.Button(self.toolbar, text="Save As...", command=self.save_soundscript, state="disabled")
        self.btn_save_ss_as.pack(
            side=tk.LEFT, padx=(0, 0)
        )
        self.btn_add_sounds = ttk.Button(self.toolbar, text="Add Sounds", command=self.add_sounds_button, state="disabled")
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
            height = 1, # количество строк, которые будут одновременно видны в таблице (по вертикали)
            width = 6, # количество столбцов, которые будут одновременно видны (по горизонтали)
            # align="center",
        )
        self.sheet.pack(fill=tk.BOTH, expand=True)
        self.sheet["B:E"].align("center") # горизонтальное центрование для некоторых столбцов

        # Всякие разрешения для таблицы
        try:
            self.sheet.enable_bindings(
                (
                    "single_select",
                    "row_select",
                    "column_select",
                    "drag_select",
                    "arrowkeys",
                    "right_click_popup_menu",
                    "rc_select",
                    # "rc_insert_row",
                    # "rc_delete_row",
                    # "rc_delete",
                    # "copy",
                )
            )
            # print(f"Bindings enabled!")
        except Exception as e:
            print(f"Cant enable bindings!")
            print(f"{e}")
            pass

        # Настройка ширины столбцов
        # Если убрать то сломается ширина столбцов на старте
        # Есть аналогичный код в redraw_sheet, без него сломается при открытии файла
        self.update_column_widths()

        # Создаём кастомное контекстное меню
        self.rcm_menu = tk.Menu(self, tearoff=False)

        # Бинды на контроль таблицы и контекстное меню
        self.sheet.bind("<<SheetModified>>", self.on_sheet_modified)
        self.sheet.bind("<Double-1>", self.fast_edit)
        for w in (self.sheet.MT, self.sheet.CH, self.sheet.RI):
            w.bind("<Button-3>", self.on_right_click, add="+")   # Windows/Linux
            # w.bind("<Button-2>", self.on_right_click, add="+")   # macOS
        # self.sheet.MT.bind("<Button-3>", self.on_right_click_mt, add="+") # Main Table
        # self.sheet.CH.bind("<Button-3>", self.on_right_click_ch, add="+") # Column Headers
        # self.sheet.RI.bind("<Button-3>", self.on_right_click_ri, add="+") # Row Index
        self.sheet.bind("<Control-s>", lambda event: self.save_soundscript(same_file=True))
        self.sheet.bind("<Control-S>", lambda event: self.save_soundscript(same_file=False))
        self.sheet.bind("<Return>", self.fast_edit)
        self.sheet.bind("<Delete>", self.delete_selected_rows)
        
        self.bind("<Configure>", self.on_configure)
        
        # Перехватывание закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
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
        # Если убрать, то сломается при открытии саундскрипта или добавлении новых звуков
        # Есть аналогичный код в build_table_ui, если его не будет то сломается визуал при старте до открытия файла
        self.update_column_widths()
        
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
        print(f"\n{len(self.items)} ITEMS:")
        for index, item_info in enumerate(self.items, start=1):
            # print(f"index: {index}")
            # print(f"item_info: {item_info}")
            
            # Получение данных из списка нод для заполнения таблицы
            entry_name = item_info["entry_name"]
            channel = item_info["channel"]
            soundlevel = item_info["soundlevel"]
            volume = item_info["volume"]
            pitch = item_info["pitch"]
            sounds = item_info["sounds"]
            sounds_str = ""
            
            # Проверка
            '''
            sounds.append("test_001")
            sounds.append("test_002")
            sounds.append("test_003")
            sounds.append("test_004")
            sounds.append("test_005")
            '''

            # Проверка
            print(f"{index}  {entry_name}")
            print(f"    channel:    {channel}")
            print(f"    soundlevel: {soundlevel}")
            print(f"    volume:     {volume}")
            print(f"    pitch:      {pitch}")
            print(f"    sounds:     ")
            sound_count = 0
            for sound in sounds:
                sound_count += 1
                print(f"    {sound}")
                sounds_str = sounds_str + str(sound)  + "\n"

            # Заполняем данные таблицы
            data.append([entry_name, channel, soundlevel, volume, pitch, sounds_str])
        
        # print(f"data: {data}")
        
        # Назначить новые данные
        try:
            self.sheet.set_sheet_data(data, redraw=False)
        except TypeError:
            # В старых версиях нет аргументов redraw/*_positions
            self.sheet.set_sheet_data(data)
        
        # Настройка высот строчек для каждой строки
        for index, item_info in enumerate(self.items, start=1):
            sounds = item_info["sounds"]
            self.sheet.row_height(index-1, len(sounds) * BASE_ROW_HEIGHT + BASE_ROW_HEIGHT)
        
        # Апдейт визуала таблицы
        self.redraw_sheet()

        # Апдейт статусной надписи
        self.status_var.set(f"Rows count: {len(self.items)}")

    # Вызывается каждый раз когда меняется конфигурация окна, нужно для вызова при изменении размеров окна
    def on_configure(self, event):
        # print(f"Новый размер: {event.width}x{event.height}")
        # print(f"zalupa")
        self.update_column_widths()
    
    # Метод для апдейта ширины колонн
    def update_column_widths(self):
        width = self.winfo_width()
        # height = self.winfo_height()
        column_width_pix = width/COLUMN_WIDTH_DENOMINATOR # примерно 100 при 1024
        
        column_widths_dyn = [
            (0, column_width_pix * ENTRY_NAME_WIDTH_MULTIPLIER), 
            (1, column_width_pix * CHANNEL_WIDTH_MULTIPLIER), 
            (2, column_width_pix * SOUNDLEVEL_WIDTH_MULTIPLIER), 
            (3, column_width_pix * VOLUME_WIDTH_MULTIPLIER), 
            (4, column_width_pix * PITCH_WIDTH_MULTIPLIER), 
            (5, column_width_pix * SOUNDS_WIDTH_MULTIPLIER)
        ]
        for column, width in column_widths_dyn:
            self.sheet.column_width(column, int(round(width)))
    
    # Метод для добавления в таблицу файлов которые были кинуты драг н дропом или через браузер файлов
    def add_sounds_button(self):
        print(f"add_sounds_button start")
        # self.soundscript_path = self.open_files_dialog(title="Open soundscript", filter_str="Text (*.txt);;All (*)", start_dir = scripts_folder, multi=False)
        sound_folder = os.path.dirname(self.gameinfo_path) + "/sound"
        print(f"sound_folder: {sound_folder}")
        sound_files = self.open_files_dialog(title="Open WAV files", filter_str="Sounds (*.wav);;All (*)", start_dir = sound_folder, multi=True)
        print(f"sound_files: {sound_files}")
        if not sound_files: return
        self.add_files(sound_files)

    # Метод для добавления в таблицу файлов которые были кинуты драг н дропом или через браузер файлов
    def add_files(self, paths):
        # Добавляем только WAV файлы
        wav_files = [p for p in paths if p.lower().endswith(".wav")]
        if not wav_files:
            messagebox.showwarning("Warning", f"No WAV files found!")
            return
        paths = wav_files
        
        files_count = 0
        bad_paths = []
        for path in paths:
            path = os.path.abspath(path)
            file_name = os.path.basename(path) or path
            sounds = []
            path_rel = None
            
            # Добавляем к именам первое слово из имени проекта в качестве префикса до точки
            if self.add_proj_name_to_entryname:
                file_name = self.project_name.split()[0].lower() + "." + file_name
                # print(f"self.soundscript_name: {self.soundscript_name}")
            
            # Фиксим имена
            file_name = file_name.replace(".wav", "").replace(".WAV", "")
            file_name = re.sub(r"[А-Яа-яЁё]", "", file_name)
            file_name = re.sub(r"[ \-\—\(\)\[\]\{\},;!@#$%^&*+=№~`«»<>?/\\|\"']", "_", file_name)
            file_name = re.sub(r"_+", "_", file_name)
            file_name = file_name.strip("_")
            
            # Уникальные имена
            existing_names = [e["entry_name"] for e in self.items]
            if file_name in existing_names:
                i = 1
                new_file_name = f"{file_name}_{i}"
                while new_file_name in existing_names:
                    i += 1
                    new_file_name = f"{file_name}_{i}"
                file_name = new_file_name

            # Добавление пути файла в список звуков
            # Функция чтобы преобразовывать абсолютный путь файла в относительный путь
            try:
                # Проверяем, начинается ли path с папки с гейминфо
                if os.path.commonpath([self.gameinfo_folder, os.path.normcase(path)]) == self.gameinfo_folder:
                    try:
                        relative = os.path.relpath(path, start=self.gameinfo_folder)
                        parts = relative.split(os.sep)
            
                        if parts[0].lower() == "sound":
                            # Всё, что справа от "sound"
                            path_rel = "/".join(parts[1:])
                            sounds.append(path_rel)
                        else:
                            bad_paths.append(path)
                            continue
                    except ValueError:
                        bad_paths.append(path)
                        continue
                else:
                    bad_paths.append(path)
                    continue
            except Exception:
                bad_paths.append(path)
                continue

            # Добавление новых нод
            self.items.append({"entry_name": file_name, "channel": DEFAULT_CHANNEL, "soundlevel": DEFAULT_SOUNDLEVEL, "volume": DEFAULT_VOLUME, "pitch": DEFAULT_PITCH, "sounds": sounds})
            files_count += 1

        self.update_table()
        self.status_var.set(f"Added {files_count} WAV files." if files_count else f"WAV files not found!")
        self.soundscript_saved = False
        self.title(f"{ABOUT_TOOL_NAME} | {self.project_name} - {self.soundscript_name if self.soundscript_name else 'Unsaved Soundscript'}*")
        if bad_paths:
            messagebox.showwarning(
                "WARNING",
                f'These files are not from the "{self.project_name}" directory and will not be added!\n\n' +
                "\n".join(bad_paths)
            )

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

    # Метод для нового саундскрипта
    def new_soundscript(self):
        if not self.items: return
        if not self.soundscript_saved:
            if not messagebox.askokcancel("WARNING", "Are you sure you want to create a new script?\nUnsaved progress will be lost!"): return
        self.soundscript_name = None
        self.soundscript_path = None
        self.items = []
        self.update_table()
        self.title(f"{ABOUT_TOOL_NAME} | {self.project_name} - New Soundscript")
    
    # Универсальный метод для файлового браузера на открытие файлов
    def open_files_dialog(self, title, filter_str="All Files (*.*)", start_dir=".", multi=True):
        # print(f"open_files_dialog start")
        # print(f"self: {self}")
        # print(f"title: {title}")
        # print(f"filter_str: {filter_str}")
        # print(f"start_dir: {start_dir}")
        # print(f"multi: {multi}")

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

    # Универсальный метод для файлового браузера на сохранение файла
    def save_file_dialog(self, title, filter_str="All Files (*.*)", start_dir=".", suggested_name="", add_default_ext=True):
        filetypes = []
        default_ext = ""
        if filter_str:
            for i, f in enumerate(filter_str.split(";;")):
                parts = f.split("(", 1)
                if len(parts) == 2:
                    desc = parts[0].strip()
                    patterns = parts[1].rstrip(")").strip()
                    filetypes.append((desc, patterns))
                    if i == 0 and add_default_ext:
                        first_pat = patterns.split(";")[0].strip()
                        if first_pat.startswith("*.") and len(first_pat) > 2:
                            default_ext = first_pat[1:]
        if not filetypes:
            filetypes = [("All Files", "*.*")]

        if start_dir == ".":
            initial_dir = getattr(self, "last_dir", ".")
        else:
            initial_dir = start_dir

        kwargs = dict(
            parent=self,
            title=title,
            initialdir=initial_dir,
            filetypes=filetypes,
            initialfile=suggested_name or None,
        )
        if add_default_ext and default_ext:
            kwargs["defaultextension"] = default_ext
        try:
            kwargs["confirmoverwrite"] = True
        except Exception:
            pass
    
        path = filedialog.asksaveasfilename(**kwargs)

        if not path:
            return ""
    
        # Если пользователь не указал расширение и по каким-то причинам Tk не добавил его — добавим сами
        if add_default_ext and default_ext and not os.path.splitext(path)[1]:
            path += default_ext
    
        # Запоминаем последнюю папку
        self.last_dir = os.path.dirname(path) if os.path.dirname(path) else "."
    
        return path

    # Метод для сетапа гейминфо
    def set_gameinfo(self):
        # тут логика чтобы выбрать гейминфо через браузер
        self.gameinfo_path = Path(self.open_files_dialog(title="Open Gameinfo.txt", filter_str="Text (gameinfo.txt);;All (*)", multi=False)[0])
        # print(f"self.gameinfo_path SET GAMEINFO: {self.gameinfo_path}")

        # Если гейминфо выбран и назначен удачно то идём дальше 
        if not self.gameinfo_path: return
        # print(f"self.gameinfo_path: {self.gameinfo_path}")
        # print(f"self.project_name: {self.project_name}")
        # print(f"self.last_dir: {self.last_dir}")
        
        # Сохраняемся
        self.save_cache()
        
        # Завершаем подготовку к работе
        self.prepare_work()

    # Метод для завершения подготовки к работе
    def prepare_work(self):
        # Меняем заголовок окна, добавляя имя проекта из гейминфо
        self.project_name = self.get_project_name()
        self.title(f"{ABOUT_TOOL_NAME} | {self.project_name}")
        
        # Сохраняем папку проекта
        self.gameinfo_folder = os.path.dirname(self.gameinfo_path)
        
        # Если таблица не существует - анфризим кнопки, создаём таблицу и настраиваем дрег н дроп
        if not hasattr(self, "sheet"):
            self.unfreeze_control() # Активация контроля кнопок тулбара
            self.build_table_ui() # Постройка и активация таблицы
            self.setup_dnd() # Активация драг н дропа файлов в окно и таблицу
        
        # Обновляем статусную строчку
        self.status_var.set(f"Ready for work! Add new WAV files or open an existing soundscript file.")
    
    # Метод для получения имени мода из гейминфо
    def get_project_name(self):
        # print(f"self.gameinfo_path GET PROJ NAME: {self.gameinfo_path}")
        with open(self.gameinfo_path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                # Игнорим комментарии
                if not line or line.startswith("//"):
                    continue
                m = re.match(r'^game\s+"([^"]+)"\s*$', line)
                if m:
                    return m.group(1)
                    # print(f"self.project_name: {self.project_name}")
                    break
        if not self.project_name:
            print(f"ERROR! game name not found in gameinfo.txt:")
            print(f"{gameinfo_path}")
            return
    
    # Метод для анфриза кнопок на тулбаре
    def unfreeze_control(self):
        self.btn_new_ss.state(["!disabled"])
        self.btn_open_ss.state(["!disabled"])
        self.btn_save_ss.state(["!disabled"])
        self.btn_save_ss_as.state(["!disabled"])
        self.btn_add_sounds.state(["!disabled"])

    # Метод который происходит при драг н дропе файлов на окно или таблицу
    def on_drop(self, event):
        paths = self.tk.splitlist(event.data)
        if ".txt" in paths[0]: 
            if self.items and not self.soundscript_saved:
                if not messagebox.askokcancel("WARNING", "Are you sure you want to open a script?\nUnsaved progress will be lost!"): return
            self.soundscript_path = paths[0]
            print(f"self.soundscript_path: {self.soundscript_path}")
            self.open_soundscript()
            return
        self.add_files(paths)

    # Метод для дабл клика ЛКМ по любому месту в таблице
    def on_sheet_modified(self, event):
        print(f"Sheet modified!")
        self.soundscript_saved = False
        self.title(f"{ABOUT_TOOL_NAME} | {self.project_name} - {self.soundscript_name if self.soundscript_name else 'Unsaved Soundscript'}*")
    
    # Метод для получения информации при селекте чего-либо в таблице
    def get_selection_info(self, event=None):
        print(f" ")
        print(f"get_selection_info!")
        select = self.sheet.get_currently_selected()
        print(f"select: {select}")
        if not select: return
        row, column, type_, box, iid, fill_iid = select
        from_row, from_column, upto_row, upto_column = box
        '''
        print(f"\trow: {row}")
        print(f"\tcolumn: {column}")
        print(f"\ttype_: {type_}")
        # print(f"\tbox: {box}")
        # print(f"\tiid: {iid}")
        # print(f"\tfill_iid: {fill_iid}")
        print(f"\tfrom_row: {from_row}")
        print(f"\tupto_row: {upto_row}")
        print(f"\tfrom_column: {from_column}")
        print(f"\tupto_column: {upto_column}")
        '''
        selected_rows = list(range(from_row, upto_row))
        '''
        # print(f"selected_rows:")
        # for index in selected_rows:
            # print(f"index: {index}")
        '''
        multiselect_rows = not (upto_row - 1 == from_row)
        multiselect_columns = not (upto_column - 1 == from_column)
        multiselect_both = multiselect_rows and multiselect_columns
        multiselect_check = multiselect_rows or multiselect_columns
        '''
        print(f"multiselect_rows: {multiselect_rows}")
        print(f"multiselect_columns: {multiselect_columns}")
        print(f"multiselect_both: {multiselect_both}")
        print(f"multiselect_check: {multiselect_check}")
        '''
        
        column_name_selected = (from_column <= 0 < upto_column)
        column_channel_selected = (from_column <= 1 < upto_column)
        column_soundlevel_selected = (from_column <= 2 < upto_column)
        column_volume_selected = (from_column <= 3 < upto_column)
        column_pitch_selected = (from_column <= 4 < upto_column)
        column_sounds_selected = (from_column <= 5 < upto_column)
        '''
        print(f"column_channel_selected: {column_channel_selected}")
        print(f"column_soundlevel_selected: {column_soundlevel_selected}")
        print(f"column_volume_selected: {column_volume_selected}")
        print(f"column_pitch_selected: {column_pitch_selected}")
        '''
        
        selection_info = {"row": row, "column": column, "type_": type_, "selected_rows": selected_rows, "multiselect_rows": multiselect_rows, "multiselect_columns": multiselect_columns, "multiselect_both": multiselect_both, "multiselect_check": multiselect_check, "column_name_selected": column_name_selected, "column_channel_selected": column_channel_selected, "column_soundlevel_selected": column_soundlevel_selected, "column_volume_selected": column_volume_selected, "column_pitch_selected": column_pitch_selected, "column_sounds_selected": column_sounds_selected}
        
        return selection_info
    
    # Быстрый вход в редактирование - дабл-клик ЛКМ или Enter
    def fast_edit(self, event=None):
        print(f"Fast edit!")
        
        # Получаем всю необходимую инфу о текущем выделении
        selection_info = self.get_selection_info()
        if not selection_info: return
        row = selection_info["row"]
        selected_rows = selection_info["selected_rows"]
        column_name_selected = selection_info["column_name_selected"]
        column_channel_selected = selection_info["column_channel_selected"]
        column_soundlevel_selected = selection_info["column_soundlevel_selected"]
        column_volume_selected = selection_info["column_volume_selected"]
        column_pitch_selected = selection_info["column_pitch_selected"]
        column_sounds_selected = selection_info["column_sounds_selected"]
        
        if column_name_selected: self.edit_entry_names(selected_rows)
        if column_channel_selected: self.edit_csvp(selected_rows, "channel")
        if column_soundlevel_selected: self.edit_csvp(selected_rows, "soundlevel")
        if column_volume_selected: self.edit_csvp(selected_rows, "volume")
        if column_pitch_selected: self.edit_csvp(selected_rows, "pitch")
        if column_sounds_selected: self.edit_row_sounds_list(row)
        
    # Метод для контекстного меню таблицы на ПКМ - в зависимости от контекста клика показываются разные пункты
    def on_right_click(self, event):
        print(f" ")
        print(f"Контекстное меню!")
        
        # Получаем всю необходимую инфу о текущем выделении
        selection_info = self.get_selection_info()
        if not selection_info: return
        row = selection_info["row"]
        column = selection_info["column"]
        type_ = selection_info["type_"]
        selected_rows = selection_info["selected_rows"]
        multiselect_rows = selection_info["multiselect_rows"]
        multiselect_check = selection_info["multiselect_check"]
        column_name_selected = selection_info["column_name_selected"]
        column_channel_selected = selection_info["column_channel_selected"]
        column_soundlevel_selected = selection_info["column_soundlevel_selected"]
        column_volume_selected = selection_info["column_volume_selected"]
        column_pitch_selected = selection_info["column_pitch_selected"]
        
        # Очищаем контекстное меню перед заполнением в зависимости от контекста выделения
        self.rcm_menu.delete(0, "end")
        
        # Скорее всего эта фича не нужна
        # if type_ == "cells" and not multiselect_check: self.rcm_menu.add_command(label="Edit this Cell", command=lambda: self.placeholder_message())
        
        if type_ in ("cells", "columns") and column_name_selected: self.rcm_menu.add_command(label="Edit entry.names", command=lambda: self.edit_entry_names(selected_rows))
        
        if type_ == "cells" and column_channel_selected: self.rcm_menu.add_command(label="Set Channel for selection", command=lambda: self.edit_csvp(selected_rows, "channel"))
        if type_ == "cells" and column_soundlevel_selected: self.rcm_menu.add_command(label="Set Soundlevel for selection", command=lambda: self.edit_csvp(selected_rows, "soundlevel"))
        if type_ == "cells" and column_volume_selected: self.rcm_menu.add_command(label="Set Volume for selection", command=lambda: self.edit_csvp(selected_rows, "volume"))
        if type_ == "cells" and column_pitch_selected: self.rcm_menu.add_command(label="Set Pitch for selection", command=lambda: self.edit_csvp(selected_rows, "pitch"))
        
        if type_ in ("cells", "rows") and not multiselect_rows: self.rcm_menu.add_command(label="Edit sounds of this row", command=lambda: self.edit_row_sounds_list(row))
        
        if type_ == "columns" and column == 1: self.rcm_menu.add_command(label="Set Channel for All", command=lambda: self.edit_csvp(selected_rows, "channel"))
        if type_ == "columns" and column == 2: self.rcm_menu.add_command(label="Set Soundlevel for All", command=lambda: self.edit_csvp(selected_rows, "soundlevel"))
        if type_ == "columns" and column == 3: self.rcm_menu.add_command(label="Set Volume for All", command=lambda: self.edit_csvp(selected_rows, "volume"))
        if type_ == "columns" and column == 4: self.rcm_menu.add_command(label="Set Pitch for All", command=lambda: self.edit_csvp(selected_rows, "pitch"))
        
        self.rcm_menu.add_separator()
        
        if type_ == "cells" and column in (3, 4): self.rcm_menu.add_command(label="Clear Cell(s)", command=lambda: self.clear_selected_cells())
        if type_ == "columns" and column in (3, 4): self.rcm_menu.add_command(label="Clear All", command=lambda: self.clear_selected_cells())
        if type_ in ("cells", "rows"): self.rcm_menu.add_command(label="Delete Row(s)", command=lambda: self.delete_selected_rows())

        self.rcm_menu.tk_popup(event.x_root, event.y_root)
        # sel = self.sheet.get_currently_selected()
        # print(f"sel: {sel}")
        # row = sel.get("row")
        # print(f"row: {row}")

    # Заглушечное окно
    def placeholder_message(self):
        messagebox.showinfo("Work in progress", "Сорян Русик, эта фича ещё не работает ¯\_(ツ)_/¯")
        
    # Метод для очистки необязательных клеточек
    def clear_selected_cells(self):
        print(f"CLEAR_SELECTED_CELLS START")
        selection_info = self.get_selection_info()
        selected_rows = selection_info["selected_rows"]
        column_volume_selected = selection_info["column_volume_selected"]
        column_pitch_selected = selection_info["column_pitch_selected"]
        print(f"selected_rows: {selected_rows}")
        print(f"self.items: {self.items}")
        
        # Получаем список имён нод для которых планируем очистить клеточки
        entry_names = []
        for idx in selected_rows:
            entry_names.append(self.items[idx]["entry_name"])
        print(f"entry_names: ")
        for entry_name in entry_names: print(f"{entry_name}")
        
        # Вы уверены что хотите очистить клеточки?
        if not messagebox.askyesno(
            "Clearing cells",
            f"Are you sure you want to clear cells of these {len(selected_rows)} rows?\n\n" +
            "\n".join(entry_names)
        ):
            return
        
        for idx in selected_rows:
            self.items[idx]["volume"] = "" if column_volume_selected else self.items[idx]["volume"]
            self.items[idx]["pitch"] = "" if column_pitch_selected else self.items[idx]["pitch"]

        # Апдейт таблицы и других приколов
        self.update_table()
        self.status_var.set(f"Cleared cells for {len(selected_rows)} rows!")
        self.soundscript_saved = False
        self.title(f"{ABOUT_TOOL_NAME} | {self.project_name} - {self.soundscript_name if self.soundscript_name else 'Unsaved Soundscript'}*")
        
    # Метод для удаления нод
    def delete_selected_rows(self, event=None):
        print(f"DELETE_ROWS START")
        selection_info = self.get_selection_info()
        selected_rows = selection_info["selected_rows"]
        print(f"selected_rows: {selected_rows}")
        print(f"self.items: {self.items}")
        
        # Получаем список имён нод которые планируем удалить
        entry_names = []
        for idx in selected_rows:
            entry_names.append(self.items[idx]["entry_name"])
        print(f"entry_names: ")
        for entry_name in entry_names: print(f"{entry_name}")
        
        # Вы уверены что хотите удалить эти строки?
        if not messagebox.askyesno(
            "Deleting rows",
            f"Are you sure you want to delete these {len(selected_rows)} rows?\n\n" +
            "\n".join(entry_names)
        ):
            return
        
        for i in sorted(selected_rows, reverse=True):
            del self.items[i]

        # Апдейт таблицы и других приколов
        self.update_table()
        self.status_var.set(f"Removed {len(selected_rows)} rows!")
        self.soundscript_saved = False
        self.title(f"{ABOUT_TOOL_NAME} | {self.project_name} - {self.soundscript_name if self.soundscript_name else 'Unsaved Soundscript'}*")

    # Метод для редактирования каналов одной или нескольких нод
    def edit_csvp(self, selected_rows, csvp):
        print(f" ")
        print(f"EDIT CHANNELS START")
        print(f"selected_rows: {selected_rows}")
        print(f"self.items: {self.items}")
        print(f"csvp: {csvp}")
        
        if not csvp: return
        
        if csvp == "channel":
            dialog_title = "Set Channel"
            dialog_description = "Enter a new channel value for selected rows:"
            dialog_list = CHANNELS_LIST
            dialog_default = DEFAULT_CHANNEL

        if csvp == "soundlevel":
            dialog_title = "Set Soundlevel"
            dialog_description = "Enter a new soundlevel value for selected rows:"
            dialog_list = SNDLVLS_LIST
            dialog_default = DEFAULT_SOUNDLEVEL
        
        if csvp == "volume":
            dialog_title = "Set Volume"
            dialog_description = "Enter a new volume value for selected rows:"
            dialog_list = VOLUME_LIST
            dialog_default = DEFAULT_VOLUME
        
        if csvp == "pitch":
            dialog_title = "Set Pitch"
            dialog_description = "Enter a new pitch value for selected rows:"
            dialog_list = ["10", "20", "30", "40", "50", "60", "70", "80", "90", "PITCH_LOW", "PITCH_NORM", "100", "110", "PITCH_HIGH", "120", "130", "140", "150", "160", "170", "180", "190", "200", "210", "220", "230", "240", "250", "95, 100", "100, 110"]
            dialog_default = DEFAULT_PITCH
        
        dialog = ChoiceDialog(
            self,
            dialog_title,
            dialog_description,
            dialog_list,
            dialog_default
        )
        new_value = dialog.result
        if not new_value: return
        for idx in selected_rows:
            self.items[idx][csvp] = new_value

        self.update_table()
        self.status_var.set(f"Updated {csvp} for {len(selected_rows)} rows!")
        self.soundscript_saved = False
        self.title(f"{ABOUT_TOOL_NAME} | {self.project_name} - {self.soundscript_name if self.soundscript_name else 'Unsaved Soundscript'}*")
    
    # Метод для редактирования имён
    def edit_entry_names(self, selected_rows, override_name=None):
        print(f" ")
        print(f"edit_entry_name!!!!!")
        print(f"selected_rows: {selected_rows}")
        
        for row in selected_rows:
            current_entry_name = self.items[row]["entry_name"]
            print(f"current_entry_name: {current_entry_name}")
            
            init_name = override_name if override_name else current_entry_name
            
            # Без этой штуки фокус каждого нового окна слетает начиная со второго
            self.update()
            
            new_entry_name = simpledialog.askstring(
                "New name",
                "Please enter a new entry.name:\t\t\t\n",
                initialvalue=init_name,
                parent=self
            )
            if not new_entry_name or current_entry_name == new_entry_name: continue
            
            # Проверка на существование такого имени в таблице
            existing_names = [e["entry_name"] for e in self.items]
            if new_entry_name in existing_names: 
                if not messagebox.askyesno("Warning", "This name already exist! Are you sure you want to continue?"):
                    self.edit_entry_names([row], override_name=new_entry_name)
                    continue
            # Новое значение имени
            self.items[row]["entry_name"] = new_entry_name
        
        self.update_table()
        self.status_var.set(f"{len(selected_rows)} names updated!")
        self.soundscript_saved = False
        self.title(f"{ABOUT_TOOL_NAME} | {self.project_name} - {self.soundscript_name if self.soundscript_name else 'Unsaved Soundscript'}*")
    
    # Метод для редактирования звуков ноды (один wave или rndwave)
    def edit_row_sounds_list(self, row):
        print(f" ")
        print(f"edit_row_sounds_list!")
        print(f"row: {row}")
        
        entry_name = self.items[row]["entry_name"]
        
        sounds = self.items[row]["sounds"]
        print(f"sounds: {sounds}")
        
        for wave in sounds: print(f"\twave: {wave}")
        print(f" ")
        
        new_sounds = SoundsListEdit(
            self,
            f'Edit Sounds for "{entry_name}"',
            f'Add or remove sounds for "{entry_name}".\t\nSingle sound will be only "wave".\t\t\t\nMultiple sounds will be "rndwave" block with waves.\t',
            sounds
        )
        new_sounds = new_sounds.result
        
        print(f"!!! new_sounds: {new_sounds}")
        if not new_sounds: return
        
        self.items[row]["sounds"] = new_sounds
        
        self.update_table()
        self.status_var.set(f"Updated sounds for {entry_name}!")
        self.soundscript_saved = False
        self.title(f"{ABOUT_TOOL_NAME} | {self.project_name} - {self.soundscript_name if self.soundscript_name else 'Unsaved Soundscript'}*")

    # Метод для загрузки кэша из файла
    def load_cache(self) -> str | None:
        cache_path = Path(CACHE_PATH)
        if not cache_path.exists():
            return None
        # print(f"cache_path: {cache_path}")
        try:
            gameinfo_path = Path(json.loads(cache_path.read_text(encoding="utf-8"))[0].get("gameinfo_path"))
            window_size = json.loads(cache_path.read_text(encoding="utf-8"))[1].get("window_size")
            # print(f"gameinfo_path: {gameinfo_path}")
            # print(f"window_size: {window_size}")
            if gameinfo_path.exists(): self.gameinfo_path = gameinfo_path
            self.geometry(window_size if window_size else WINDOW_SIZE_DEFAULT)
            return
        except Exception as e:
            print(f"Failed to load cache!")
            print(f"Exception:")
            print(e)
            return
    
    # Метод для сохранения кэша в файл
    def save_cache(self) -> bool:
        width = self.winfo_width()
        height = self.winfo_height()
        window_size = f"{width}x{height}"
        json_dumps_content = [
            {"gameinfo_path": str(self.gameinfo_path)},
            {"window_size": window_size},
        ]
        try:
            Path(CACHE_PATH).write_text(json.dumps(json_dumps_content, indent=2), encoding="utf-8")
            print(f"Cache saved!")
            # print(f"Content:")
            # print(f"{json_dumps_content}")
            return True
        except Exception as e:
            print(f"ERROR SAVING CACHE:")
            print(e)
            return False

    # Функция для дампа содержания саундскрипта из итемов
    def dump_soundscript_from_items(self) -> str:
        items = self.items
        out = []
        out.append(f'// Generated by {ABOUT_TOOL_NAME}')
        out.append(f'// {ABOUT_TOOL_DESCRIPTION}')
        out.append(f'// {ABOUT_TOOL_AUTHOR}')
        out.append(f'// {ABOUT_TOOL_REQUESTED}')
        out.append(f'// {ABOUT_TOOL_LINK}')
        out.append(f'// {ABOUT_TOOL_DISCORD}\n')
        for r in items:
            out.append(f'"{r["entry_name"]}"\n{{')
            out.append(f'\t"channel"\t\t"{r["channel"]}"')
            if r["volume"]: out.append(f'\t"volume"\t\t"{r["volume"]}"')
            out.append(f'\t"soundlevel"\t"{r["soundlevel"]}"')
            if r["pitch"]: out.append(f'\t"pitch"\t\t\t"{r["pitch"]}"')
    
            if not r.get("sounds"):
                out.append('\t"wave"\t\t""')
            elif len(r["sounds"]) == 1:
                out.append(f'\t"wave"\t\t\t"{r["sounds"][0]}"')
            else:
                out.append('\t"rndwave"\n\t\t{')
                for w in r["sounds"]:
                    out.append(f'\t\t"wave"\t"{w}"')
                out.append('\t}')
            out.append('}\n')
        return "\n".join(out)
    
    # Функция для сохранения саундскрипта
    def save_soundscript(self, same_file=False):
        if not self.items: return
        
        # Если у нас абсолютно новый файл и пользователь жмякает Save - надо запускать Save As логику
        if not self.soundscript_name: same_file=False
        
        scripts_folder = os.path.dirname(self.gameinfo_path) + "/scripts"
        ss_path = self.soundscript_path
        
        print(f"ss_path: {ss_path}")
        print(f"same_file: {same_file}")
        print(f"self.soundscript_name: {self.soundscript_name}")
        print(f"self.soundscript_path: {self.soundscript_path}")
        
        if not same_file:
            ss_name = self.soundscript_name if self.soundscript_name else self.project_name.split()[0].lower() + "_" + "soundscript"
            print(f"ss_name: {ss_name}")
            ss_path = self.save_file_dialog(title = "Save Soundscript", filter_str = "Text (*.txt);;All (*)", start_dir = scripts_folder, suggested_name = ss_name, add_default_ext = True)
        
        if not ss_path: return None
        print(f"ss_path: {ss_path}")
        
        soundscript_content = self.dump_soundscript_from_items()
        print(f"soundscript_content:")
        print(soundscript_content)
        with open(ss_path, "w", encoding="utf-8") as f:
            f.write(soundscript_content)
        self.soundscript_name = os.path.basename(ss_path)
        self.soundscript_path = ss_path
        self.title(f"{ABOUT_TOOL_NAME} | {self.project_name} - {self.soundscript_name}")
        self.soundscript_saved = True
        self.save_cache() # Сохраняемся
        self.status_var.set(f"{self.soundscript_name} successfully saved!")
        return ss_path
    
    # Функция для открытия саундскрипта
    def open_soundscript_dialog(self):
        if self.items and not self.soundscript_saved:
            if not messagebox.askokcancel("WARNING", "Are you sure you want to open a script?\nUnsaved progress will be lost!"): return
        self.gameinfo_path = str(self.gameinfo_path)
        scripts_folder = os.path.dirname(self.gameinfo_path) + "/scripts"
        self.soundscript_path = self.open_files_dialog(title="Open soundscript", filter_str="Text (*.txt);;All (*)", start_dir = scripts_folder, multi=False)
        if not self.soundscript_path: return
        self.soundscript_path = self.soundscript_path[0]
        self.open_soundscript()
        
    # Функция для открытия саундскрипта
    def open_soundscript(self):
        if not self.soundscript_path: return
        self.soundscript_name = os.path.basename(self.soundscript_path) or self.soundscript_path
        with open(self.soundscript_path, 'r', encoding='utf-8') as soundscript_file: soundscript_content = soundscript_file.read()
        print(f"soundscript_content:")
        print(soundscript_content)
        try:
            new_items = self.parse_soundscript(soundscript_content)
            print(f"new_items:")
            print(new_items)
            if new_items:
                self.items = new_items
                self.update_table()
                self.title(f"{ABOUT_TOOL_NAME} | {self.project_name} - {self.soundscript_name}")
                self.soundscript_saved = True
        except Exception as e:
            print(f"ERROR READING SOUNDSCRIPT FILE!")
            print(e)
            return

    # Функция для чтения саундскрипта
    def parse_soundscript(self, text) -> List[Dict[str, Any]]:
        items = []
        # Регулярка для нахождения каждого блока
        block_pattern = re.compile(r'"([^"]+)"\s*\{([^}]*)\}', re.DOTALL)
    
        for match in block_pattern.finditer(text):
            entry_name = match.group(1)
            body = match.group(2)
    
            item: Dict[str, Any] = {
                "entry_name": entry_name,
                "channel": "",
                "volume": "",
                "soundlevel": "",
                "pitch": "",
                "sounds": []
            }
    
            # Проверка на rndwave
            if "rndwave" in body:
                # находим все wave внутри rndwave
                rnd_pattern = re.compile(r'"wave"\s+"([^"]+)"')
                item["sounds"] = rnd_pattern.findall(body)
            else:
                wave_match = re.search(r'"wave"\s+"([^"]+)"', body)
                if wave_match:
                    item["sounds"] = [wave_match.group(1)]
    
            # остальные параметры
            channel_match = re.search(r'"channel"\s+"([^"]+)"', body)
            if channel_match:
                item["channel"] = channel_match.group(1)
    
            volume_match = re.search(r'"volume"\s+"([^"]+)"', body)
            if volume_match:
                item["volume"] = volume_match.group(1)
    
            soundlevel_match = re.search(r'"soundlevel"\s+"([^"]+)"', body)
            if soundlevel_match:
                item["soundlevel"] = soundlevel_match.group(1)
    
            pitch_match = re.search(r'"pitch"\s+"([^"]+)"', body)
            if pitch_match:
                item["pitch"] = pitch_match.group(1)
    
            items.append(item)
    
        return items

    # Метод для отслеживания закрытия окна приложения
    def on_closing(self):
        if not self.soundscript_saved:
            answer = messagebox.askyesnocancel(
                "Unsaved changes",
                "You have unsaved changes! \nWould you like to save before exiting?"
            )
            if answer:  # Да, сохраняем
                self.save_soundscript(same_file=True)
                self.save_cache() # Сохраняемся
                self.destroy()
            elif answer is False:  # Нет, выходим без сохранения
                self.save_cache() # Сохраняемся
                self.destroy()
            else:  # Отмена - остаёмся в приложении
                self.save_cache() # Сохраняемся
                return
        else:
            self.save_cache() # Сохраняемся
            self.destroy()

# Класс диалогового окна для редактирования csvp
class ChoiceDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt, values, default=None):
        super().__init__(parent)
        self.title(title)
        self.result = None

        # Минимальные размеры
        self.minsize(300, 160)

        # Описание
        tk.Label(self, text=prompt).pack(padx=10, pady=10)

        # Combobox
        self.combo = ttk.Combobox(self, values=values, state="readonly")
        self.combo.pack(padx=10, pady=5, fill="x", expand=True)

        # Дефолтное значение
        if default and default in values:
            self.combo.set(default)
        else:
            self.combo.current(0)

        # Подпись и поле ввода
        tk.Label(self, text="Or enter a custom value:").pack(padx=10, pady=(10, 0))
        self.entry = tk.Entry(self)
        self.entry.pack(padx=10, pady=5, fill="x", expand=True)

        # Кнопки
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        ok_button = tk.Button(button_frame, text="   OK   ", command=self.on_ok, default="active")
        ok_button.pack(side="left", padx=5)

        cancel_button = tk.Button(button_frame, text="Cancel", command=self.on_cancel)
        cancel_button.pack(side="right", padx=5)

        # Фокус на поле ввода
        self.entry.focus_set()

        # Enter = OK
        self.bind("<Return>", lambda event: self.on_ok())

        # Escape = Cancel
        self.bind("<Escape>", lambda event: self.on_cancel())

        # Сделать окно модальным
        self.grab_set()

        # Центрирование
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Ждать закрытия
        self.wait_window()

    def on_ok(self):
        text_value = self.entry.get().strip()
        if text_value:
            self.result = text_value
        else:
            self.result = self.combo.get()
        self.destroy()

    def on_cancel(self):
        self.destroy()

# Класс окна для редактирования звуков конкретной ноды
class SoundsListEdit(tk.Toplevel):
    def __init__(self, parent, title, prompt, sounds):
        super().__init__(parent)
        self.title(title)
        self.result = None
        
        self.parent = parent

        # Минимальные размеры
        self.minsize(300, 300)

        # Описание
        tk.Label(self, text=prompt).pack(padx=10, pady=10)
        
        # Список
        self.sounds_list = tk.Listbox(self, selectmode='extended', width=50, height=10)
        self.sounds_list.pack(padx=10, pady=10)
        self.sounds_list.bind("<Control-a>", self.select_all)
        self.sounds_list.bind("<Control-A>", self.select_all)
        self.sounds_list.bind("<Delete>", self.remove_selected)
        
        # Заполняем список текущим списком
        for sound in sounds: self.sounds_list.insert(tk.END, sound)
        
        self.sounds = sounds

        # Кнопки
        button_frame_1 = tk.Frame(self)
        button_frame_1.pack(pady=10)
        button_frame_2 = tk.Frame(self)
        button_frame_2.pack(pady=10)
        
        add_sounds_btn = tk.Button(button_frame_1, text="      Add Sounds\t", command=self.add_files).pack(side="left", padx=5)
        
        remove_sounds_btn = tk.Button(button_frame_1, text="  Remove Sounds\t", command=self.remove_selected).pack(side="left", padx=5)

        ok_button = tk.Button(button_frame_2, text="     OK\t", command=self.on_ok, default="active")
        ok_button.pack(side="left", padx=5)

        cancel_button = tk.Button(button_frame_2, text="  Cancel\t", command=self.on_cancel)
        cancel_button.pack(side="right", padx=5)

        # Фокус на поле ввода
        self.sounds_list.focus_set()

        # Enter = OK
        self.bind("<Return>", lambda event: self.on_ok())

        # Escape = Cancel
        self.bind("<Escape>", lambda event: self.on_cancel())

        # Сделать окно модальным
        self.grab_set()

        # Центрирование
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Ждать закрытия
        self.wait_window()

    # Метод для добавления новых звуков в список
    def add_files(self):
        print(f"SoundsListEdit add_files")
        
        # Выбираем WAV файлы
        sound_folder = os.path.dirname(self.parent.gameinfo_path) + "/sound"
        print(f"sound_folder: {sound_folder}")
        sound_files = self.parent.open_files_dialog(title="Open WAV files", filter_str="Sounds (*.wav);;All (*)", start_dir = sound_folder, multi=True)
        print(f"sound_files: {sound_files}")
        if not sound_files: return
        
        # Отбираем хорошее от плохого
        new_sounds = []
        bad_paths = []
        already_in_list = []
        for path in sound_files:
            # Добавление пути файла в список звуков
            # Функция чтобы преобразовывать абсолютный путь файла в относительный путь
            try:
                # Проверяем, начинается ли path с папки с гейминфо
                if os.path.commonpath([self.parent.gameinfo_folder, os.path.normcase(path)]) == self.parent.gameinfo_folder:
                    try:
                        relative = os.path.relpath(path, start=self.parent.gameinfo_folder)
                        parts = relative.split(os.sep)
            
                        if parts[0].lower() == "sound":
                            # Всё, что справа от "sound"
                            path_rel = "/".join(parts[1:])
                            if path_rel not in list(self.sounds_list.get(0, tk.END)):
                                new_sounds.append(path_rel)
                            else:
                                already_in_list.append(path_rel)
                        else:
                            bad_paths.append(path)
                            continue
                    except ValueError:
                        bad_paths.append(path)
                        continue
                else:
                    bad_paths.append(path)
                    continue
            except Exception:
                bad_paths.append(path)
                continue
        print(f"new_sounds: {new_sounds}")
        print(f"bad_paths: {bad_paths}")
        print(f"already_in_list: {already_in_list}")
        
        # Добавляем новые звуки к текущему списку
        for new_sound in new_sounds: self.sounds_list.insert(tk.END, new_sound)
        
        # self.sounds_list.insert(tk.END, file_path)
        # Restore the output name
        # self.output_name_entry.delete(0, tk.END)
        # self.output_name_entry.insert(0, self.output_name)
        # pass

    def remove_selected(self, event=None):
        selected_indices = self.sounds_list.curselection()
        for index in reversed(selected_indices):
            self.sounds_list.delete(index)

    def select_all(self, event=None):
        self.sounds_list.selection_set(0, tk.END)
        return "break"  # чтобы не влияло на другие виджеты

    def on_ok(self):
        print(f"SoundsListEdit on_ok")
        print(f"self.sounds:")
        for old_sound in self.sounds:
            print(f"\t{old_sound}")
        redacted_sounds = list(self.sounds_list.get(0, tk.END))
        print(f"redacted_sounds:")
        for new_sound in redacted_sounds:
            print(f"\t{new_sound}")
        if not redacted_sounds:
            messagebox.showerror("ERROR", f"There must be at least one sound in the list!")
            return
        self.result = redacted_sounds
        self.destroy()

    def on_cancel(self):
        self.destroy()

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