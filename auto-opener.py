#!/usr/bin/python3

import sys
import os
import re
import subprocess
import argparse

# --- Configuration ---

TOP_LEVEL_COMMANDS = ["conf", "list", "help"]
SUB_COMMANDS = ["list", "add", "remove"]

# --- Error Handling ---

def error(message):
    print(message)
    if notifications: send_notification(message)

def fatal_error(message):
    error(message)
    sys.exit(1)

def send_notification(message, error=False):
    title = f"{args[0]}{"ERROR" if error else ""}"
    match sys.platform:
        case "linux" | "linux2":
            subprocess.Popen(['notify-send', message, f"--app-name={title}"])
        case "darwin":
            CMD = '''
                on run argv
                    display notification (item 2 of argv) with title (item 1 of argv)
                end run
            '''
            subprocess.call([
                'osascript', '-e', CMD, title, message])
        case "win32":
            pass # not implemented
        case _:
            fatal_error("Couldn't detect OS platform")

# --- Utility Functions ---

def exist_path(filepath):
    return os.path.exists(filepath)

def valid_link(link):
    link = link.strip()
    return link.startswith("http") or exist_path(link)

def generate_key_list(config):
    return [key for key in config]

def make_hyperlink(url, text=None):
    if not url.startswith("http"):
        text = url
        url = f"file://{url}"
    return f'\033]8;;{url}\033\\{text}\033]8;;\033\\'

def cardinal_print(to_print, as_hyperlink=False):
    for i, element in enumerate(to_print, 0):
        if as_hyperlink: element = make_hyperlink(element, element)
        print(f"{i}) {element}")

def print_key_list(config):
    key_list = generate_key_list(config)
    print("Titles in config file:")
    cardinal_print(key_list)
    return key_list

def display_help():
    top_level_commands_str = ", ".join(TOP_LEVEL_COMMANDS)
    sub_commands_str = ", ".join(SUB_COMMANDS)
    help_text = (
        "Help:\n"
        f"  ao <title>                         As default usage opens links related to title.\n"
        f"  ao <top-level command>.            Top-level commands: [{top_level_commands_str}]\n"
        f"  ao <title> OPTIONAL <sub-command>. Sub commands: [{sub_commands_str}]\n"
        f"Please note: add and remove commands are user-interactive."
    )
    print(help_text)

# --- Command line args and configuration ---

def get_config_path():
    path = ""
    match sys.platform:
        case "linux" | "linux2" | "darwin":
            path = os.path.expanduser("~/.config/auto-opener/config.config")
        case "win32":
            separator = "\\"
            path = separator.join(os.path.realpath(__file__).split(separator)[:-1] + ["template.config"])
        case _:
            fatal_error("Couldn't detect OS platform")

    return path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Auto Opener: Manage and open URLs or file paths from a configuration file.",
        usage="%(prog)s [title] [sub-command]"
    )

    parser.add_argument(
        'title_or_command', 
        nargs='?', 
        help="A title from the config or a top-level command. Top-level commands: conf, list, help."
    )
    
    # Optional sub-command
    parser.add_argument(
        'sub_command', 
        nargs='?', 
        choices=SUB_COMMANDS, 
        help="Sub-command for a title: list, add, or remove."
    )
    
    return parser.parse_args()

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

def rewrite_config(filepath, config):
    with open(filepath, "w") as f:
        for key, links in config.items():
            f.write(f"[{key}]\n")
            f.writelines(f"{link}\n" for link in links)
            f.write("\n")

# --- Link Opening ---

def open_default(path):
    match sys.platform:
        case "linux" | "linux2":
            os.system(f"xdg-open '{path}'")
        case "darwin":
            os.system(f"open '{path}'")
        case "win32":
            try:
                os.startfile(f"'{path}'")
            except: # TODO: FIX logs the same thing for every error in windows 
                print("Path in config file are not formatted for Windows, ignoring.")
        case _:
            fatal_error("Couldn't detect OS platform")

def open_links(links):
    for link in links:
        if valid_link(link):
            open_default(link)
            print(f"Opened successfully {link}")
        else:
            error(f"`{link}` is not a valid URL or filepath.")

# --- User Input Handling ---

def controlled_input(upper_limit, message):
    valid_input = ""
    while not valid_input.isnumeric() or 0 > int(valid_input) or int(valid_input) >= upper_limit:
        valid_input = input(f"Insert a valid number between 0 and {upper_limit - 1}: ")

    return int(valid_input)

# --- Top-Level Command Handling ---

def handle_top_level_command(config, command):
    if command == "conf":
        open_default(path)
        print("Opened config.")
    elif command == "help":
        display_help()
    elif command == "list":
        print_key_list(config)

# --- Sub-Command Handling ---

def handle_sub_command(config, command, title_to_open):
    modified_config = False
    if command == "list":
        links = config.get(title_to_open, [])
        print(f"Links of title {title_to_open}:")
        if len(links) == 0:
            error(f"no links associated with this title.")
        else:
            cardinal_print(links, as_hyperlink=True)
    elif command == "add":
        new_link = input(f"Insert filepath/url to {command} to {title_to_open}{' (new)' if title_to_open not in config else ''}: ")
        config.setdefault(title_to_open, []).append(new_link)
        modified_config = True
        print(f"{new_link} added successfully to {title_to_open}")
    elif command == "remove":
        if title_to_open in config:
            links_list = config.get(title_to_open, [])
            if len(links_list) == 0:
                remove_title = input(f"{title_to_open} has no links associated with it. Want to remove the title from configuration? [y/N] ")
                if remove_title.strip().lower() == "y":
                    config.pop(title_to_open)
                    modified_config = True
                    print(f"Removed {title_to_open} from configuration.")
            else:
                print("Current titles' list:")
                cardinal_print(links_list, as_hyperlink=True)
                index = controlled_input(len(links_list), "Insert index of the element to remove: ")
                element = links_list.pop(index)
                modified_config = True
                print(f"{element} removed successfully from {title_to_open}")
        else:
            fatal_error(f"Can't remove: {title_to_open} is not a title in config.")
        
    if modified_config:
        rewrite_config(path, config)

# --- Main Functionality ---

def open_title(config, to_open):
    if to_open in config:
        links = config[to_open]
        open_links(links)
    else:
        error(f"ERR: {to_open} not in config file.")

if __name__ == "__main__":
    args = parse_args()
    notifications = False

    path = get_config_path()    
    config = parse_config(path)
    if args.title_or_command in TOP_LEVEL_COMMANDS:
        handle_top_level_command(config, args.title_or_command)
    elif args.title_or_command:
        title = args.title_or_command
        if args.sub_command:
            handle_sub_command(config, args.sub_command, title)
        else:  
            open_title(config, title)
    else:
        fatal_error("Invalid command or missing title. Use --help for usage.")