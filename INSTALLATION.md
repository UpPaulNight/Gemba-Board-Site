# Installation

## Install requirements

Python packages

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Node packages

```bash
npm install
```

## Install fonts

```bash
mkdir -p  ~/.fonts/truetype
cp fonts/* ~/.fonts/truetype/
fc-cache -f -v
```

See whoever is managing this project for any aptos fonts if they are still
required. Those cannot be distributed freely.

## Configure environment variables

Create a `.env` file in the project root directory with the following contents:

- `DOWNLOAD_KEY`: Epicor API download key (`DashboardImages` is intended for this purpose).
- `DOWNLOAD_PASS`: Epicor API download password (`DashboardFileDownloader2` is the intended user to refer to).

The format of the `.env` file should be as follows:

```env
DOWNLOAD_KEY=abc123ihavekey
DOWNLOAD_PASS='456nothingrhymeswithpass'
```

You can check to make sure the environment variables are set correctly by running:

```bash
python3 index.py
```

## Configure the service files

In `services/gemba-browser.service`, edit the line that currently is
`ExecStart=/usr/bin/chromium --kiosk http://127.0.0.1:8000/index.html`. Instead
of *index.html*, put the specific HTML file you want to open on startup, e.g.
*Fabrication.html*.

## Install services

### Make sure the systemd user directory exists

```bash
mkdir -p ~/.config/systemd/user
systemctl --user daemon-reload
```

### Copy service and timer files

```bash
cp services/*.service ~/.config/systemd/user/
cp services/*.timer ~/.config/systemd/user/
systemctl --user daemon-reload
```

### Enable and start services

```bash
systemctl --user enable refresh-image.timer
systemctl --user start refresh-image.timer

systemctl --user enable gemba-browser.service
systemctl --user enable start-gemba-http-server.service
```

## Test services

### Check that the timer is running

```bash
systemctl --user status refresh-image.timer
```

### Test that images can be pulled

```bash
systemctl --user start refresh-image.service
systemctl --user status refresh-image.service
```

If you tested the python file earlier and it worked, then this will not download
new files, but it will be sufficient to test that the service is working.

### Test that the web server starts

```bash
systemctl --user start start-gemba-http-server.service
systemctl --user status start-gemba-http-server.service
```

If that runs correctly, test that the browser service starts successfully

```bash
systemctl --user start gemba-browser.service
```

If a web browser opens to the correct page, the installation is complete.
