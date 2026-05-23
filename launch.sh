#!/bin/bash

source $(pwd)/.venv/bin/activate

export __NV_PRIME_RENDER_OFFLOAD=1
export __GLX_VENDOR_LIBRARY_NAME=nvidia
$(which python3) $(pwd)/minecraft_launcher.py
