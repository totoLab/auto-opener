#!/usr/bin/python3

import sys, os, re, subprocess


TOP_LEVEL_COMMANDS = ["conf", "help"]
SUB_COMMANDS = ["add", "remove"]

def todo():
    fatal_error("Not yet implemented.")

def fatal_error(message):
    print(message)
    sys.exit()

def exist_path(filepath):
    return os.path.exists(filepath)

def valid_link(link):
    link = link.strip()
    return "http" in link[:6] or exist_path(link)

def parse_args(args):
    n = len(args)

    if n == 1:
        fatal_error("Not enough arguments.")
    elif n == 2:
        command = args[1]
        if command in TOP_LEVEL_COMMANDS:
            return None, command, 0, None
        else:
            return None, "open", 1, command
    elif n == 3:
        title = args[1]
        sub_command = args[2]
        if sub_command in SUB_COMMANDS:
            return None, sub_command, 1, title

    fatal_error("Not a valid command.")

def parse_config(filepath):
    config = {}
    title_pattern = r'^\[(.+)\]$'

    with open(filepath, 'r') as file:
        current_title = None
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            match = re.match(title_pattern, line)
            if match:
                current_title = match.group(1)
                if current_title in config:
                    fatal_error(f"Bad config at {filepath}, duplicate title found: '{current_title}' on line {line_number}")
                config[current_title] = []
            elif line:
                if current_title is None:
                    fatal_error(f"Bad config at {filepath}, line without title at line {line_number}: '{line}'")
                config[current_title].append(line)

    return config

def open_links(links):
    for link in links:
        if valid_link(link):
            os.system(f"xdg-open {link}")
            print(f"Opened successfully {link}")
        else:
            print(f"`{link}` is not a valid url or filepath.")


def main(filepath, to_open):
    config = parse_config(filepath)
    if to_open in config:
        links = config[to_open]
        open_links(links)
    else:
        print(f"ERR: {to_open} not in config file.")

fallback_path = os.path.expanduser("~/.config/auto-opener/config.config")

if __name__ == "__main__":
    args = sys.argv

    path, command, command_type, title_to_open = parse_args(args)
    if path is None:
        path = fallback_path

    if command_type == 0:
        if command == "conf":
            subprocess.call(('xdg-open', path))
            print("Opened config.")
        elif command == "help":
            top_level_commands_str = ", ".join(TOP_LEVEL_COMMANDS)
            sub_commands_str = ", ".join(SUB_COMMANDS)
            help_text = (
                "Help:\n"
                "  ao <title>                         As default usage\n"
                f"  ao <top-level command>.            Top-level commands: [{top_level_commands_str}]\n"
                f"  ao <title> OPTIONAL <sub-command>. Sub commands: [{sub_commands_str}]"
            )
            print(help_text)
    elif command_type == 1:
        if command == "open":
            main(path, title_to_open)
        elif command == "add":
            todo()
        elif command == "remove":
            todo()
    else:
        print("Unhandled case. Go fix.")
