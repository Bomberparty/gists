import json
import os
import subprocess
import sys
import threading
import uuid
from tkinter import Button, Entry, Label, Tk
from tkinter.ttk import Combobox, Progressbar

import minecraft_launcher_lib

PROFILE_FILE = "profile.json"


class MinecraftLauncher:
    def __init__(self):
        # Initialize main window
        self.window = Tk()
        self.window.title("Minecraft Launcher")

        # Minecraft directory (constant for this instance)
        self.minecraft_directory = (
            minecraft_launcher_lib.utils.get_minecraft_directory()
        )

        # Initialize UI components
        self._create_widgets()
        self._setup_layout()

        # Version variable that will be set during installation
        self.version = None

    def _create_widgets(self):
        """Create all GUI widgets"""
        # Username components
        self.username_label = Label(self.window, text="Username:")
        self.username_input = Entry(self.window)

        # Version selection components
        self.version_label = Label(self.window, text="Version:")
        versions = minecraft_launcher_lib.utils.get_installed_versions(
            self.minecraft_directory
        )
        versions.append({"id": "not found"})
        self.version_list = [v["id"] for v in versions]
        self.version_select = Combobox(self.window, values=self.version_list)
        self.version_select.current(0)

        # Launch button
        self.launch_button = Button(
            self.window, text="Launch", command=self._launch_game
        )
        # Install new minecraft version buntton
        self.download_button = Button(
            self.window, text="Download", command=self._install_new
        )

    def _setup_layout(self):
        """Arrange widgets in the window"""
        self.username_label.grid(row=0, column=0)
        self.username_input.grid(row=0, column=1)
        self.version_label.grid(row=1, column=0)
        self.version_select.grid(row=1, column=1)
        self.launch_button.grid(row=2, column=1)
        self.download_button.grid(row=3, column=1)

    def _install_new(self):
        installer = MinecraftInstaller()
        installer.run()

    def _get_minecraft_options(self):
        if not (os.path.exists(PROFILE_FILE)):
            options = {
                "username": self.username_input.get()
                if not (self.username_input.get() == "")
                else "TEST",
                "uuid": str(uuid.uuid4()),
            }
            with open(PROFILE_FILE, "w") as f:
                json.dump(options, f)
        else:
            options = json.load(open(PROFILE_FILE, "r"))
        options["jvmArguments"] = [
            "-Dminecraft.api.auth.host=https://nope.invalid",
            "-Dminecraft.api.account.host=https://nope.invalid",
            "-Dminecraft.api.session.host=https://nope.invalid",
            "-Dminecraft.api.services.host=https://nope.invalid",
        ]
        return options

    def _launch_game(self):
        """Launch Minecraft with configured settings"""
        self.version = self.version_select.get()
        self.window.withdraw()

        options = self._get_minecraft_options()
        minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(
            self.version,
            self.minecraft_directory,
            options,
        )

        subprocess.run(minecraft_command)
        sys.exit(0)

    def run(self):
        """Start the application"""
        self.window.mainloop()


class MinecraftInstaller:
    def __init__(self):
        # Initialize main window
        self.window = Tk()
        self.window.title("Install a specific version of minecraft")

        # Minecraft directory (constant for this instance)
        self.minecraft_directory = (
            minecraft_launcher_lib.utils.get_minecraft_directory()
        )

        # Initialize UI components
        self._create_widgets()
        self._setup_layout()

        # Version variable that will be set during installation
        self.version = None

    def _create_widgets(self):
        """Create all GUI widgets"""
        # Version selection components
        self.version_label = Label(self.window, text="Version:")
        versions = minecraft_launcher_lib.utils.get_available_versions(
            self.minecraft_directory
        )
        self.version_list = [v["id"] for v in versions]
        self.version_select = Combobox(self.window, values=self.version_list)
        self.version_select.current(0)

        # Launch button
        self.launch_button = Button(
            self.window, text="Install", command=self._start_launch_process
        )

    def _setup_layout(self):
        """Arrange widgets in the window"""
        self.version_label.grid(row=0, column=0)
        self.version_select.grid(row=0, column=1)
        self.launch_button.grid(row=1, column=1)

    def _start_launch_process(self):
        """Handle launch button click"""
        self.launch_button.config(state="disabled")
        self._hide_input_widgets()
        self._show_progress_widgets()

        # Start installation in separate thread
        threading.Thread(target=self._install_minecraft, daemon=True).start()

    def _hide_input_widgets(self):
        """Hide version inputs"""
        for widget in [self.version_select, self.version_label]:
            widget.grid_remove()

    def _show_progress_widgets(self):
        """Show progress bar and status label"""
        self.progress_bar = Progressbar(
            self.window, orient="horizontal", mode="determinate"
        )
        self.progress_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)

        self.status_label = Label(self.window, text="Starting installation...")
        self.status_label.grid(row=1, column=0, columnspan=2)

    def _install_minecraft(self):
        """Install Minecraft version in background thread"""
        # Get selected version from combobox
        self.version = self.version_select.get()

        # Set up installation callbacks
        callbacks = {
            "setStatus": lambda text: self.window.after(0, self._update_status, text),
            "setProgress": lambda value: self.window.after(
                0, self._update_progress, value
            ),
            "setMax": lambda value: self.window.after(0, self._set_max_progress, value),
        }

        # Perform actual installation
        minecraft_launcher_lib.install.install_minecraft_version(
            self.version, self.minecraft_directory, callback=callbacks
        )

        # Close the window after installation completes
        self.window.after(0, self.window.destroy())

    def _update_status(self, text):
        """Update installation status text"""
        self.status_label.config(text=text)

    def _update_progress(self, value):
        """Update progress bar value"""
        self.progress_bar["value"] = value

    def _set_max_progress(self, value):
        """Set maximum value for progress bar"""
        self.progress_bar.config(maximum=value)

    def run(self):
        """Start the application"""
        self.window.mainloop()


if __name__ == "__main__":
    launcher = MinecraftLauncher()
    launcher.run()
