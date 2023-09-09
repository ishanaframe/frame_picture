#!/usr/bin/env python3

import os
import glob
import random
import tkinter as tk
from tkinter import ttk  # Import ttk module for styled buttons
from tkinter import messagebox
import pygame
from pygame.locals import QUIT, FULLSCREEN, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from PIL import Image, ImageTk
import subprocess
import sys
import socket

# Define global variables for double-click handling and slideshow status
last_click_time = 0
click_count = 0
slideshow_active = False
root = None

def get_media_files(folder_path):
    supported_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.mp4', '.avi', '.mkv']
    media_files = []
    for ext in supported_extensions:
        media_files.extend(glob.glob(os.path.join(folder_path, f'*{ext}')))
    return media_files

def is_connected():
    """Check if there's an internet connection."""
    try:
        # Connect to the host -- tells us if the host is actually reachable
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False

def import_and_restart():
    # Check internet connection
    if not is_connected():
        messagebox.showerror("Error", "No internet connection found")
        return

    # Run the git pull command
    try:
        os.chdir("/home/admin/Desktop/frame_picture")
        subprocess.check_call(["git", "pull", "https://github.com/ishanaframe/frame_picture.git"])
    except subprocess.CalledProcessError as e:
        print(f"Error during git pull: {e}")
        return

    # Restart the application
    python = sys.executable
    os.execl(python, python, *sys.argv)



def main(folder_path):
    global slideshow_active
    slideshow_active = True

    pygame.init()

    screen_info = pygame.display.Info()
    screen_width, screen_height = screen_info.current_w, screen_info.current_h

    pygame.display.set_caption("Folder Slideshow")

    pygame.display.set_mode((0, 0), FULLSCREEN)
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()
    running = True
    paused = False

    media_files = get_media_files(folder_path)
    if not media_files:
        print(f"No supported media files found in '{folder_path}'.")
        pygame.quit()
        return

    random.shuffle(media_files)
    current_index = 0

    #exit_button = ttk.Button(root, text="Exit", command=exit_application, style="Rounded.TButton")
    #exit_button.place(relx=0.95, rely=0.95, anchor="se")

    global last_click_time, click_count

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                if paused:
                    paused = False
                else:
                    paused = True
                    pygame.time.delay(1000)
                current_time = pygame.time.get_ticks()
                if current_time - last_click_time < 500:
                    close_slideshow()
                else:
                    last_click_time = current_time
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                click_count += 1

        if click_count > 1:
            click_count = 0

        if not paused:
            media_file = media_files[current_index]
            extension = os.path.splitext(media_file)[1].lower()

            screen.fill((0, 0, 0))

            if extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                image = pygame.image.load(media_file)
                image_width, image_height = image.get_size()

                if image_width > screen_width or image_height > screen_height:
                    ratio = min(screen_width / image_width, screen_height / image_height)
                    new_width = int(image_width * ratio)
                    new_height = int(image_height * ratio)
                    image = pygame.transform.scale(image, (new_width, new_height))

                screen.blit(image, ((screen_width - image.get_width()) // 2, (screen_height - image.get_height()) // 2))
            elif extension in ['.mp4', '.avi', '.mkv']:
                video = pygame.movie.Movie(media_file)
                video.set_display(screen, pygame.Rect(0, 0, screen_width, screen_height))
                video.play()

            pygame.display.flip()
            pygame.time.delay(3000)

            current_index += 1
            if current_index >= len(media_files):
                current_index = 0

    pygame.quit()
    slideshow_active = False

loading_label = None  # Global variable to hold the loading GIF label

def show_loading():
    global loading_label
    gif = tk.PhotoImage(file="loading.gif")  # Assuming the GIF is in the same directory as the script
    loading_label = tk.Label(root, image=gif, bg="#E2D1F9")
    loading_label.image = gif
    loading_label.place(relx=0.5, rely=0.5, anchor="center")
    root.update()  # Update the GUI to display the GIF immediately

def hide_loading():
    global loading_label
    if loading_label:
        loading_label.destroy() 


def delayed_start_slideshow(folder_path):
    hide_loading()
    main(folder_path)
    update_avatar()  # Update the avatar when returning to the homescreen
    root.deiconify()

def create_slideshow(folder_path):
    show_loading()  # Show the loading GIF
    root.after(500, lambda: delayed_start_slideshow(folder_path))  # Delay the start of the slideshow by 500ms



def close_slideshow():
    pygame.quit()
    global slideshow_active
    slideshow_active = False
    update_avatar()
    root.deiconify()

def update_avatar():
    avatar_folder = "avatar"
    avatar_files = glob.glob(os.path.join(avatar_folder, "*.png")) + glob.glob(os.path.join(avatar_folder, "*.jpg"))
    random_avatar = random.choice(avatar_files)
    
    image = Image.open(random_avatar)
    avatar_image = ImageTk.PhotoImage(image)
    
    avatar_label.config(image=avatar_image)
    avatar_label.image = avatar_image

exit_button = None  # Define a global variable for the exit button

def create_homescreen(current_folder=None):
    global root, exit_button
    if not root:
        root = tk.Tk()
        root.title("Folder Slideshow")
        root.attributes('-fullscreen', True)
        root.configure(bg="#E2D1F9")

        global avatar_label
        avatar_label = tk.Label(root, bg="#E2D1F9")
        avatar_label.place(relx=0.25, rely=0.5, anchor="center", relwidth=0.45, relheight=0.9)  # Adjusted size for offset

    update_avatar()

    frame = tk.Frame(root, bg="#E2D1F9")
    frame.place(relx=0.6, rely=0.1, anchor="nw")

    # Ignoring the 'avatar' folder
    folders = [folder for folder in os.listdir() if os.path.isdir(folder) and folder not in ["__pycache__", ".git", "avatar"]]

    for idx, folder in enumerate(folders):
        button = ttk.Button(frame, text=folder, command=lambda f=folder: create_slideshow(f), style="Custom.TButton")
        button.grid(row=idx, column=0, padx=10, pady=10, sticky="w")

    s = ttk.Style()
    s.configure("Custom.TButton", padding=10, relief="raised", borderwidth=4, font=("Helvetica", 16), background="#317773", foreground="black")

    # Destroy the previous exit button if it exists
    if exit_button:
        exit_button.destroy()

    exit_button = ttk.Button(root, text="Exit", command=root.destroy, style="Custom.TButton")  # Directly destroy the root without confirmation
    exit_button.place(relx=0.95, rely=0.95, anchor="se")

    # Create and place the "Import" button next to the "Exit" button
    import_button = ttk.Button(root, text="Import", command=import_and_restart, style="Custom.TButton")
    import_button.place(relx=0.82, rely=0.95, anchor="se")  # Adjusted the relx value for spacing


    root.mainloop()


def exit_application():
    result = messagebox.askquestion("Exit Application", "Are you sure you want to exit?")
    if result == 'yes':
        if slideshow_active:
            pygame.quit()
        root.destroy()

create_homescreen()
