import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from tksheet import Sheet
import json
from pathlib import Path
import re
from typing import List, Dict, Any

# Основные константы на чтение
ABOUT_TOOL_VERSION = "0.0.7"
ABOUT_TOOL_NAME = f"Soundscripts Editor v{ABOUT_TOOL_VERSION}"
ABOUT_TOOL_DESCRIPTION = "This tool helps to edit soundscripts files used on Source Engine."
ABOUT_TOOL_AUTHOR = "Shitcoded by Ambiabstract (Sergey Shavin)."
ABOUT_TOOL_REQUESTED = "Requested by Aptekarr."
ABOUT_TOOL_LINK = "Github: https://github.com/Ambiabstract/soundscripts_editor"
ABOUT_TOOL_DISCORD = "Discord: @Ambiabstract"
WINDOW_SIZE = "1024x720"
COLUMN_WIDTHS = [(0, 200), (1, 100), (2, 100), (3, 100), (4, 100), (5, 385)]
HEADERS = ["entry.name", "channel", "soundlevel", "volume", "pitch", "sounds"]
BASE_ROW_HEIGHT = 22
DEFAULT_CHANNEL = "CHAN_AUTO"
DEFAULT_SOUNDLEVEL = "SNDLVL_NORM"
DEFAULT_VOLUME = "VOL_NORM"
DEFAULT_PITCH = "PITCH_NORM"
CACHE_PATH = "soundscripts_editor_cache.json"

# Класс приложения
class App(TkinterDnD.Tk):
    # Конструктор класса - метод, который задаёт начальное состояние объекта сразу после его создания
    def __init__(self):
        super().__init__() # вызывает конструктор родительского класса TkinterDnD.Tk чтобы всё работало
        
        # Основные переменные класса
        self.title(f"{ABOUT_TOOL_NAME}")
        self.geometry(WINDOW_SIZE)
        self.resizable(False, False)
        self.items = []  # список словарей в котором хранятся все нужные нам ноды
        self.gameinfo_path = None
        self.gameinfo_folder = None
        self.project_name = None
        self.soundscript_path = None
        self.soundscript_name = None
        self.soundscript_saved = False

        # Строим визуалочку окна, тулбара, нижней строчки
        self.build_main_ui()
        
        gameinfo_path = self.load_cache()
        if gameinfo_path:
            # print(f"gameinfo_path from cache: {gameinfo_path}")
            self.gameinfo_path = gameinfo_path
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
        self.btn_save_ss = ttk.Button(self.toolbar, text="Save Soundscript As", command=self.save_soundscript, state="disabled")
        self.btn_save_ss.pack(
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
    def on_double_click(self, event=None):
        print(f"Double click!")
        sel = self.sheet.get_currently_selected()
        print(f"sel: {sel}")
        row = sel.get("row")
        print(f"row: {row}")

    # Метод для загрузки кэша из файла
    def load_cache(self) -> str | None:
        cache_path = Path(CACHE_PATH)
        if not cache_path.exists():
            return None
        # print(f"cache_path: {cache_path}")
        try:
            gameinfo_path = Path(json.loads(cache_path.read_text(encoding="utf-8"))[0].get("gameinfo_path"))
            # print(f"gameinfo_path: {gameinfo_path}")
            if gameinfo_path.exists(): return gameinfo_path
            return None
        except Exception as e:
            print(f"Failed to load cache!")
            print(f"Exception:")
            print(e)
            return None
    
    # Метод для сохранения кэша в файл
    def save_cache(self) -> bool:
        json_dumps_content = [
            {"gameinfo_path": str(self.gameinfo_path)}
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
    def save_soundscript(self):
        scripts_folder = os.path.dirname(self.gameinfo_path) + "/scripts"
        ss_name = self.project_name.split()[0].lower() + "_" + "soundscript"
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
        self.title(f"{ABOUT_TOOL_NAME} | {self.project_name} - {self.soundscript_name}")
        self.soundscript_saved = True
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