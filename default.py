import os
import shutil
import subprocess
import xbmcgui
import xbmcaddon

ADDON = xbmcaddon.Addon()

# Settings (can be changed in Add-on Settings)
url = ADDON.getSetting('game_url') or "https://slither.io"
browser_setting = ADDON.getSetting('browser_path') or ""
browser_args_setting = ADDON.getSetting('browser_args') or "--kiosk --start-fullscreen --app={url}"

# Helper to check executability
def is_executable(path):
    return path and os.path.isfile(path) and os.access(path, os.X_OK)

# Build list of candidate browser executables to try
candidates = []
# 1) User provided path from settings
if browser_setting:
    candidates.append(browser_setting)
# 2) Try common binaries on PATH
for name in ('brave-browser', 'brave', 'brave-nightly'):
    try:
        p = shutil.which(name)
    except Exception:
        p = None
    if p:
        candidates.append(p)
# 3) Common installation locations
common_paths = [
    '/usr/bin/brave-browser',
    '/usr/bin/brave',
    '/opt/brave.com/brave/brave',
    '/snap/bin/brave'
]
for p in common_paths:
    candidates.append(p)

# De-duplicate while preserving order
seen = set()
candidates_clean = []
for p in candidates:
    if p and p not in seen:
        seen.add(p)
        candidates_clean.append(p)

browser = None
for p in candidates_clean:
    if is_executable(p):
        browser = p
        break

if not browser:
    tried = '\n'.join(candidates_clean) if candidates_clean else '(no candidates)'
    message = (
        "Brave browser not found on your system.\n\n"
        "Tried these locations:\n" + tried + "\n\n"
        "Please install Brave (https://brave.com) or set the correct browser path in the add-on settings.\n"
        "Open the add-on's settings via Add-ons → My add-ons → Programs → Slither.io (Brave) → Configure."
    )
    xbmcgui.Dialog().ok("Slither.io", message)
else:
    # Prepare arguments; allow the user to use {url} placeholder in the settings
    args_str = browser_args_setting.replace('{url}', url)
    args_list = args_str.split()
    # If the args contain a standalone --app= (without url) ensure it includes the URL
    for i, a in enumerate(args_list):
        if a.startswith('--app=') and len(a) == len('--app='):
            args_list[i] = '--app=' + url
    # If no --app or --app= found, append the default --app={url}
    if not any(arg.startswith('--app') for arg in args_list):
        args_list.append('--app=' + url)

    try:
        subprocess.Popen([browser] + args_list)
        # Notify user
        xbmcgui.Dialog().notification('Slither.io', 'Launching Brave...')
    except Exception as e:
        xbmcgui.Dialog().ok('Slither.io', 'Failed to launch browser: %s' % str(e))
