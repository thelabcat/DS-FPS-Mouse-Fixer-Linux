# Nintendo DS FPS Mouse Fixer for Linux
A Python-based cross-platform port of https://github.com/JDoe212/DS-FPS-Mouse-Fixer with some quality of life improvements.
Currently written mousefixes:
- Metroid Prime Hunters
- Metroid Prime Hunters First Hunt (Demo)

Support for other games is possible, but isn't planned at current. Request a game, or write a mousefix and create a pull request yourself if you want.

## Requirements:
This program is tested and working with Python 3.12 on Fedora 39 x86 64.
To run from source, install Python 3.x, and the following Python libraries. If on Linux, they must be where root can see them. To achieve that, I ran Pip (Python's package installer) as root, even though it's not recommended.
- PyAutoGUI: https://pypi.org/project/PyAutoGUI/
- Pillow: https://pypi.org/project/pillow/
- Keyboard: https://pypi.org/project/keyboard/
- Mouse: https://pypi.org/project/mouse/

Additionally, to use the HUD detection features on Linux, you will also need to install whichever screenshot tool PyAutoGUI is configured to use. Python will tell you in a traceback if it's not available. Either scrot or gnome-screenshot.

## Usage
### TOML Configuration:
- Set your emulator keybinds to match emuKeys in the configuration TOML, or vice versa. By default, D-Pad is WASD, and the left and right shoulder buttons are N and M respectively.
- Change the mousefix keybinds under mousefix.default for use by all mousefixes, or under mousefix.*MousefixName* for mousefix-specific settings, but beware that you cannot specify between left and right Shift, or left and right Control. Also beware that for some reason the keyboard library detects H as Backspace on my system.
- Changing other values is not recommended.

### Running the script:
1. To run from source, the DS_FPS_mousefix.py script is the main program. The scripts in the mousefixes folder are not meant to be run by themselves as they rely on it.
2. You have to run the program as root on Linux, as the keyboard and mouse libraries require root access on that platform.
3. When the GUI opens, select a game from the option menu.
4. If you do not want to use HUD detection for auto-pause and other features, uncheck the "Use HUD detection" box.
5. Click "Start" when you are ready, with the emulator open. After a delay, the window will turn red, and the mousefix is active.
6. After the mousefix window turns red, *do not make any other clicks.* Click two diagonal opposite corners of the stylus play area in your emulator, with the tip of your mouse cursor as close to the actual corner as you can, to calibrate where the play area is and how big it is. If you move the play area by resizing or repositioning the emulator window, you will need to restart the mousefix to recalibrate.

#### Controls:
- The default controls are mainly the same as the original mousefix, except that Right Shift is NOT the mousefix pause key; Backslash is.
- Backspace is configured as the kill key, like the original.
- If the mousefix window is closed while the mousefix is paused, the mousefix should exit with the window. Killing the mousefix via Backspace should conversely destory the window.

- Metroid Prime Hunters:
    - I added V and B for yes and no, and X for OK.
    - Boost ball can be done in two ways: By pressing Tab, optionally with direction key combos to boost in a direction other than forward (relies on TOML emuKeys.dPad being set correctly), or; With the HUD detection features (singleplayer only), by pressing, holding, and releasing RMB (this momentarily sacrifices mouse-based steering).
- Metroid Prime Hunters First Hunt:
    - Jump can only be performed by a double tap on the touch screen, so this is mapped by default to Space. There is some latency here which I can't do anything about AFAIK. Switching weapons also inadvertently will trigger a jump, because the weapon buttons are within the jump double-tap area in the ROM programming.

## Notes:
- Because of a limitation in PyAutoGUI, the mousefixes will temporarily sacrifice wrapping while holding the mouse down. As soon as the mouse button is released irl, wrapping is restored, and the mouse is reset to center if it was dragged out of the bounds of the steer area. Try to avoid needing to steer when holding a charged shot or continuous fire from the full-auto weapons.
- This program should theoretically work on Windows, but I didn't test that. If you'd like to test it yourself, let me know how it worked for you. Thanks!

See you next mission! S.D.G.
