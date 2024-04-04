#!/usr/bin/env python3
#MPH First Hunt mouse fix for Linux
#S.D.G.
    
class FirstHuntMousefix(MousefixBase):
    config = "firstHunt"

    def __init__(self, *args, **kwargs):
        """MouseFix for Metroid Prime: Hunters [First Hunt]"""
        super().__init__(*args, **kwargs)

    def get_is_hud(self):
        """Are we in the Varia HUD, not in the ship? Does not work in weapon select"""
        return pyautogui.pixelMatchesColor(*self.rel_to_abs(*self["isHudCoords"]), self["isHudColor"], self["colorTolerance"])
    
    def weaponselect(self, weapon):
        """Select a weapon by index 1-3"""
        self.touchbutton(self["weaponSelectButtons"][weapon-1])

    def jump(self, e):
        """Perform a double-tap jump"""
        if e.event_type == "down":
            for i in range(2):
                self.reset_mouse()
                time.sleep(CONFIG["buttonWait"])

name = "Metroid PH: First Hunt"
mousefix = FirstHuntMousefix
