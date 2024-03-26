# MPH-DS-mouse-fixer-linux
A Python-based Linux port of the Metroid Prime: Hunters component of https://github.com/JDoe212/DS-FPS-Mouse-Fixer
This program was tested with Python 3.12 on Fedora 39 x64.

## Requirements:
This script is tested and working with Python 3.12 on Fedora 39 x86 64.
Install the following Python libraries. If on Linux, they must be where root can see them. To achieve that, I ran Pip (Python's package installer) as root, even though it's not recommended.
- PyAutoGUI: https://pypi.org/project/PyAutoGUI/
- Pillow: https://pypi.org/project/pillow/
- Keyboard: https://pypi.org/project/keyboard/
- Mouse: https://pypi.org/project/mouse/

Additionally, to use the HUD detection features on Linux, you will also need to install whichever screenshot tool PyAutoGUI is configured to use. Python will tell you in a traceback if it's not available. Either scrot or gnome-screenshot. To avoid this installation and not use the HUD detector, always answer Y to the "Are you going into multiplayer?" prompt when the program starts.

## Usage
### Emulator configuration:
- Set N and M as the left and right shoulder buttons respectively in your emulator.
- Either set your D-Pad buttons as WASD in your emulator, or change the DPAD_KEYS variable in this script to match your preferred configuration.

### Script configuration:
- You can change the key bindings in the KEYBINDINGS dictionary, but beware that you cannot specify between left and right Shift, or left and right Control. Also beware that for some reason the keyboard library detects H as Backspace on my system.
- There are some other key binding absolute variables, generally not meant to be altered, lower down in the configuration section of the script. Change the kill key, pause key, and left/right shoulder button use keys there.

### Running the script:
- You have to run this script as root on Linux, as the keyboard and mouse libraries require root access on that platform.
- On startup, the program will ask, "Are you going into multiplayer?" If you answer "n" or nothing, the program will enable the HUD detection features: It will occasionally check for a Varia orange pixel from Samus's HUD on screen in specific locations. These checks are used: to automatically pause the game while in-ship or in cutscenes (note that while auto-paused, you cannot also manually pause); to momentarily sacrifice steering for a shoulder button (right click) boost ball.
- After answering the question, the program will tell you to click opposite corners of the touch area, to get where it is on screen and how big it is. Do so with the tip of the mouse cursor as close to the exact corners as you can. Do not click anything else first! Note, it doesn't matter which two corners of the touch area that you click, as long as they are diagonal opposites (i.e. after clicking one corner, the second corner clicked is the one farthest away from the first).
#### Controls:
- The default controls are mainly the same as the original mouse fix, except that Right Shift is NOT the mousefix pause key; Backslash is.
- Backspace is configured as the kill key, like the original.
- I added V and B for yes and no, and X for OK. 
- Boost ball can be done in two ways: By pressing Tab, optionally with direction key combos to boost in a direction other than forward (relies on DPAD_KEYS being set correctly), or; With the HUD detection features (singleplayer only), by pressing, holding, and releasing RMB (this momentarily sacrifices mouse-based steering).


## Notes:
- Because of a limitation in PyAutoGUI, the mouse fix will temporarily sacrifice wrapping while holding a charged shot. As soon as the mouse button is released irl, wrapping is restored, and the mouse is reset to center if it was dragged out of the bounds of the steer area. Try to avoid needing to steer when loading a charged shot.
- This script should theoretically work on Windows, but I didn't test that. If you'd like to test it yourself, let me know how it worked for you. Thanks!

See you next mission! S.D.G.
