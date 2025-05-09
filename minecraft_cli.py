import minecraft_launcher_lib
import subprocess
import sys
import uuid

minecraft_version = "1.16.5"

# This gets you the default mencraft directory this library usually creates
# To find a necessary version you have installed, you need to list all directories in the 'version' directory inside of this one 
minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()

# Install specific minecraft version
# minecraft_launcher_lib.install.install_minecraft_version(minecraft_version, minecraft_directory)

# Get available versions to install
# versions = minecraft_launcher_lib.utils.get_available_versions(self.minecraft_directory)

# If you want to login into your microsoft account, use this code to get the login code, and use the commented options
# login_url, state, code_verifier = minecraft_launcher_lib.microsoft_account.get_secure_login_data(CLIENT_ID, REDIRECT_URL)
# print(f"Please open {login_url} in your browser and copy the url you are redirected into the prompt below.")
# code_url = input()

# # Get the code from the url
# try:
#     auth_code = minecraft_launcher_lib.microsoft_account.parse_auth_code_url(code_url, state)
# except AssertionError:
#     print("States do not match!")
#     sys.exit(1)
# except KeyError:
#     print("Url not valid")
#     sys.exit(1)

# # Get the login data
# login_data = minecraft_launcher_lib.microsoft_account.complete_login(CLIENT_ID, None, REDIRECT_URL, auth_code, code_verifier)

# # Get Minecraft command
# options = {
#     "username": login_data["name"],
#     "uuid": login_data["id"],
#     "token": login_data["access_token"]
# }

options = {
    "username": "brpxd",
    "uuid": "a8f34036-4cb8-481d-b67c-86d75d2384b3",
}

minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(minecraft_version, minecraft_directory, options)

subprocess.run(minecraft_command, cwd=minecraft_directory)