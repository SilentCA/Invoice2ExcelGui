import pathlib
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
import pygubu

import logging
import pathlib
import Invoice2Excel
import pandas as pd
import openpyxl
import os


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
PROJECT_UI = PROJECT_PATH / "Invoice2ExcelApp.ui"


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
        self.filenamesVar = tk.StringVar()
        self.filenum = tk.IntVar()
        builder.import_variables(self, ['in_path', 'out_path', 'is_mode_append', 'filenamesVar', 'filenum'])

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
        filenames = list(pathlib.Path(dirname).rglob('*.pdf')) 
        self.filenamesVar.set(filenames)
        self.filenum.set(len(filenames))

    def on_button_select_in_files_clicked(self):
        filenames = filedialog.askopenfilenames(filetypes=[('PDF','*.pdf')])
        self.filenamesVar.set(filenames)
        self.filenum.set(len(filenames))

    def on_button_select_out_path_clicked(self):
        filepath = filedialog.asksaveasfilename(filetypes=[('Excel','*.xlsx')], defaultextension='xlsx')
        self.out_path.set(filepath)

    def on_button_run_clicked(self):
        is_mode_append = self.is_mode_append.get()
        in_path = self.in_path.get()
        out_path = self.out_path.get()
        logger.info("处理开始")
        logger.info(f"\n\t附加模式: {is_mode_append}\n\t发票目录: {in_path}\n\t保存路径: {out_path}")
        logger.info('正在处理中请稍后...')
        write_mode = 'append' if is_mode_append else 'write'
        self.invoice2excel(eval(self.filenamesVar.get()), out_path, write_mode)
        logger.info('处理结束\n')
        messagebox.showinfo(message='处理完成')

    def invoice2excel(self, filenames:list, out_path:str, write_mode:str):
        num = len(filenames)
        logger.info(f'Total files to parse: {num}.')
        data = pd.DataFrame()
        for idx, f in enumerate(filenames):
            logger.info(f'{idx+1}/{num}({round((idx+1)/num*100)}%)\t{f}')
            extractor = Invoice2Excel.Extractor(f)
            try:
                d = extractor.extract()
                df_item = pd.DataFrame()
                df_item.loc[0, '发票文件'] = f'=HYPERLINK("{os.path.abspath(f)}","{f}")'
                d = pd.concat([d, df_item], axis=1)
                data = pd.concat([data, d], axis=0, sort=False, ignore_index=True)
            except Exception as e:
                logger.error('File error:', f, '\n', e)
            self.builder.get_object('progressbar1').step(100/num)

        logger.info(f'Finish parsing, save data to {out_path}')
        if write_mode == 'write':
            data.to_excel(out_path, sheet_name='data')
        elif write_mode == 'append':
            wb = openpyxl.load_workbook(out_path)
            ws = wb['data']
            # skip header and a blank row next to header
            rows = openpyxl.utils.dataframe.dataframe_to_rows(data, header=False)
            rows.__next__()
            for r in rows:
                ws.append(r)
            wb.save(out_path)
        logger.info(f'All Done.')


if __name__ == '__main__':
    app = Invoice2ExcelApp()
    app.run()

