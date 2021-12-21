import pathlib
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import pygubu

import logging
import Invoice2Excel


# Configure logging
logger = logging.getLogger(name=__name__)
logger.setLevel(logging.INFO)
format_str = logging.Formatter('%(asctime)s - %(message)s')
# add stream and file logging
fh = logging.FileHandler('log.txt')
# ch = logging.StreamHandler()
fh.setFormatter(format_str)
# ch.setFormatter(format_str)
logger.addHandler(fh)
# logger.addHandler(ch)


PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "invoice2Excel.ui"


class TkTextHandler(logging.Handler):
    def __init__(self, tkText):
        logging.Handler.__init__(self)
        self.tkText = tkText

    def emit(self, record):
        msg = self.format(record)
        self.tkText.configure(state='normal')
        self.tkText.insert(tk.END, msg + '\n')
        # scroll to the bottom
        self.tkText.see(tk.END)
        self.tkText.configure(state='disabled')
        self.tkText.update()


class Invoice2ExcelApp:
    def __init__(self, master=None):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.mainwindow = builder.get_object('mainwindow', master)

        self.in_path = tk.StringVar()
        self.out_path = tk.StringVar()
        self.is_mode_append = tk.BooleanVar()
        builder.import_variables(self, ['in_path', 'out_path', 'is_mode_append'])

        builder.connect_callbacks(self)
        
        # add tk text logging
        text_handler = TkTextHandler(self.builder.get_object('text_log'))
        text_handler.setFormatter(format_str)
        logger.addHandler(text_handler)

    def run(self):
        self.mainwindow.mainloop()

    def on_button_select_in_path_clicked(self):
        dirname = filedialog.askdirectory()
        self.in_path.set(dirname)

    def on_button_select_out_path_clicked(self):
        filepath = filedialog.asksaveasfilename(filetypes=[('Excel','*.xlsx')], defaultextension='xlsx')
        self.out_path.set(filepath)

    def on_button_run_clicked(self):
        is_mode_append = self.is_mode_append.get()
        in_path = self.in_path.get()
        out_path = self.out_path.get()
        logger.info("处理开始")
        logger.info(f"附加模式: {is_mode_append}\n发票目录: {in_path}\n保存路径: {out_path}")
        write_mode = 'append' if is_mode_append else 'write'
        Invoice2Excel.invoice2Excel(in_path, out_path, write_mode)
        logger.info('处理结束\n')


if __name__ == '__main__':
    app = Invoice2ExcelApp()
    app.run()

