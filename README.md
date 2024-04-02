# Nintendo DS FPS Mouse Fixer for Linux
A Python-based Linux port of https://github.com/JDoe212/DS-FPS-Mouse-Fixer
Currently written mousefixes:
- Metroid Prime Hunters
- Metroid Prime Hunters First Hunt (Demo)

Support for other games is possible, but isn't planned at current. Request a game, or write a mousefix and create a pull request yourself if you want.

## Requirements:
These scripts are tested and working with Python 3.12 on Fedora 39 x86 64.
Install the following Python libraries. If on Linux, they must be where root can see them. To achieve that, I ran Pip (Python's package installer) as root, even though it's not recommended.
- PyAutoGUI: https://pypi.org/project/PyAutoGUI/
- Pillow: https://pypi.org/project/pillow/
- Keyboard: https://pypi.org/project/keyboard/
- Mouse: https://pypi.org/project/mouse/

Additionally, to use the HUD detection features on Linux, you will also need to install whichever screenshot tool PyAutoGUI is configured to use. Python will tell you in a traceback if it's not available. Either scrot or gnome-screenshot.

## Usage
### Configuration:
- Set N and M as the left and right shoulder buttons respectively in your emulator.
- Either set your D-Pad buttons as WASD in your emulator, or change the DPAD_KEYS variable in the DS_FPS_mousefix_linux.py module to match your preferred configuration.
- All global variables in the DS_FPS_mousefix_linux.py module are inherited by all mousefixes. Configure them in the module.
- You can change the key bindings in the KEYBINDINGS dictionary of the mousefixes, but beware that you cannot specify between left and right Shift, or left and right Control. Also beware that for some reason the keyboard library detects H as Backspace on my system.
- Changing MOUSEBINDS is not recommended, as some functions of the mousefix assume they will not change.

### Running the script:
1. The DS_FPS_mousefix_linux.py script is a module, not meant to be run by itself. The *mousefix.py import it, and they are meant to be run by themselves.
2. You have to run the scripts as root on Linux, as the keyboard and mouse libraries require root access on that platform.
3. On startup, the mousefixes will ask you a question that has to do with using the auto-pause functionality, which looks for pixels on screen of a certain color.
4. After answering the question, the program(s) will tell you to click opposite corners of the touch area, to get where it is on screen and how big it is. Do so with the tip of the mouse cursor as close to the exact corners as you can. Do not click anything else first! Note, it doesn't matter which two corners of the touch area that you click, as long as they are diagonal opposites (i.e. after clicking one corner, the second corner clicked is the one farthest away from the first).

#### Controls:
- The default controls are mainly the same as the original mousefix, except that Right Shift is NOT the mousefix pause key; Backslash is.
- Backspace is configured as the kill key, like the original.

- Metroid Prime Hunters:
    - I added V and B for yes and no, and X for OK.
    - Boost ball can be done in two ways: By pressing Tab, optionally with direction key combos to boost in a direction other than forward (relies on DPAD_KEYS being set correctly), or; With the HUD detection features (singleplayer only), by pressing, holding, and releasing RMB (this momentarily sacrifices mouse-based steering).
- Metroid Prime Hunters First Hunt:
    - Jump can only be performed by a double tap on the touch screen, so this is mapped by default to Space. There is some latency here which I can't do anything about AFAIK. Switching weapons also inadvertently will trigger a jump, because the weapon buttons are within the jump double-tap area in the ROM programming.

## Notes:
- Because of a limitation in PyAutoGUI, the mousefixes will temporarily sacrifice wrapping while holding the mouse down. As soon as the mouse button is released irl, wrapping is restored, and the mouse is reset to center if it was dragged out of the bounds of the steer area. Try to avoid needing to steer when holding a charged shot or continuous fire from the full-auto weapons.
- These mousefixes should theoretically work on Windows, but I didn't test that. If you'd like to test it yourself, let me know how it worked for you. Thanks!

See you next mission! S.D.G.
