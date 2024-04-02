#!/usr/bin/env python3
#MPH First Hunt mouse fix for Linux, ver 2.0
#S.D.G.

"""
NOTES:
- Boost ball should not be handled by the mousefix, as it works via a double-tap of direction buttons.
"""

from DS_FPS_mousefix_linux import *
    
class FirstHuntMousefix(MousefixBase):
    
    def __init__(self, run=True, USE_AUTO_PAUSE=True):
        """MouseFix for Metroid Prime: Hunters [First Hunt]"""
        super(type(self), self).__init__(USE_AUTO_PAUSE)
        self.SCALE = (1280, 960) #Size of reference window

        #Limits of where to wrap the mouse
        self.MOUSE_DRAG_AREA_X = (0, 1115)
        self.MOUSE_DRAG_AREA_Y = (0, 555)

        self.IS_HUD_COORDS = (45, 625) #Coordinates to check for color match if we are in HUD or elsewhere
        self.VARIA_ORANGE = 219, 162, 56 #Color of varia components in HUD
        self.COLOR_TOLERANCE = 10

        self.KEYBINDS = {'q': 'MAIN_WEAPON',
                    'e': 'MISSILES',
                    'r': 'THIRD_WEAPON',
                    'ctrl': 'MORPH_BALL',
                    'space': 'JUMP'
                    }

        self.TOUCHBUTTONS = { #Each button's position, and how long to press it
            "MAIN_WEAPON" : ((930, 864), BUTTON_WAIT),
            "MISSILES" : ((1090, 744), BUTTON_WAIT),
            "THIRD_WEAPON" : ((1200, 579), BUTTON_WAIT),
            "MORPH_BALL" : ((165, 780), BUTTON_WAIT),
            }

        self.WEAPONSELECT_BUTTONS = ( #Buttons of the three weapons for numerical selection
            self.TOUCHBUTTONS["MAIN_WEAPON"],
            self.TOUCHBUTTONS["MISSILES"],
            self.TOUCHBUTTONS["THIRD_WEAPON"],
            )

    def get_is_hud(self):
        """Are we in the Varia HUD, not in the ship? Does not work in weapon select"""
        return pyautogui.pixelMatchesColor(*self.rel_to_abs(*self.IS_HUD_COORDS), self.VARIA_ORANGE, self.COLOR_TOLERANCE)
    
    def weaponselect(self, weapon):
        """Select a weapon by index 1-3"""
        self.touchbutton(self.WEAPONSELECT_BUTTONS[weapon-1])

    def jump(self, e):
        """Perform a double-tap jump"""
        if e.event_type == "down":
            for i in range(2):
                self.reset_mouse()
                time.sleep(BUTTON_WAIT)

if __name__ == "__main__":
    fhmf=FirstHuntMousefix(USE_AUTO_PAUSE = not "n" in input("Use HUD check auto-pause? [Y]/n: ").lower())
    fhmf.start()
