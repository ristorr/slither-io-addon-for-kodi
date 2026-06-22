import subprocess
import xbmcgui
import os

url = "https://slither.io"

browser = "/usr/bin/brave-browser"

if not os.path.exists(browser):
    xbmcgui.Dialog().ok(
        "Slither.io",
        "Brave browser not found at /usr/bin/brave-browser"
    )
else:
    subprocess.Popen([
        browser,
        "--kiosk",
        "--start-fullscreen",
        "--app=" + url
    ])
