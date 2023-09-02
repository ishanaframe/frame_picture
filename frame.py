#!/usr/bin/env python3
import os
import glob
import random
import tkinter as tk
from tkinter import ttk  # Import ttk module for styled buttons
from tkinter import messagebox
import pygame
from pygame.locals import QUIT, FULLSCREEN, MOUSEBUTTONDOWN, MOUSEBUTTONUP

# Define global variables for double-click handling and slideshow status
last_click_time = 0
click_count = 0
slideshow_active = False

# Function to get media files in a folder
def get_media_files(folder_path):
    supported_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.mp4', '.avi', '.mkv']
    media_files = []
    for ext in supported_extensions:
        media_files.extend(glob.glob(os.path.join(folder_path, f'*{ext}')))
    return media_files

# Function to start the slideshow
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

    #back_button = ttk.Button(root, text="Back", command=lambda: close_slideshow(), style="Rounded.TButton")
    exit_button = ttk.Button(root, text="Exit", command=exit_application, style="Rounded.TButton")

    #back_button.place(relx=0.05, rely=0.05, anchor="nw")
    exit_button.place(relx=0.95, rely=0.95, anchor="se")

    global last_click_time, click_count

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Pause/unpause on single click
                if paused:
                    paused = False
                else:
                    paused = True
                    pygame.time.delay(1000)  # Delay to avoid registering a single click as a double click
                # Check for double-click
                current_time = pygame.time.get_ticks()
                if current_time - last_click_time < 500:
                    # This is a double-click, go back to the homepage
                    close_slideshow()
                else:
                    # This is a single-click, update last click time
                    last_click_time = current_time
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                click_count += 1

        if click_count > 1:
            # Reset click count after a double-click
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
            pygame.time.delay(3000)  # Delay between media files

            current_index += 1
            if current_index >= len(media_files):
                current_index = 0

    pygame.quit()
    slideshow_active = False

# Function to create a slideshow
def create_slideshow(folder_path):
    root.withdraw()  # Hide the main homescreen window
    main(folder_path)

# Function to close the slideshow and return to the homescreen
def close_slideshow():
    pygame.quit()
    global slideshow_active
    slideshow_active = False
    root.deiconify()  # Show the main homescreen window

# Function to create the homescreen
def create_homescreen(current_folder=None):
    global root
    root = tk.Tk()
    root.title("Folder Slideshow")
    root.attributes('-fullscreen', True)  # Set the window to fullscreen
    root.configure(bg="black")

    # Create a frame to center the folder buttons
    frame = tk.Frame(root, bg="black")
    frame.pack(expand=True, fill="both")

    # List all folders except the Python file's directory and .git folders
    folders = [folder for folder in os.listdir() if os.path.isdir(folder) and folder != "__pycache__" and not folder.startswith(".git")]

    # Create buttons for each folder with rounded edges and spacing
    folder_buttons = []
    for folder in folders:
        button = ttk.Button(frame, text=folder, command=lambda f=folder: create_slideshow(f), style="Rounded.TButton")
        folder_buttons.append(button)

    # Create a custom ttk style for rounded buttons
    s = ttk.Style()
    s.configure("Rounded.TButton", padding=10, relief="raised", borderwidth=4, font=("Helvetica", 16))

    # Place folder buttons in a grid with spacing
    row, col = 0, 0
    for i, button in enumerate(folder_buttons):
        button.grid(row=row, column=col, padx=10, pady=10)
        col += 1
        if col >= 4:
            col = 0
            row += 1

    # Create and place the "Exit" button at the bottom-right corner
    exit_button = ttk.Button(root, text="Exit", command=exit_application, style="Rounded.TButton")
    exit_button.place(relx=0.95, rely=0.95, anchor="se")

    root.mainloop()

# Function to exit the application
def exit_application():
    result = messagebox.askquestion("Exit Application", "Are you sure you want to exit?")
    if result == 'yes':
        if slideshow_active:
            pygame.quit()
        root.destroy()

# Create the initial homescreen
create_homescreen()
