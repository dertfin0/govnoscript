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
            print(f"Can't parse number [{string}]")
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
            print(f"Can't parse number [{string}]")
            number = 0
        return number

def run(filename: str, script_vars:dict=None):
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

def interpret(lines: list, script_vars:dict=None):
    """
    Run interpretation of govno-lines
    :param lines: Lines of govno-script
    :param script_vars: .govno-file variables
    """
    import pyautogui as gui
    import keyboard as kb
    import time
    from datetime import datetime

    execution_start = datetime.now().timestamp()

    for line in lines:
        if script_vars is not None:
            for var in script_vars.keys():
                line = line.replace(f"%{var}%", script_vars[var])

        line0 = line.split()

        if line in ["", " ", "\n"]:
            continue
        if line0[0].startswith("#"):
            continue

        match line0[0].lower():
            case "moveto":
                if len(line0) != 4:
                    print(f"Syntax error in line [{lines.index(line)+1}]")
                    continue
                gui.moveTo(int(line0[1]), int(line0[2]), _parse_number(line0[3]))
            case "click":
                if len(line0) != 2:
                    print(f"Syntax error in line [{lines.index(line)+1}]")
                    continue
                match line0[1].lower():
                    case "left":
                        gui.leftClick()
                    case "right":
                        gui.rightClick()
                    case "middle":
                        gui.middleClick()
                    case _:
                        print(f"Unknown mouse button [{line0[1]}]")
            case "wait":
                if len(line0) != 2:
                    print(f"Syntax error in line [{lines.index(line)+1}]")
                    continue
                time.sleep(float(line0[1]))
            case "write":
                if len(line0) < 3:
                    print(f"Syntax error in line [{lines.index(line)+1}]")
                    continue
                text = " ".join(line0[2:])
                kb.write(text, _parse_number(line0[1]))
            case "write_by_keyboard":
                if len(line0) < 3:
                    print(f"Syntax error in line [{lines.index(line)+1}]")
                    continue
                text = " ".join(line0[2:]).lower()
                for char in text:
                    time.sleep(_parse_number(char))
                    kb.press(char)
                    time.sleep(0.05)
                    kb.release(char)
            case "press":
                if len(line0) != 2:
                    print(f"Syntax error in line [{lines.index(line)+1}]")
                    continue
                kb.press(line0[1])
            case "release":
                if len(line0) != 2:
                    print(f"Syntax error in line [{lines.index(line) + 1}]")
                    continue
                kb.release(line0[1])
            case "time":
                now = datetime.now().timestamp()
                ms = int((now - execution_start) * 1000)
                print(f"{ms} ms")
            case _:
                print(f"Unknown command [{line}]")
