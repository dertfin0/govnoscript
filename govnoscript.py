import pyautogui as gui
import keyboard as kb
import time
from datetime import datetime

# Internal

def _parse_number(string: str) -> float:
    """
    Parses number from string
    :param string: Number or number with uncertainty
    :return:
    """
    from random import uniform
    string = string.replace(',', '.')
    if "~" in string:
        number = string.split("~")
        if len(number) != 2:
            print(f"Can't parse number [{string}]. Returning 0")
            return 0
        else:
            return uniform(
                float(number[0]) - float(number[1]),
                float(number[0]) + float(number[1])
            )
    else:
        try:
            number = float(string)
        except ValueError:
            print(f"Can't parse number [{string}]. Returning 0")
            number = 0
        return number


def _parse_variable(line: str) -> list | None:
    """
    Try to parse variable from line
    :param line: Line of code
    :return: List [key, value] or none, if not parsed
    """
    splitted = line.split()
    if len(splitted) < 3 or splitted[1] != "=":
        return None

    name = splitted[0]
    value = " ".join(splitted[2:])
    return [name, value]


# Commands

def _moveto(line0):
    if len(line0) != 4:
        raise ValueError
    gui.moveTo(int(_parse_number(line0[1])), int(_parse_number(line0[2])), _parse_number(line0[3]))

def _click(line0):
    if len(line0) != 2:
        raise ValueError
    match line0[1].lower():
        case "left":
            gui.leftClick()
        case "right":
            gui.rightClick()
        case "middle":
            gui.middleClick()
        case _:
            print(f"Unknown mouse button [{line0[1]}]")

def _wait(line0):
    if len(line0) != 2:
        raise ValueError
    time.sleep(float(line0[1]))

def _write(line0):
    if len(line0) < 3:
        raise ValueError
    text = " ".join(line0[2:])
    kb.write(text, _parse_number(line0[1]))

def _write_by_keyboard(line0):
    if len(line0) < 3:
        raise ValueError
    text = " ".join(line0[2:]).lower()
    for char in text:
        time.sleep(_parse_number(line0[1]))
        kb.press(char)
        time.sleep(0.05)
        kb.release(char)

def _press(line0):
    if len(line0) != 2:
        raise ValueError
    kb.press(line0[1])

def _release(line0):
    if len(line0) != 2:
        raise ValueError
    kb.release(line0[1])

def _time(execution_start):
    now = datetime.now().timestamp()
    ms = int((now - execution_start) * 1000)
    print(f"{ms} ms")

def _hotkey(line0):
    if len(line0) != 2:
        raise ValueError
    keys = line0[1].split("+")
    for key in keys:
        kb.press(key)
        time.sleep(0.01)
    for key in keys[::-1]:
        kb.release(key)
        time.sleep(0.01)

def _tap(line0):
    if len(line0) != 2:
        raise ValueError
    kb.press(line0[1])
    time.sleep(0.03)
    kb.release(line0[1])

def _parse_line(line, execution_start, script_vars):
    line0 = line.split()

    if line in ["", " ", "\n"]:
        return
    if line0[0].startswith("#"):
        return

    match line0[0].lower():
        case "moveto":
            _moveto(line0)
        case "click":
            _click(line0)
        case "wait":
            _wait(line0)
        case "write":
            _write(line0)
        case "write_by_keyboard":
            _write_by_keyboard(line0)
        case "press":
            _press(line0)
        case "release":
            _release(line0)
        case "hotkey":
            _hotkey(line0)
        case "tap":
            _tap(line0)
        case "time":
            _time(execution_start)
        case _:
            variable = _parse_variable(line)
            if variable is None:
                print(f"Unknown command [{line}]")
            else:
                script_vars[variable[0]] = variable[1]

# Main methods

def run(filename: str, script_vars: dict = None):
    """
    Read .govno file and run it
    :param filename: .govno-file
    :param script_vars: .govno-file variables
    :raise IOError: Got not .govno-file
    """
    if not filename.endswith(".govno"):
        raise IOError(f"File {filename} must end with .govno")

    with open(filename, "r") as file:
        lines = file.read().split("\n")

    interpret(lines, script_vars)


def interpret(lines: list, script_vars: dict = None):
    """
    Run interpretation of govno-lines
    :param lines: Lines of govno-script
    :param script_vars: .govno-file variables
    """

    if script_vars is None:
        script_vars = {}

    execution_start = datetime.now().timestamp()

    for line in lines:
        for var in script_vars.keys():
            line = line.replace(f"%{var}%", script_vars[var])

        try:
            _parse_line(line, execution_start, script_vars)
        except ValueError:
            print(f"Syntax error in line [{lines.index(line) + 1}]")