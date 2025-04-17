from tkinter import Tk, Canvas, Entry, Text, Button, Scrollbar, Menu, filedialog, messagebox
from main import scrape_lyrics
from threading import Thread
from time import sleep
import os

# Initialize main window
window = Tk()
window.title("LyricsFusion")
window.geometry("1000x540")
window.resizable(False, False)
window.configure(bg="#F4F6F8")  # Soft gray-blue background

# ========== GUI COMPONENTS ========== #

canvas = Canvas(window, bg="#F4F6F8", height=668, width=1209, bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)




# Headings
canvas.create_text(144.0, 22.0, anchor="nw", text="LyricsFusion", fill="#1B1A55", font=("Impact", 40 * -1))



# Labels
canvas.create_text(103.0, 128.0, anchor="nw", text="Enter the artist name", fill="#333333", font=("Comfortaa", 15 * -1))
canvas.create_text(103.0, 235.0, anchor="nw", text="Enter the track name", fill="#333333", font=("Comfortaa", 15 * -1))


# Status text
status_text = canvas.create_text(220.0, 340.0, anchor="nw", text="", fill="#6C63FF", font=("Inter", 15 * -1))

# Input Fields
# Entry fields
entry_bg = "#FFFFFF"
entry_border = "#CCCCCC"
entry_text = "#333333"

artist_name = Entry(bd=1, bg=entry_bg, fg=entry_text, 
                    highlightthickness=1, 
                    highlightbackground=entry_border,
                      font=("Comfortaa", 15 * -1))
artist_name.place(x=103.0, y=160.0, width=330.0, height=40.0)


track_name = Entry(bd=1, bg=entry_bg, fg=entry_text, 
                   highlightthickness=1, 
                   highlightbackground=entry_border,
                   font=("Comfortaa", 15 * -1))
track_name.place(x=103.0, y=270.0, width=330.0, height=40.0)

# Lyrics Display Container

lyricsContainer = Text(
    bd=0,
    bg="#F4F6F8",  # White background for clarity
    fg="#000716",
    highlightthickness=0,
    highlightbackground="#CCCCCC",
    font=("Consolas", 14 * -1),
    wrap="word",
    cursor="arrow",
    selectbackground="#AAB2FF",
    selectforeground="#000716",
    insertbackground="#000716",
    undo=True
)
lyricsContainer.config(padx=10, pady=10)
lyricsContainer.place(x=480, y=11.0, width=500, height=520)
lyricsContainer.insert("1.0", "Lyrics will appear here...")















# Scrollbar
scrollbar = Scrollbar(lyricsContainer)
scrollbar.pack(side="right", fill="y")
scrollbar.place(x=475, y=3, width=20, height=500)
scrollbar.config(command=lyricsContainer.yview)
lyricsContainer.config(yscrollcommand=scrollbar.set)

# ========== CORE FUNCTIONS ========== #

def create_lyrics_folder():
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    folder_path = os.path.join(desktop, "LyricsFusionFolder")
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def save_lyrics():
    lyrics = lyricsContainer.get("1.0", "end-1c")
    if lyrics.strip():
        folder_path = create_lyrics_folder()
        file_name = f"{track_name.get()} - {artist_name.get()}.txt"
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(lyrics)
        messagebox.showinfo("Success", f"Lyrics saved to {file_path}")
    else:
        messagebox.showerror("Error", "No lyrics to save.")

def open_lyrics():
    folder_path = create_lyrics_folder()
    file_path = filedialog.askopenfilename(initialdir=folder_path, title="Select a file",
                                           filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as file:
            lyrics = file.read()
        lyricsContainer.delete("1.0", "end")
        lyricsContainer.insert("1.0", lyrics)

def scrape_lyrics_handler():
    track = track_name.get()
    artist = artist_name.get()

    if not (track and artist):
        messagebox.showerror("Error", "Please enter both artist and track names.")
        lyricsContainer.delete("1.0", "end")
        lyricsContainer.insert("1.0", "Lyrics will appear here...")
        return

    # Status animation
    def animate_loading():
        for i in range(3):
            canvas.itemconfig(status_text, text=f"Searching for lyrics{'.' * i}")
            window.update()
            sleep(0.5)

    def enable_button():
        sleep(0.5)
        button_1.config(state="normal")
        canvas.itemconfig(status_text, text="")

    def search():
        try:
            lyrics = scrape_lyrics(artist, track)
            if lyrics:
                window.title(f"LyricsFusion - {lyrics['track_title']}")
                lyricsContainer.delete("1.0", "end")
                lyricsContainer.insert("1.0", lyrics['lyrics'])
                lyricsContainer.config(state="normal")
                canvas.itemconfig(status_text, text="Lyrics found!")
            else:
                messagebox.showerror("Error", "Lyrics not found.")
                lyricsContainer.delete("1.0", "end")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch lyrics.\n{e}")
        finally:
            enable_button()

    animate_loading()
    button_1.config(state="disabled")
    Thread(target=search).start()

# ========== UI ACTIONS ========== #

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        window.destroy()

# Button

button_1 = Button(
    text="Search for lyrics",
    borderwidth=0,
    highlightthickness=0,
    font=("Comfortaa", 15 * -1),
    command=scrape_lyrics_handler,
    relief="flat",
    cursor="hand2",
    bg="#6C63FF",  # Primary purple
    fg="#FFFFFF",
    activebackground="#574FCF",  # Slightly darker on hover
    activeforeground="#FFFFFF"
)

button_1.place(x=108.0, y=370.0, width=300.0, height=45)

# Menu Bar
menu_bar = Menu(window)
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Save", command=save_lyrics)
file_menu.add_command(label="Open", command=open_lyrics)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=window.quit)
menu_bar.add_cascade(label="File", menu=file_menu)
window.config(menu=menu_bar)

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()
window.destroy()
# End of GUI code
# Note: The scrape_lyrics function is assumed to be defined in the main.py file.
# Ensure that the main.py file is in the same directory as this script.
# The scrape_lyrics function should handle the actual web scraping logic.
# The GUI is built using Tkinter and provides a user-friendly interface for searching and saving lyrics.
# The lyrics are displayed in a Text widget with a scrollbar for easy navigation.
# The application also includes error handling and user feedback through message boxes.
# The lyrics folder is created on the user's desktop to store saved lyrics.
