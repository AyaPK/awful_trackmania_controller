import board
import digitalio
import time
import usb_hid
import struct
from adafruit_debouncer import Debouncer

# Custom Gamepad class using raw HID
class Gamepad:
    def __init__(self, devices):
        # Find the gamepad device
        self._gamepad_device = None
        if devices:
            for device in devices:
                if device.usage_page == 0x01 and device.usage == 0x05:  # Generic Desktop, Gamepad
                    self._gamepad_device = device
                    break
        
        # Initialize gamepad state
        self._report = bytearray(3)  # 3-byte report (X, Y, Buttons)
        # Set Y to center (128) initially
        self._report[1] = 128
        # Buttons start at 0 (not pressed)
        self._report[2] = 0
        
    def move_joysticks(self, x=None, y=None):
        """Move joysticks. x and y should be in range -127 to 127"""
        if x is not None:
            # Convert from -127..127 to 0..255 range
            x_byte = max(0, min(255, x + 128))
            self._report[0] = x_byte
        if y is not None:
            # Convert from -127..127 to 0..255 range  
            y_byte = max(0, min(255, y + 128))
            self._report[1] = y_byte
            
        # Send the report
        if self._gamepad_device:
            try:
                self._gamepad_device.send_report(self._report)
            except Exception as e:
                print(f"HID send error: {e}")
                
    def press_button(self, button_num, pressed):
        """Press or release a button (1-8). pressed = True/False"""
        if 1 <= button_num <= 8:
            bit_mask = 1 << (button_num - 1)
            if pressed:
                self._report[2] |= bit_mask  # Set bit
            else:
                self._report[2] &= ~bit_mask  # Clear bit
            
            # Send the report
            if self._gamepad_device:
                try:
                    self._gamepad_device.send_report(self._report)
                except Exception as e:
                    print(f"HID send error: {e}")

# Rotary encoder pins
clk_right = digitalio.DigitalInOut(board.GP22)  # A RIGHT
clk_right.direction = digitalio.Direction.INPUT
clk_right.pull = digitalio.Pull.UP

dt_right = digitalio.DigitalInOut(board.GP26_A0)  # B RIGHT
dt_right.direction = digitalio.Direction.INPUT
dt_right.pull = digitalio.Pull.UP

# Optional: Encoder push button on SW
btn_pin_right = digitalio.DigitalInOut(board.GP15) # Press RIGHT
btn_pin_right.direction = digitalio.Direction.INPUT
btn_pin_right.pull = digitalio.Pull.UP
switch_right = Debouncer(btn_pin_right)

# Rotary encoder pins
clk_left = digitalio.DigitalInOut(board.GP17)  # A LEFT
clk_left.direction = digitalio.Direction.INPUT
clk_left.pull = digitalio.Pull.UP

dt_left = digitalio.DigitalInOut(board.GP16)  # B LEFT
dt_left.direction = digitalio.Direction.INPUT
dt_left.pull = digitalio.Pull.UP

# Optional: Encoder push button on SW
btn_pin_left = digitalio.DigitalInOut(board.GP14) # Press LEFT
btn_pin_left.direction = digitalio.Direction.INPUT
btn_pin_left.pull = digitalio.Pull.UP
switch_left = Debouncer(btn_pin_left)

# Button pins
btn = digitalio.DigitalInOut(board.GP18)
btn.direction = digitalio.Direction.INPUT
btn.pull = digitalio.Pull.UP
btn_switch = Debouncer(btn)

# Initialize gamepad
gamepad = Gamepad(usb_hid.devices)

# Track last state of CLK and DT for both encoders
last_clk_right = clk_right.value
last_dt_right = dt_right.value
stick_x = 0  # Analog stick X position (-127 to 127, 0 is center)
last_stick_x = None  # Track last sent position to avoid unnecessary updates

last_clk_left = clk_left.value
last_dt_left = dt_left.value
counter_left = 0

while True:
    switch_right.update()
    switch_left.update()
    btn_switch.update()

    # Handle push buttons
    if switch_right.fell:
        print("Right Encoder Button Pressed - B Button!")
        gamepad.press_button(2, True)  # Press B button (button 2)
    if switch_right.rose:
        print("Right Encoder Button Released - B Button!")
        gamepad.press_button(2, False)  # Release B button

    if switch_left.fell:
        print("Left Encoder Button Pressed - A Button!")
        gamepad.press_button(1, True)  # Press A button (button 1)
    if switch_left.rose:
        print("Left Encoder Button Released - A Button!")
        gamepad.press_button(1, False)  # Release A button

    if btn_switch.fell:
        print("Reset Button Pressed - X Button!")
        stick_x = 0
        counter_left = 0
        gamepad.press_button(3, True)  # Press X button (button 3)
        # Only send stick reset if position actually changed
        if last_stick_x != stick_x:
            gamepad.move_joysticks(x=stick_x, y=0)
            last_stick_x = stick_x
    
    if btn_switch.rose:
        print("Reset Button Released - X Button!")
        gamepad.press_button(3, False)  # Release X button

    # Rotary encoder logic with proper debouncing
    current_clk_right = clk_right.value
    current_dt_right = dt_right.value

    current_clk_left = clk_left.value
    current_dt_left = dt_left.value

    # Right encoder - only trigger on CLK change for debouncing
    if current_clk_right != last_clk_right:
        if current_clk_right == False:
            if current_dt_right != current_clk_right:
                # Clockwise - move stick right
                stick_x = min(127, stick_x + 15)  # Increment by 5, max 127
                print("Rotated Right Clockwise →", stick_x)
            else:
                # Counter-clockwise - move stick left
                stick_x = max(-127, stick_x - 15)  # Decrement by 5, min -127
                print("Rotated Right Counter-Clockwise ←", stick_x)
            
            # Only send HID report if position actually changed
            if last_stick_x != stick_x:
                gamepad.move_joysticks(x=stick_x, y=0)
                last_stick_x = stick_x

    # Left encoder - only trigger on CLK change for debouncing
    if current_clk_left != last_clk_left:
        if current_clk_left == False:
            if current_dt_left != current_clk_left:
                counter_left += 1
                print("Rotated Left Clockwise →", counter_left)
            else:
                counter_left -= 1
                print("Rotated Left Counter-Clockwise ←", counter_left)

    # Update last states for both encoders
    last_clk_right = current_clk_right
    last_dt_right = current_dt_right
    last_clk_left = current_clk_left
    last_dt_left = current_dt_left
    time.sleep(0.001)  # Increased debounce to reduce USB traffic
