#!/usr/bin/python3

import sys, os, re

def fatal_error(message):
    print(message)
    sys.exit()

def exist_path(filepath):
    return os.path.exists(filepath)

def valid_link(link):
    link = link.strip()
    return "http" in link[:6] or exist_path(link)

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

    config_to_open = "default"
    if len(args) > 1:
        config_to_open = args[1]

    path = fallback_path
    if len(args) > 2:
        path = args[2]

    main(path, config_to_open)