import os
import pickle

import tkinter as tk
from tkinter import messagebox
import face_recognition


def get_button(window, text, bg, command, fg='white'):
    button = tk.Button(
                        window,
                        text=text,
                        activebackground="black",
                        activeforeground="white",
                        fg=fg,
                        bg=bg,
                        command=command,
                        borderwidth=0,
                        font=("Segoe UI bold", 18)
                    )

    return button


def get_img_label(window):
    label = tk.Label(window)
    label.grid(row=0, column=0)
    return label


def get_text_label(window, text, background, font=("Segoe UI", 20)):
    label = tk.Label(
                     window, 
                     text=text,
                     font=font, 
                     justify="left", 
                     anchor="nw",
                     padx=0,
                     pady=0,
                     background=background
                )

    return label


def get_entry_text(window):
    inputtxt = tk.Text(
                       window,
                       height=2,
                       width=15, font=("Segoe UI", 20)
                    )
    return inputtxt


def get_message(window, text, width, background="white", foreground="black", font=("Segoe UI", 12)):
    message = tk.Message(
                        window,
                        text=text,
                        font=font,
                        background=background,
                        foreground=foreground,
                        anchor="nw",
                        justify="left",
                        padx=0,
                        pady=0,
                        width=width
                    )
    return message


def msg_box(title, description, parent=None):
    messagebox.showinfo(title=title, message=description, parent=parent)


def recognize(img, db_path):
    # it is assumed there will be at most 1 match in the db

    embeddings_unknown = face_recognition.face_encodings(img)
    if len(embeddings_unknown) == 0:
        return 'no_persons_found'
    else:
        embeddings_unknown = embeddings_unknown[0]

    db_dir = sorted(os.listdir(db_path))
    print(db_dir)

    match = False
    j = 0
    while not match and j < len(db_dir):
        path_ = os.path.join(db_path, db_dir[j])
        
        print(path_)
        file = open(path_, 'rb')
        embeddings = pickle.load(file)

        match = face_recognition.compare_faces([embeddings], embeddings_unknown)[0]
        j += 1

    if match:
        return db_dir[j - 1][:-7]
    else:
        return 'unknown_person'

