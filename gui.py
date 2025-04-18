import customtkinter
from tkinter import filedialog, messagebox
import threading, os, requests
import webbrowser

import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller EXE """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


track_title = ''
auto_save = False
file_path = None

def internet_connection():
    try:
        requests.get('https://www.google.com', timeout=5)
        return True
    except requests.ConnectionError:
        return False


path = os.path.join(os.path.expanduser("~"), "Desktop", "LyricsFusionLyrics")
def folder_path():
    if not os.path.exists(path):
        os.mkdir(path)
    return path
folder_path()


def check_auto_save():
    global auto_save
    val = auto_save_checkBox.get()
    if val == 'on':
        auto_save = True
        print("Auto save Lyrics enable")
    else:
        auto_save = False
        print("Auto save Lyrics disabled")


def open_in_browser(website):
    artist_name = artist_name_entry.get()
    track_name = track_name_entry.get()
    site = website
    if not (artist_name and track_name):
        return None 
    try:
        if site.lower() == 'spotify':
         spotify_url = f"https://open.spotify.com/search/{artist_name} {track_name}"
         webbrowser.open_new_tab(spotify_url)
        elif site.lower() == 'youtube':
         yt_url = f"https://www.youtube.com/results?search_query={artist_name} {track_name}"
         webbrowser.open_new_tab(yt_url)
    except Exception as e:
        messagebox.showerror(title="Failed to open browser",message=f"An error occured: \n {e}")






def search_handler():
    global track_title
    artist_name = artist_name_entry.get().strip()
    track_name = track_name_entry.get().strip()

    if not (artist_name and track_name):
        messagebox.showwarning(title="Invalid input", message="Both artist name and track name are required")
        feedback_label.configure(text="Both artist name and track name are required", text_color="#DE3163")
        return None
    threading.Thread(target=internet_connection).start()
    submit_btn.configure(state="disabled")

    # if not internet_connection():
    #     submit_btn.configure(state="disabled")
    #     feedback_label.configure(text="No internet connection. Please check your connection.",text_color="#DE3163")
    #     messagebox.showwarning(title='No internet', message='No internet connection. Please check your connection.')
    #     return  None

    def search():
            try:
                global auto_save
                from scraper import scrape_lyrics
                feedback_label.configure(text=f"Searching for: {track_name} by {artist_name}")
                results = scrape_lyrics(artist_name, track_name)
                if results:
                    feedback_label.configure(text="Lyrics found!")
                    textarea.delete("1.0", "end")
                    track_title: object = results['track_title']
                    root.title(f"LyricsFusion - {track_title}")
                    textarea.insert("1.0", results['lyrics'])
                    if auto_save:
                        threading.Thread(target=save_file).start()
                else:
                    feedback_label.configure(text="Lyrics not found" , text_color="#DE3163")
            except Exception as e:
                print(f"An error occurred: {e}")
                feedback_label.configure(text="Failed to fetch lyrics", text_color="#DE3163")
            finally:
                submit_btn.configure(state="normal")

    threading.Thread(target=search).start()





def combobox_callback(option):
    action = option.lower()
    if action == 'open file':
        threading.Thread(target=open_file, daemon=True).start()
    elif action == 'save file':
        threading.Thread(target=save_file).start()
    elif action == 'save as...':
        threading.Thread(target=save_as_file).start()
    elif action == 'exit':
        root.destroy()




def save_as_file():
    global file_path
    content = textarea.get("1.0", "end-1c")
    if not content.strip():
        feedback_label.configure(text="Nothing to save",text_color='#F88379')
        return print("Nothing to save")

    try:
        file = filedialog.asksaveasfilename(
            title="Save as file...",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file:
            with open(file,mode='w',encoding='utf-8') as f:
                f.write(str(content))
            print("File saved")
            feedback_label.configure(text=f"Saved as:  {os.path.basename(file_path)}")
            return None
        else:
            feedback_label.configure(text="Save canceled",text_color='#F88379')
            return None
    except Exception as e:
        print(f"Failed to save file: {e}")
        messagebox.showerror(title="Save Error", message=str(e))
        return None


def open_file():
    global file_path
    try:
        file_path = filedialog.askopenfilename(
            title="Open file",
            defaultextension=".txt",
            initialdir=folder_path(),
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            file_name = os.path.basename(file_path)
            root.title(f"LyricsFusion - {file_name}")
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                textarea.delete("1.0", "end")
                textarea.insert("1.0", content)
            feedback_label.configure(text="File opened")
        else:
            feedback_label.configure(text="No file selected",text_color='#F88379')
    except Exception as e:
        messagebox.showerror(title="Open Error", message=str(e))

def save_file():
    global file_path
    try:
        folder_path()
        content = textarea.get("1.0", "end-1c")
        if not content.strip():
            feedback_label.configure(text="Nothing to save",text_color='#F88379')
            return
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        else:
            filename = artist_name_entry.get().strip() + "-" + track_name_entry.get().strip()
            file_path = os.path.join(path, f"{filename}.txt")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        feedback_label.configure(text="File saved to")
        root.title(f"LyricsFusion - {track_title}| File saved to: {file_path}")
    except Exception as e:
        messagebox.showerror(title="Save Error", message=str(e))
        print(f"Failed to save file: {e}")

# === GUI Layout ===

customtkinter.set_appearance_mode('dark')
customtkinter.set_default_color_theme('green')

root = customtkinter.CTk()
root.title("LyricsFusion")

root.iconbitmap(resource_path("lyricsfusion.ico"))

root.geometry('870x500')
frame = customtkinter.CTkFrame(root, width=860, height=490)
frame.grid(row=0, column=0, pady=5, padx=5, sticky='nsew')

title = customtkinter.CTkLabel(frame, text='LyricsFusion', font=('Arial Bold', 35))
title.place(y=50, x=70)


optionMenu = customtkinter.CTkOptionMenu(frame,
    values=["Open file", 
            "Save file", 
            "Save as...",
              "Exit"],
    command=combobox_callback)
optionMenu.set("File")
optionMenu.place(y=5, x=5)



textarea = customtkinter.CTkTextbox(frame,
                                   height=480,
                                   width=470,
                                   text_color="#F8F8FF",
                                   activate_scrollbars=True,
                                   wrap="word")
textarea.place(x=380, y=5)

artist_name_entry = customtkinter.CTkEntry(frame, placeholder_text="Enter artist name",placeholder_text_color='#E0FFFF')
artist_name_entry.configure(width=330, height=40)
artist_name_entry.place(y=150, x=20)

track_name_entry = customtkinter.CTkEntry(frame, placeholder_text="Enter track name",placeholder_text_color='#E0FFFF')
track_name_entry.configure(width=330, height=40)
track_name_entry.place(y=250, x=20)

feedback_label = customtkinter.CTkLabel(frame, text='Searching for lyrics', anchor='n')
feedback_label.place(y=320, x=50)

submit_btn = customtkinter.CTkButton(frame,
                                     text="Search for lyrics",
                                     command=search_handler)
submit_btn.place(y=350, x=20)
submit_btn.configure(width=330, height=40)

auto_save_var = customtkinter.StringVar(value='off')

auto_save_checkBox = customtkinter.CTkCheckBox(frame,text="Auto save Lyrics",
                                            checkbox_width=15,
                                            checkbox_height=15,
                                            border_width=1,
                                            variable=auto_save_var,
                                            onvalue='on',
                                            offvalue='off',
                                            command=check_auto_save
                                            )
auto_save_checkBox.place(y=440,x=20)

open_in_label = customtkinter.CTkLabel(root,text="Open: ")

open_in_label.place(y=410,x=20)

spotify_label = customtkinter.CTkButton(root,
                text="Spotify",
                fg_color="#262626",
                text_color="#0FFFFF",
                hover_color="#232323",
                width=34,
                command=lambda:open_in_browser("spotify")
                )
spotify_label.place(y=410,x=70)

yt_label = customtkinter.CTkButton(root,
                text="YouTube",
                fg_color="#262626",
                text_color="#0FFFFF",
                hover_color="#232323",
                width=34,
                command=lambda:open_in_browser("youtube")
                )
yt_label.place(y=410,x=135)




root.resizable(False, False)
root.mainloop()


