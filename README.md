# LG WebOS Camera for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom component that provides a real-time camera feed of your LG WebOS TV screen.

**Note:** This integration requires your LG TV to be **rooted** and have **SSH enabled**.

## Features

-   **Real-time Screen Capture**: View what's playing on your TV directly in Home Assistant.
-   **Configurable Refresh Rate**: Set your preferred update interval (default: 5 seconds).
-   **Secure Connection**: Connects via SSH using `asyncssh`.
-   **Offline Handling**: Gracefully handles TV power state (Offline/Online).

## Prerequisites

1.  **Rooted LG WebOS TV**: Your TV must be rooted (e.g., using [RootMyTV](https://rootmy.tv/)).
2.  **SSH Enabled**: You must be able to connect to your TV via SSH.
3.  **Home Assistant**: This component is designed for Home Assistant.

## Installation

### Option 1: HACS (Recommended)

1.  Open HACS in Home Assistant.
2.  Go to "Integrations" > "Explore & Download Repositories".
3.  Search for "LG WebOS Camera" (if published) or add this repository as a custom repository.
4.  Click "Download".
5.  Restart Home Assistant.

### Option 2: Manual Installation

1.  Download the `webos_camera` folder from the `custom_components` directory in this repository.
2.  Copy it to your Home Assistant `config/custom_components/` directory.
3.  Restart Home Assistant.

## Configuration

1.  Go to **Settings** > **Devices & Services**.
2.  Click **Add Integration**.
3.  Search for **LG WebOS Camera**.
4.  Enter your TV's SSH details:
    -   **Host**: IP address of your TV.
    -   **Username**: Usually `root`.
    -   **Password**: Your SSH password.
    -   **Refresh Interval**: How often to update the image (in seconds).

## Troubleshooting

-   **Connection Failed**: Ensure your TV is on and you can SSH into it from a terminal using the same credentials.
-   **No Image**: Verify that `luna-send` is available on your TV by running `luna-send -n 1 -f luna://com.webos.service.capture/executeOneShot '{"path":"/tmp/test.png", "method":"DISPLAY", "format":"PNG", "width":960, "height":540}'` via SSH.

## License

MIT License
