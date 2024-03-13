# MPH-DS-mouse-fixer-linux
A Python-based Linux port of the Metroid Prime: Hunters component of https://github.com/JDoe212/DS-FPS-Mouse-Fixer

To use this script, you must install the pyautogui Python library, the keyboard Python library, and the mouse Python library, all where root can see them. I ran pip as root even though it's not recommended.
To use the HUD detector, which automatically pauses the mouse fix in the ship, you will also need to install whichever screenshot tool pyautogui is configured to use. It will tell you in a traceback if it's not available. Either scrot or gnome-screenshot.
To not use the HUD detector, answer Y to the "Are you going into multiplayer?" prompt when the program starts.
You have to run this script as root on Linux, as the keyboard and mouse libraries require root access on that platform.

The default controls are mainly the same as the original mouse fix, except that right shift is NOT the mousefix pause key; backslash is. I added V and B for yes and no, and X for OK. Looks like he added these too, but forgot to put them in his readme.
Like the original, set N and M as the left and right shoulder buttons respectively in your emulator.
You can change the key bindings in the KEYBINDINGS dictionary, but beware that you cannot specify left or right shift or control. Also beware that for some reason the unmaintained keyboard library detects H as Backspace on my system.
There are some other key binding absolute variables, generally not meant to be altered, lower down in the configuration section of the script. Change the kill key, pause key, and left/right shoulder button use keys there.

Backspace is configured as the kill key, like the original.

This script should theoretically work on Windows, but I didn't test that.

See you next mission! S.D.G.
