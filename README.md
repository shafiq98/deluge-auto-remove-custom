# deluge-auto-remove-custom
Custom logic to look through a directory, check if hardlinks still exist, and if not, remove those torrents from deluge client.

# How to:
NOTE: Run this inside unraid terminal directly. Running this via Ubuntu VM and windows has inaccurate hard link reporting.
```bash
python main.py
```