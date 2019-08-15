# rocketchat-downloader

This tool allows you download the complete history of a single room including all uploaded files. This is e.g. helpful after closing a room to have a local archive.

## Requirements
  * Python 3
    * Requests
  * RocketChat Server with enabled REST-Api


## Usage
```
cp config.py.example config.py
<edit config.py>
python3 downloader.py <room name>
```

The tool automatically tries to identify if the given room is a channel or a privte group.

**WARNING**: If it's a private group, the user defined in the `config.py` must be a member!