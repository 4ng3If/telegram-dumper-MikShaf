import re
import os
from colorama import Fore, Style

RST = Style.RESET_ALL
DIM = Style.DIM

RED = Fore.RED
GRN = Fore.GREEN
YLW = Fore.YELLOW
BLU = Fore.BLUE
MGA = Fore.MAGENTA
CYN = Fore.CYAN

ok = f"{RST}[{CYN}+{RST}]"
info = f"{RST}[{MGA}info{RST}]"
success = f"{RST}[{GRN}✓{RST}]"
warning = f"{RST}[{YLW}-{RST}]"
error = f"{RST}[{RED}!{RST}]"

def color(string, color, wrap=None):
    global RST
    return f"{RST}{color}{string}{RST}" if not wrap else wrap.replace("STR", f"{RST}{color}{string}{RST}")

def generate_box(lines, length=78, title="", titleclr=Fore.YELLOW, pos="center", loc="top"):
    output = []
    undefined = (length == -1)
    length = 40 if undefined else length  
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    
    def title_bar(start, end, title, length, titleclr, pos, undefined):
        title_length = len(title) + 2  
        content_length = length - 2
        wrap_left = color("[", RST) if title else color('─', DIM)
        wrap_right = color("]", RST) if title else color('─', DIM)

        if pos == "center":
            pad = (content_length - title_length) // 2
            return f"{start}{'─' * pad}{wrap_left}{color(title, titleclr)}{wrap_right}{color(f"{'─' * pad}{end if not undefined else '»'}", DIM)}"

        elif pos == "right":
            pad = (content_length - title_length) - 1
            return f"{start}{'─' * pad}{wrap_left}{color(title, titleclr)}{wrap_right}{color(f"{end if not undefined else '─»'}", DIM)}"

        else:  
            return f"{start}{wrap_left}{color(title, titleclr)}{wrap_right}{color(f"{'─' * (content_length - title_length)}{end if not undefined else '»'}", DIM)}"

    
    if loc == "top":
        output.append(color(title_bar("┌", "┐", title, length, titleclr, pos, undefined), DIM))
    else:
        output.append(color(f"┌{'─' * (length - 2)}{'┐' if not undefined else '»'}", DIM))

    
    for line in lines:
        line_length = len(ansi_escape.sub('', line))  
        padding = length - line_length - 3  
        output.append(f"{color('│', DIM)} {line}{' ' * padding}{color('│' if not undefined else '', DIM)}")

    
    if loc == "bottom":
        output.append(color(title_bar("└", "┘", title, length, titleclr, pos, undefined), DIM))
    else:
        output.append(color(f"└{'─' * (length - 2)}{'┘' if not undefined else '»'}", DIM))

    return "\n".join(output)

def prompt(title, titleclr=Fore.CYAN, pos='left', before=""):
    lgth = (18 - (len(title) // 2))  
    contentLen = (38 - len(f"[{title}]"))
    match (pos):
        case 'center':
            return f"{color(f'{before}┌{'─' * lgth}', DIM)}[{color(title, titleclr)}]{color(f"{'─' * lgth}»", DIM)}\n{color('└──', DIM)}{Fore.YELLOW}» "

        case 'rigth':
            return f"{color(f'{before}┌{'─' * (contentLen - 1)}', DIM)}[{color(title, titleclr)}]{color('─»', DIM)}\n{color('└──', DIM)}{Fore.YELLOW}» "

        case 'left' | _:
            return f"{color(f'{before}┌─', DIM)}[{color(title, titleclr)}]{color(f"{'─' * (contentLen - 1)}»", DIM)}\n{color('└──', DIM)}{Fore.YELLOW}» "

def banner():
    os.system("cls" if os.name == "nt" else "clear")

    rainbow = [RED, YLW, GRN, CYN, YLW]      
    logo = [
        " __  __   _   _      ____    _                __ ",
        "|  \\/  | (_) | | __ / ___|  | |__     __ _   / _|",
        "| |\\/| | | | | |/ / \\___ \\  | '_ \\   / _` | | |_ ",
        "| |  | | | | |   <   ___) | | | | | | (_| | |  _|",
        "|_|  |_| |_| |_|\\_\\ |____/  |_| |_|  \\__,_| |_|  ",
    ]
    shades = [CYN, GRN, YLW, RED, MGA]
    for ln, col in zip(logo, shades):
        print(color(ln, col))

    
    print(color("MikShaf • Telegram OSINT", YLW))
    print(color("github.com/0xtiho/telegram-dumper-MikShaf", CYN), color("v1.0", YLW))
