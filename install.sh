CONFIG_DIR=$HOME/.config/auto-opener

if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR" || { echo "Error while creating config directory"; exit 1; }
    echo "Created config directory"
else
    echo "Config directory already exists"
fi

if [ ! -f "$CONFIG_DIR/config.config" ]; then
    cp template.config "$CONFIG_DIR/config.config" || { echo "Error while creating config file"; exit 1; }
    echo "Created config file"
else
    echo "Config file already exists"
fi
