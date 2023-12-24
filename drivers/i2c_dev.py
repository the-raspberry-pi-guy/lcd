from smbus import SMBus
from RPi.GPIO import RPI_REVISION
from time import sleep
from re import findall, match
from subprocess import check_output
from os.path import exists

# old and new versions of the RPi have swapped the two i2c buses
# they can be identified by RPI_REVISION (or check sysfs)
BUS_NUMBER = 0 if RPI_REVISION == 1 else 1

# other commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00
SESSION_STATE_BACKLIGHT = ''

En = 0b00000100  # Enable bit
Rw = 0b00000010  # Read/Write bit
Rs = 0b00000001  # Register select bit

class I2CDevice:
    def __init__(self, addr=None, addr_default=None, bus=BUS_NUMBER):
        if not addr:
            # try autodetect address, else use default if provided
            try:
                self.addr = int('0x{}'.format(
                    findall("[0-9a-z]{2}(?!:)", check_output(['/usr/sbin/i2cdetect', '-y', str(BUS_NUMBER)]).decode())[0]), base=16) \
                    if exists('/usr/sbin/i2cdetect') else addr_default
            except:
                self.addr = addr_default
        else:
            self.addr = addr
        self.bus = SMBus(bus)

    # write a single command
    def write_cmd(self, cmd):
        self.bus.write_byte(self.addr, cmd)
        sleep(0.0001)

    # write a command and argument
    def write_cmd_arg(self, cmd, data):
        self.bus.write_byte_data(self.addr, cmd, data)
        sleep(0.0001)

    # write a block of data
    def write_block_data(self, cmd, data):
        self.bus.write_block_data(self.addr, cmd, data)
        sleep(0.0001)

    # read a single byte
    def read(self):
        return self.bus.read_byte(self.addr)

    # read
    def read_data(self, cmd):
        return self.bus.read_byte_data(self.addr, cmd)

    # read a block of data
    def read_block_data(self, cmd):
        return self.bus.read_block_data(self.addr, cmd)


class Lcd:
    def __init__(self, addr=None):
        self.addr = addr
        self.lcd = I2CDevice(addr=self.addr, addr_default=0x27)
        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x02)
        self.lcd_write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
        self.lcd_write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
        self.lcd_write(LCD_CLEARDISPLAY)
        self.lcd_write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
        sleep(0.2)

    # clocks EN to latch command
    def lcd_strobe(self, data):
        if SESSION_STATE_BACKLIGHT == 0:
            LCD = LCD_NOBACKLIGHT
        else:
            LCD = LCD_BACKLIGHT
        self.lcd.write_cmd(data | En | LCD)
        sleep(.0005)
        self.lcd.write_cmd(((data & ~En) | LCD))
        sleep(.0001)

    def lcd_write_four_bits(self, data):
        if SESSION_STATE_BACKLIGHT == 0:
            LCD = LCD_NOBACKLIGHT
        else:
            LCD = LCD_BACKLIGHT
        self.lcd.write_cmd(data | LCD)
        self.lcd_strobe(data)

    # write a command to lcd
    def lcd_write(self, cmd, mode=0):
        self.lcd_write_four_bits(mode | (cmd & 0xF0))
        self.lcd_write_four_bits(mode | ((cmd << 4) & 0xF0))

    # put string function
    def lcd_display_string(self, string, line):
        if line == 1:
            self.lcd_write(0x80)
        if line == 2:
            self.lcd_write(0xC0)
        if line == 3:
            self.lcd_write(0x94)
        if line == 4:
            self.lcd_write(0xD4)
        for char in string:
            self.lcd_write(ord(char), Rs)

    # put extended string function. Extended string may contain placeholder like {0xFF} for
    # displaying the particular symbol from the symbol table
    def lcd_display_extended_string(self, string, line):
        if line == 1:
            self.lcd_write(0x80)
        if line == 2:
            self.lcd_write(0xC0)
        if line == 3:
            self.lcd_write(0x94)
        if line == 4:
            self.lcd_write(0xD4)
        # Process the string
        while string:
            # Trying to find pattern {0xFF} representing a symbol
            result = match(r'\{0[xX][0-9a-fA-F]{2}\}', string)
            if result:
                self.lcd_write(int(result.group(0)[1:-1], 16), Rs)
                string = string[6:]
            else:
                self.lcd_write(ord(string[0]), Rs)
                string = string[1:]

    # clear lcd and set to home
    def lcd_clear(self):
        self.lcd_write(LCD_CLEARDISPLAY)
        self.lcd_write(LCD_RETURNHOME)

    # backlight control (on/off)
    # options: lcd_backlight(1) = ON, lcd_backlight(0) = OFF
    def lcd_backlight(self, state):
        global SESSION_STATE_BACKLIGHT
        if state == 1:
            self.lcd.write_cmd(LCD_BACKLIGHT)
        elif state == 0:
            self.lcd.write_cmd(LCD_NOBACKLIGHT)

        if state == 1 or state == 0:  # Save backlight settings
            SESSION_STATE_BACKLIGHT = state
class CustomCharacters:
    def __init__(self, lcd):
        self.lcd = lcd
        # Data for custom character #1. Code {0x00}.
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
        self.chars_list = [self.char_1_data, self.char_2_data, self.char_3_data,
                           self.char_4_data, self.char_5_data, self.char_6_data,
                           self.char_7_data, self.char_8_data]

        # commands to load character adress to RAM srarting from desired base adresses:
        char_load_cmds = [0x40, 0x48, 0x50, 0x58, 0x60, 0x68, 0x70, 0x78]
        for char_num in range(8):
            # command to start loading data into CG RAM:
            self.lcd.lcd_write(char_load_cmds[char_num])
            for line_num in range(8):
                line = self.chars_list[char_num][line_num]
                binary_str_cmd = "0b000{0}".format(line)
                self.lcd.lcd_write(int(binary_str_cmd, 2), Rs)