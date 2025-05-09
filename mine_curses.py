import tkinter as tk
from tkinter import ttk, messagebox
import minecraft_launcher_lib
import subprocess
import sys
import uuid
import threading
import time


class MinecraftLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Launcher")
        self.root.geometry("600x400")
        
        self.minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
        self.selected_version = None
        self.username = "Player"
        self.login_data = None
        self.progress = {"max": 0, "current": 0, "status": "", "error": None}
        self.lock = threading.Lock()
        
        self.container = tk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        self.current_frame = None
        self.show_main_menu()

    def show_main_menu(self):
        if self.current_frame:
            self.current_frame.destroy()
        
        frame = tk.Frame(self.container)
        
        tk.Label(frame, text="Minecraft Launcher", font=("Helvetica", 16, "bold")).pack(pady=20)
        
        menu_items = [
            ("Play", self.launch_game),
            ("Select Version", self.show_version_select),
            ("Install Version", self.show_install_version),
            ("Microsoft Login", self.microsoft_login),
            ("Set Username", self.show_set_username),
            ("Quit", self.root.destroy)
        ]
        
        for text, command in menu_items:
            btn = tk.Button(frame, text=text, width=20, command=command)
            btn.pack(pady=5)
        
        self.current_frame = frame
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_version_select(self):
        self.refresh_installed_versions()
        
        if self.current_frame:
            self.current_frame.destroy()
        
        frame = tk.Frame(self.container)
        
        tk.Label(frame, text="Select Version", font=("Helvetica", 14)).pack(pady=10)
        
        listbox = tk.Listbox(frame, width=50, height=15)
        listbox.pack(pady=10)
        
        for version in self.installed_versions:
            listbox.insert(tk.END, f"{version['id']} ({version['type']})")
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Select", command=lambda: self.select_version(listbox)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Back", command=self.show_main_menu).pack(side=tk.RIGHT, padx=10)
        
        self.current_frame = frame
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def select_version(self, listbox):
        selection = listbox.curselection()
        if not selection:
            return
        
        self.selected_version = self.installed_versions[selection[0]]['id']
        self.show_main_menu()

    def refresh_installed_versions(self):
        self.installed_versions = minecraft_launcher_lib.utils.get_installed_versions(self.minecraft_directory)

    def show_install_version(self):
        if self.current_frame:
            self.current_frame.destroy()
        
        frame = tk.Frame(self.container)
        
        tk.Label(frame, text="Install Version", font=("Helvetica", 14)).pack(pady=10)
        
        self.install_listbox = tk.Listbox(frame, width=50, height=15)
        self.install_listbox.pack(pady=10)
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Install", command=self.start_installation).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Back", command=self.show_main_menu).pack(side=tk.RIGHT, padx=10)
        
        self.current_frame = frame
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        
        self.populate_available_versions()

    def populate_available_versions(self):
        def fetch_versions():
            try:
                versions = minecraft_launcher_lib.utils.get_available_versions(self.minecraft_directory)
                self.root.after(0, lambda: self.update_install_listbox(versions))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        
        threading.Thread(target=fetch_versions).start()

    def update_install_listbox(self, versions):
        self.install_listbox.delete(0, tk.END)
        for version in versions:
            self.install_listbox.insert(tk.END, f"{version['id']} ({version['type']})")

    def start_installation(self):
        selection = self.install_listbox.curselection()
        if not selection:
            return
        
        version = self.install_listbox.get(selection[0]).split(" ")[0]
        self.show_progress_screen(version)

    def show_progress_screen(self, version):
        if self.current_frame:
            self.current_frame.destroy()
        
        frame = tk.Frame(self.container)
        
        self.progress_label = tk.Label(frame, text="Starting installation...", font=("Helvetica", 12))
        self.progress_label.pack(pady=20)
        
        self.progress_bar = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress_bar.pack(pady=10)
        
        self.cancel_btn = tk.Button(frame, text="Cancel", command=self.show_main_menu)
        self.cancel_btn.pack(pady=10)
        
        self.current_frame = frame
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        
        self.run_installation(version)

    def run_installation(self, version):
        install_thread = threading.Thread(target=self.install_version_thread, args=(version,))
        install_thread.start()
        self.monitor_progress(install_thread)

    def monitor_progress(self, thread):
        if thread.is_alive():
            self.update_progress()
            self.root.after(100, lambda: self.monitor_progress(thread))
        else:
            if self.progress["error"]:
                messagebox.showerror("Error", self.progress["error"])
            else:
                messagebox.showinfo("Success", "Installation completed successfully!")
            self.show_main_menu()

    def update_progress(self):
        with self.lock:
            self.progress_label.config(text=self.progress["status"])
            self.progress_bar["maximum"] = self.progress["max"] if self.progress["max"] > 0 else 1
            self.progress_bar["value"] = self.progress["current"]

    def install_version_thread(self, version):
        def callback(status, progress, max_progress):
            with self.lock:
                self.progress["status"] = status
                self.progress["current"] = progress
                self.progress["max"] = max_progress
        
        try:
            minecraft_launcher_lib.install.install_minecraft_version(
                version, self.minecraft_directory, callback=callback
            )
        except Exception as e:
            with self.lock:
                self.progress["error"] = str(e)

    def show_set_username(self):
        if self.current_frame:
            self.current_frame.destroy()
        
        frame = tk.Frame(self.container)
        
        tk.Label(frame, text="Enter Username", font=("Helvetica", 14)).pack(pady=10)
        
        self.username_entry = tk.Entry(frame, width=30)
        self.username_entry.insert(0, self.username)
        self.username_entry.pack(pady=10)
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="OK", command=self.save_username).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Cancel", command=self.show_main_menu).pack(side=tk.RIGHT, padx=10)
        
        self.current_frame = frame
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def save_username(self):
        new_username = self.username_entry.get().strip()
        if new_username:
            self.username = new_username
        self.show_main_menu()

    def microsoft_login(self):
        messagebox.showinfo("Info", "Microsoft login not implemented yet")

    def launch_game(self):
        if not self.selected_version:
            messagebox.showerror("Error", "No version selected!")
            return
        
        options = {
            "username": self.username,
            "uuid": str(uuid.uuid4()),
        }
        
        if self.login_data:
            options.update({
                "uuid": self.login_data["id"],
                "token": self.login_data["access_token"],
            })
        
        try:
            minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(
                self.selected_version, self.minecraft_directory, options
            )
            subprocess.run(minecraft_command, cwd=self.minecraft_directory)
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    launcher = MinecraftLauncher(root)
    root.mainloop()