#!/usr/bin/env python3

import os
import sys
import json
from tkinter import *
from tkinter import filedialog
from pathlib import Path
from pikepdf import Pdf, Encryption

class ProtectPdfsWindow:
    def __init__(self, lang_file='en.json'):

        if os.path.isfile(lang_file):
            self.lang = json.loads(open(lang_file, 'r', encoding='utf8').read())
        else:
            print(f'Error: File {lang_file} does not exist. Using default language English')
            self.lang = default_lang

        self.root = Tk()
        self.root.title(self.lang_string('window_title'))

        self.remove_password = BooleanVar()
        self.lbl_selected_dir_text = StringVar()
        self.btn_apply_text = StringVar()
        self.btn_apply_text.set(self.lang_string('add_pwd_protection'))
        self.lbl_selected_dir_text.set(self.lang_string('no_dir_selected'))

        self.frm1 = Frame()
        self.frm1.pack(anchor='w') 

        self.btn_select_dir = Button(self.frm1, text=self.lang_string('select_dir'), command=self.select_dirs)
        self.btn_select_dir.pack(side=LEFT)

        self.lbl_selected_dir = Label(self.frm1, textvariable=self.lbl_selected_dir_text)
        self.lbl_selected_dir.pack(side=TOP, expand=True)

        self.frm2 = Frame()
        self.frm2.pack(anchor='w')

        self.lbl_password = Label(self.frm2, text=self.lang_string('pwd'))
        self.lbl_password.pack(side=LEFT)

        self.ent_password = Entry(self.frm2)
        self.ent_password.pack()

        self.frm3 = Frame(self.root)
        self.frm3.pack(anchor='w')

        self.btn_apply = Button(self.frm3, textvariable=self.btn_apply_text, command=self.apply)
        self.btn_apply.pack(side=LEFT)

        self.cbtn_decrypt = Checkbutton(self.frm3, text=self.lang_string('remove_pwd_protection_checkbox'), variable=self.remove_password, command=lambda: self.btn_apply_text.set(self.lang_string('remove_pwd_protection') if self.remove_password.get() else self.lang_string('add_pwd_protection')))
        self.cbtn_decrypt.pack(expand=True)

        self.txt_info = Text(self.root, width=80, height=20)
        self.txt_info.pack(anchor='w')
        self.txt_info.insert(END, self.lang_string('will_be_applied_to_zero'))

        self.btn_quit = Button(self.root, text=self.lang_string('quit'), command=self.root.destroy)
        self.btn_quit.pack(anchor='w')

        self.root.mainloop()

    def select_dirs(self):
        self.directory = filedialog.askdirectory()
        self.txt_info.delete('1.0', END)
        self.txt_info.insert(END, self.lang_string('dirs_are_being_searched'))
        self.txt_info.update()
        self.lbl_selected_dir_text.set(self.directory)
        self.pdfs = list(map(str, Path(self.directory).rglob('*.pdf')))
        self.txt_info.delete('1.0', END)
        self.txt_info.insert(END, '\n'.join(self.pdfs) + '\n' + self.lang_string('pdfs_were_found', locals()))

    def apply(self):
        password = self.ent_password.get()
        if not password:
            print('no_pwd_provided')
            self.infoText.setText('no_pwd_provided')
            return
        self.txt_info.delete('1.0', END)
        infoText = ''
        cnt = 0
        for pdf_path in self.pdfs:
            try:
                if self.remove_password.get():
                    pdf = Pdf.open(pdf_path, password=password)
                    pdf.save(pdf_path + '.tmp')
                else:
                    pdf = Pdf.open(pdf_path)
                    # Use R=4 and not R=6 (256bit AES), since the latter cannot be read by Adobe for some reason
                    pdf.save(pdf_path + '.tmp', encryption=Encryption(owner=password, user=password, R=4))
                pdf.close()
                os.remove(pdf_path)
                os.rename(pdf_path + '.tmp', pdf_path)
                info = self.lang_string('pdfs_were_modified', locals())
                print(info)
                cnt += 1
            except Exception as e:
                info = self.lang_string('error_on_pdf_processing', locals()) + ' (' + str(e) + ')'
                print(info)
            self.txt_info.insert(END, info + '\n')
            self.txt_info.update()
        self.txt_info.insert(END, self.lang_string('done', locals()))

    def lang_string(self, s, env=globals() | locals()):
        return eval("f'" + self.lang[s] + "'", env)

default_lang = {
    "select_dir":"Select directory",
    "quit":"Quit",
    "no_dir_selected":"No directory selected",
    "will_be_applied_to_zero":"No PDFs will be modified",
    "pwd":"Password:",
    "add_pwd_protection":"Protect PDFs with password",
    "remove_pwd_protection":"Remove passwords from PDFs",
    "remove_pwd_protection_checkbox":"Remove password?",
    "pdfs_were_found":"{str(len(self.pdfs))} PDFs were found",
    "no_pwd_provided":"No password was specified",
    "dirs_are_being_searched":"Directories are being searched",
    "pdfs_were_modified":"PDF was {\"decrypted\" if self.remove_password.get() else \"encrypted\"} ({pdf_path})",
    "done":"Done: {cnt}/{len(self.pdfs)} PDFs were {\"decrypted\" if self.remove_password.get() else \"encrypted\"}",
    "error_on_pdf_processing":"An error occured while processing PDF {pdf_path}",
    "window_title":"Protect PDFs"
}

if __name__ == '__main__':
    widget = ProtectPdfsWindow('de.json')
