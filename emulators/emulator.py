import tkinter as tk
from tkinter import font
from typing import List, Optional, Union
from re import match
from time import sleep

custom_chars = {}  # Storage CustomCharacters


class LcdEmulator:
    def __init__(self,
                 TITTLE_WINDOWS: Union[str, int] = "LCD 16x2 Emulator",
                 LCD_BACKGROUND: str = "green",
                 LCD_FOREGROUND: str = "black",
                 SESSION_STATE_BACKLIGHT: int = 1,
                 FONT: str = "Courier",
                 FONT_SIZE: int = 75,
                 COLUMNS: int = 16,
                 ROWS: int = 2,
                 CHAR_WIDTH: int = 75):

        """
        Parameters
        ----------
        TITTLE_WINDOWS: Union[str, int], default "LCD 16x2 Emulator"
            As expected, rename the TKinter windows
        LCD_BACKGROUND: str, default "green", HEX allowed (e.g #55A8DB),
            List: https://www.tcl-lang.org/man/tcl8.4/TkCmd/colors.htm
            Control background color.
        LCD_FOREGROUND: str, default "black", HEX allowed (e.g #55A8DB),
            List: https://www.tcl-lang.org/man/tcl8.4/TkCmd/colors.htm
            Control foreground color (generally the text unless you do SESSION_STATE_BACKLIGHT = 0 (OFF)).
        SESSION_STATE_BACKLIGHT: int, default 1, 1: BACKLIGHT ON | 0: BACKLIGHT OFF
            Control the backlight, 1 for ON and 0 for OFF.
        FONT: str, default "Courier", List: https://stackoverflow.com/a/64301819
            Change font.
        FONT_SIZE: int, default 75,
            The font size also adapt to the size of the windows so as not to exceed.
        COLUMNS: int, default 16,
            Unlike the 16x2 LCD screen, here we can have several columns
        ROWS: int, default 2,
            Unlike the 16x2 LCD screen, here we can have several rows
        CHAR_WIDTH: int, default 75,
            Resize the TKinter windows

        Examples
        --------
        >>> import emulators

        >>> display = emulators.LcdEmulator()
        >>> cc = emulators.CustomCharactersEmulator(display)

        """

        self.root = tk.Tk()
        self.root.title(TITTLE_WINDOWS)

        try:
            self.root.winfo_rgb(LCD_BACKGROUND)
            self.LCD_BACKGROUND_DEFAULT = LCD_BACKGROUND
            self.LCD_BACKGROUND = LCD_BACKGROUND
        except tk.TclError:
            self.LCD_BACKGROUND_DEFAULT = "green"
            self.LCD_BACKGROUND = "green"
            print(f"'{LCD_BACKGROUND}' is not a valid LCD_BACKGROUND. List of colors: https://www.tcl-lang.org/man/tcl8.4/TkCmd/colors.htm")

        try:
            self.root.winfo_rgb(LCD_FOREGROUND)
            self.LCD_FOREGROUND_DEFAULT = LCD_FOREGROUND
            self.LCD_FOREGROUND = LCD_FOREGROUND
        except tk.TclError:
            self.LCD_BACKGROUND_DEFAULT = "black"
            self.LCD_BACKGROUND = "black"
            print(f"'{LCD_FOREGROUND}' is not a valid LCD_FOREGROUND. List of colors: https://www.tcl-lang.org/man/tcl8.4/TkCmd/colors.htm")

        if SESSION_STATE_BACKLIGHT not in [0, 1]:
            print(
                f"Error : '{SESSION_STATE_BACKLIGHT}' is not a valid value for SESSION_STATE_BACKLIGHT. Use of 1 by default (ON), use 0 for backlight OFF.")
            self.SESSION_STATE_BACKLIGHT = 1
        else:
            self.SESSION_STATE_BACKLIGHT = SESSION_STATE_BACKLIGHT

        if FONT in font.families():
            self.FONT = FONT
        else:
            self.FONT = "Courier"
            print(f"'{FONT}' is not a valid FONT, List of fonts: {font.families()} | https://stackoverflow.com/a/64301819")

        if FONT_SIZE > 0:
            self.FONT_SIZE = FONT_SIZE
        else:
            self.FONT_SIZE = 75
            print(f"FONT_SIZE '{FONT_SIZE}' must be higher than 1.")

        if COLUMNS < 1:
            print(f"'{COLUMNS}' is not a valid number of COLUMNS, COLUMNS must be higher than 1.")
            self.COLUMNS = 16
        else:
            self.COLUMNS = COLUMNS

        if ROWS < 1:
            print(f"'{ROWS} is not a valid number of ROWS, ROWS must be higher than 1.")
            self.ROWS = 2
        else:
            self.ROWS = ROWS

        if CHAR_WIDTH < 1:
            print(f"'{CHAR_WIDTH} is not a valid number of CHAR_WIDTH, CHAR_WIDTH must be higher than 1.")
            self.CHAR_WIDTH = 75
        else:
            self.CHAR_WIDTH = CHAR_WIDTH

        self.CHAR_HEIGHT = self.CHAR_WIDTH * 1.6
        self.rectangles = []

        self.rects = []
        self.texts = []

        self.canvas = tk.Canvas(self.root, width=self.COLUMNS * self.CHAR_WIDTH, height=self.ROWS * self.CHAR_HEIGHT,
                                bg=self.LCD_BACKGROUND)
        self.canvas.pack()

        font_obj = font.Font(family=self.FONT, size=self.FONT_SIZE)
        all_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=<>?/~`[]{}|\\;:'\",. "
        max_char_width = 0
        for char in all_characters:
            char_width = font_obj.measure(char)
            if char_width > max_char_width:
                max_char_width = char_width
        if self.CHAR_WIDTH <= max_char_width * 0.95:
            self.FONT_SIZE = int(self.CHAR_WIDTH / max_char_width * self.FONT_SIZE * 0.95)

        self.chars = []
        for row in range(self.ROWS):
            for col in range(self.COLUMNS):
                rect = self.canvas.create_rectangle(
                    col * self.CHAR_WIDTH,
                    row * self.CHAR_HEIGHT,
                    (col + 1) * self.CHAR_WIDTH,
                    (row + 1) * self.CHAR_HEIGHT,
                    outline=self.LCD_FOREGROUND,
                    width=max(1, int(self.CHAR_WIDTH / 15))
                )
                text = self.canvas.create_text(
                    col * self.CHAR_WIDTH + self.CHAR_WIDTH // 2,
                    row * self.CHAR_HEIGHT + self.CHAR_HEIGHT // 2,
                    text="",
                    font=(self.FONT, self.FONT_SIZE),
                    fill=self.LCD_FOREGROUND
                )
                self.rects.append(rect)
                self.texts.append(text)
                self.chars.append(text)

        self.custom_characters = CustomCharactersEmulator(self)

    # put string function
    def lcd_display_string(self, text, line=0):
        line = line - 1
        start_index = line * self.COLUMNS
        for i, char in enumerate(text):
            if start_index + i < len(self.chars):
                self.canvas.itemconfig(self.chars[start_index + i], text=char)

        self.lcd_update()

    # put extended string function. Extended string may contain placeholder like {0xFF} for
    # displaying the particular symbol from the symbol table
    def lcd_display_extended_string(self, text, line=0):
        line = line - 1
        i = 0
        x_offset = 0
        while i < len(text):
            match_result = match(r'\{0[xX][0-9a-fA-F]{2}}', text[i:])
            if match_result:
                char_code = match_result.group(0)
                custom_char_bitmap = self.custom_characters.get_custom_char(char_code)
                self.custom_characters.draw_custom_char(custom_char_bitmap,
                                                        x_offset * self.CHAR_WIDTH,
                                                        line * self.CHAR_HEIGHT, self.LCD_FOREGROUND)
                x_offset += 1
                i += 6
            else:
                self.canvas.itemconfig(self.chars[line * self.COLUMNS + x_offset], text=text[i])
                x_offset += 1
                i += 1
        self.lcd_update()

    # clear lcd
    def lcd_clear(self):
        self.root.update_idletasks()
        self.root.update()
        for i in range(2):
            self.lcd_display_string("                ", i)
        for rect_id in self.rectangles:
            self.canvas.delete(rect_id)
        self.rectangles.clear()

    def lcd_update(self):
        self.root.update_idletasks()
        self.root.update()

    # backlight control (on/off)
    # options: lcd_backlight(1) = ON, lcd_backlight(0) = OFF
    def lcd_backlight(self, state: int):
        if state not in [0, 1]:
            print(
                f"Error : '{state}' is not a valid value for lcd_backlight(state). Use of 1 by default (ON), use 0 for backlight OFF.")
            state = 1

        if state == 1:
            self.LCD_BACKGROUND = self.LCD_BACKGROUND_DEFAULT
            self.LCD_FOREGROUND = self.LCD_FOREGROUND_DEFAULT
        elif state == 0:
            self.LCD_BACKGROUND = self.LCD_FOREGROUND_DEFAULT
            self.LCD_FOREGROUND = self.LCD_BACKGROUND_DEFAULT

        self.canvas.configure(bg=self.LCD_BACKGROUND)

        for rect in self.rects:
            self.canvas.itemconfig(rect, outline=self.LCD_FOREGROUND)
        for text in self.texts:
            self.canvas.itemconfig(text, fill=self.LCD_FOREGROUND)

        self.SESSION_STATE_BACKLIGHT = state


class CustomCharactersEmulator:
    def __init__(self, lcd):
        self.lcd = lcd
        self.CHAR_WIDTH = self.lcd.CHAR_WIDTH
        # Data for custom character #1. Code {0x00}
        self.char_1_data = ["11111",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111"]
        # Data for custom character #2. Code {0x01}
        self.char_2_data = ["11111",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111"]
        # Data for custom character #3. Code {0x02}
        self.char_3_data = ["11111",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111"]
        # Data for custom character #4. Code {0x03}
        self.char_4_data = ["11111",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111"]
        # Data for custom character #5. Code {0x04}
        self.char_5_data = ["11111",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111"]
        # Data for custom character #6. Code {0x05}
        self.char_6_data = ["11111",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111"]
        # Data for custom character #7. Code {0x06}
        self.char_7_data = ["11111",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111"]
        # Data for custom character #8. Code {0x07}
        self.char_8_data = ["11111",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "10001",
                            "11111"]

    # load custom character data to CG RAM for later use in extended string. Data for
    # characters is hold in file custom_characters.txt in the same folder as i2c_dev.py
    # file. These custom characters can be used in printing of extended string with a
    # placeholder with desired character codes: 1st - {0x00}, 2nd - {0x01}, 3rd - {0x02},
    # 4th - {0x03}, 5th - {0x04}, 6th - {0x05}, 7th - {0x06} and 8th - {0x07}.
    def load_custom_characters_data(self):
        char_data_list = [
            (f"{{0x00}}", self.char_1_data),
            (f"{{0x01}}", self.char_2_data),
            (f"{{0x02}}", self.char_3_data),
            (f"{{0x03}}", self.char_4_data),
            (f"{{0x04}}", self.char_5_data),
            (f"{{0x05}}", self.char_6_data),
            (f"{{0x06}}", self.char_7_data),
            (f"{{0x07}}", self.char_8_data)
        ]

        for char_name, bitmap in char_data_list:
            if len(bitmap) != 8 or any(len(row) != 5 for row in bitmap):
                continue
            custom_chars[char_name] = bitmap

    def get_custom_char(self, char_name):
        return custom_chars.get(char_name, ["00000"] * 8)

    # Draw CustomCharacters
    def draw_custom_char(self, bitmap, x, y, color):
        pixel_size = self.CHAR_WIDTH / 5
        for row, line in enumerate(bitmap):
            for col, bit in enumerate(line):
                if bit == '1':
                    rect_id = self.lcd.canvas.create_rectangle(
                        x + (col * pixel_size),
                        y + (row * pixel_size),
                        x + ((col + 1) * pixel_size),
                        y + ((row + 1) * pixel_size),
                        fill=color,
                        outline=color
                    )
                    self.lcd.rectangles.append(rect_id)
