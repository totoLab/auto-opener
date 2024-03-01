#!/usr/bin/python3

import sys
import os
import re
import subprocess

# --- Configuration ---

TOP_LEVEL_COMMANDS = ["conf", "list", "help"]
SUB_COMMANDS = ["list", "add", "remove"]
fallback_path = os.path.expanduser("~/.config/auto-opener/config.config")

# --- Error Handling ---

def fatal_error(message):
    print(message)
    sys.exit(1)

# --- Utility Functions ---

def exist_path(filepath):
    return os.path.exists(filepath)

def valid_link(link):
    link = link.strip()
    return link.startswith("http") or exist_path(link)

def generate_key_list(config):
    return [key for key in config]

def cardinal_print(to_print):
    for i, element in enumerate(to_print, 0): print(f"{i}) {element}")

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
            os.system(f"xdg-open {path}")
        case "darwin":
            os.system(f"open {path}")
        case "win32":
            try:
                os.startfile(path)
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
            print(f"`{link}` is not a valid URL or filepath.")

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
            print(f"no links associated with this title.")
        else:
            cardinal_print(links)
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
                cardinal_print(links_list)
                index = controlled_input(len(links_list), "Insert index of the element to remove: ")
                element = links_list.pop(index)
                modified_config = True
                print(f"{element} removed successfully from {title_to_open}")
        else:
            fatal_error(f"Can't remove: {title_to_open} is not a title in config.")
        
    if modified_config:
        rewrite_config(path, config)

# --- Main Functionality ---

def main(filepath, to_open):
    config = parse_config(filepath)
    if to_open in config:
        links = config[to_open]
        open_links(links)
    else:
        print(f"ERR: {to_open} not in config file.")

if __name__ == "__main__":
    args = sys.argv

    path, command, command_type, title_to_open = parse_args(args)
    if path is None:
        path = fallback_path

    config = parse_config(path)

    if command_type == 0:
        handle_top_level_command(config, command)
    elif command_type == 1:
        if command == "open":
            main(path, title_to_open)
        elif command in SUB_COMMANDS:
            handle_sub_command(config, command, title_to_open)
    else:
        print("Unhandled case. Go fix.")
