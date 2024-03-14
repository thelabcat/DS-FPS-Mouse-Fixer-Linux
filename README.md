# MPH-DS-mouse-fixer-linux
A Python-based Linux port of the Metroid Prime: Hunters component of https://github.com/JDoe212/DS-FPS-Mouse-Fixer

# Requirements:
Install the following Python libraries where root can see them. To achieve this, I ran pip as root, even though it's not recommended.
- PyAutoGUI: https://pypi.org/project/PyAutoGUI/
- keyboard: https://pypi.org/project/keyboard/
- mouse: https://pypi.org/project/mouse/

Additionally, to use the HUD detector, you will also need to install whichever screenshot tool PyAutoGUI is configured to use. Python will tell you in a traceback if it's not available. Either scrot or gnome-screenshot. To avoid this installation and not use the HUD detector, always answer Y to the "Are you going into multiplayer?" prompt when the program starts.

# Usage
- You have to run this script as root on Linux, as the keyboard and mouse libraries require root access on that platform.
- Set N and M as the left and right shoulder buttons respectively in your emulator.
- Either set your D-Pad buttons as WASD in your emulator, or change the DPAD_KEYS variable in this script to match your preferred configuration.
- The default controls are mainly the same as the original mouse fix, except that right shift is NOT the mousefix pause key; backslash is.
- Backspace is configured as the kill key, like the original.
- I added V and B for yes and no, and X for OK. 
- Boost ball can be done by pressing Tab, with direction key combos to boost in a direction other than forward. Relies on DPAD_KEYS being set correctly.
- You can change the key bindings in the KEYBINDINGS dictionary, but beware that you cannot specify left or right shift or control. Also beware that for some reason the keyboard library detects H as Backspace on my system.
- There are some other key binding absolute variables, generally not meant to be altered, lower down in the configuration section of the script. Change the kill key, pause key, and left/right shoulder button use keys there.
- If you answer "n" or nothing to the "Are you going into multiplayer?" startup question, the program will occasionally check for a Varia orange pixel from the corner of Samus's HUD on screen, and pauses the mouse fix if it does not see it. It should thus auto-pause the fix in-ship and during cutscenes, allowing normal mouse use during these. Note that while auto-paused, you cannot also manually pause.

This script should theoretically work on Windows, but I didn't test that. If you'd like to test it yourself, let me know how it worked for you. Thanks!

See you next mission! S.D.G.
