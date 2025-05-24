# Warp Cloudflare - GUI

A simple PyQt5 graphical interface to manage the Cloudflare Warp connection via `warp-cli` on Linux.

## Features

- Starts and checks the status of the `warp-svc` service.
- Displays the current IP address.
- Connects and disconnects Warp with a single click.
- Shows real-time logs.
- Automatically registers Warp if needed.

## Requirements

- Python 3
- warp-cli and warp-svc installed
- `systemd` and permissions to use `sudo`

## Installation

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## How to use

```bash
sudo python3 warp_gui.py
```

> **Tip:** Run with proper permissions to avoid failures when controlling the Warp service.
