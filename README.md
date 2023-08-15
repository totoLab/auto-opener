# ao: auto-opener
The name is based on calling someone's attention with the expression "ao", largely used in Rome. Here instead we "call" files and URLs.

### Installation
Running `install.sh` will create the necessary directory structure `~/.config/auto-opener/` and copy the template for the config file with the name `config.config`.   

### Configuration
`~/.config/auto-opener/config.config` will contain garbage configuration after copy. Inserting valid names and filepaths/URLs will be needed.

### Running
The script can be executed as `python auto-opener.py` or directly from shell `./auto-opener.py`. <br>
Creating a soft-link using this command `ln -s path/to/auto-opener.py ao` or moving the script inside a PATH folder, lets it execute from anywhere with this syntax: `ao example1`.