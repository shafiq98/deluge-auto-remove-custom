# deluge-auto-remove-custom
Custom logic to look through a directory, check if hardlinks still exist, and if not, remove those torrents from deluge client.

# How to:
NOTE: Run this inside unraid terminal directly. Running this via Ubuntu VM and windows has inaccurate hard link reporting.

# Setup
1. Create new account for Deluge RPC to assume
2. Add new line in vim with format specified in https://deluge-torrent.org/userguide/authentication/
    2.1. SAMPLE_USERNAME:SAMPLE_PASSWORD:5
```bash 
cd /path/to/deluge/app/data
vim auth
```

```bash
python main.py
```