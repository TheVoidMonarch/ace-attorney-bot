# ⚖️ Ace Attorney WhatsApp Bot

A WhatsApp bot that turns message chains into Ace Attorney courtroom scenes.  
Refactored from [TheVoidMonarch/ace-attorney-bot](https://github.com/TheVoidMonarch/ace-attorney-bot), powered by [objection_engine](https://github.com/LuisMayo/objection_engine).

---

## How It Works

Users send messages to the bot's WhatsApp number in this format:

```
Phoenix: I OBJECT!
Edgeworth: On what grounds?
Phoenix: I have absolutely no idea
```

After 5 seconds of silence, the bot renders and sends back an Ace Attorney video scene. Images can be sent with a caption in the same format and will appear as evidence.

---

## Requirements

Before following any platform guide, you'll need:

- A **Twilio account** — [sign up free at twilio.com](https://twilio.com)
- A **ngrok account** — [sign up free at ngrok.com](https://ngrok.com)
- Your **Twilio Account SID**, **Auth Token**, and **WhatsApp sandbox number** (found in the Twilio Console)
- A place to **host rendered videos publicly** (S3, GCS, or a second ngrok tunnel for dev — see [Video Hosting](#video-hosting))

---

## Table of Contents

- [Windows Setup](#windows-setup)
- [Linux Setup](#linux-setup)
- [macOS Setup](#macos-setup)
- [Android Setup](#android-setup)
- [Twilio & Webhook Configuration](#twilio--webhook-configuration)
- [Video Hosting](#video-hosting)
- [Running the Bot](#running-the-bot)
- [Troubleshooting](#troubleshooting)

---

## Windows Setup

### 1. Install Python

Download and install Python 3.10+ from [python.org](https://www.python.org/downloads/windows/).  
During installation, check **"Add Python to PATH"**.

Verify in a Command Prompt:
```cmd
python --version
```

### 2. Install ffmpeg

1. Download a Windows build from [ffmpeg.org/download.html](https://ffmpeg.org/download.html) (get a "full" build from gyan.dev or BtbN)
2. Extract it somewhere permanent, e.g. `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your **System PATH**:
   - Search for **"Edit the system environment variables"**
   - Click **Environment Variables** → find **Path** under System Variables → **Edit** → **New** → paste `C:\ffmpeg\bin`
4. Open a new Command Prompt and verify:
```cmd
ffmpeg -version
```

### 3. Install Git

Download from [git-scm.com](https://git-scm.com/download/win) and install with default options.

### 4. Clone the Repository

```cmd
git clone --recursive https://github.com/TheVoidMonarch/ace-attorney-bot
cd ace-attorney-bot
```

### 5. Install Python Dependencies

```cmd
pip install -r requirements.txt
```

If you hit OpenCV errors:
```cmd
pip install opencv-python
```

### 6. Install ngrok

Download from [ngrok.com/download](https://ngrok.com/download), extract, and either add it to your PATH or run it from its folder.

Add your auth token:
```cmd
ngrok config add-authtoken <your-ngrok-token>
```

### 7. Fill In Your Credentials

Create `credentials.txt` in the project folder:
```
YOUR_TWILIO_ACCOUNT_SID
YOUR_TWILIO_AUTH_TOKEN
whatsapp:+14155238886
```

---

## Linux Setup

### 1. Install System Dependencies

**Ubuntu / Debian:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip git ffmpeg libopencv-dev python3-opencv -y
```

**Fedora / RHEL:**
```bash
sudo dnf install python3 python3-pip git ffmpeg opencv -y
```

**Arch Linux:**
```bash
sudo pacman -Syu python python-pip git ffmpeg opencv
```

> **Note:** If you encounter a codec error like `"couldn't find codec for id 27"`, the system ffmpeg may lack required encoders. See [Troubleshooting](#troubleshooting).

### 2. Clone the Repository

```bash
git clone --recursive https://github.com/TheVoidMonarch/ace-attorney-bot
cd ace-attorney-bot
```

### 3. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 4. Install ngrok

```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
ngrok config add-authtoken <your-ngrok-token>
```

Or download the binary directly from [ngrok.com/download](https://ngrok.com/download).

### 5. Fill In Your Credentials

```bash
nano credentials.txt
```

```
YOUR_TWILIO_ACCOUNT_SID
YOUR_TWILIO_AUTH_TOKEN
whatsapp:+14155238886
```

---

## macOS Setup

### 1. Install Homebrew

If you don't already have it:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Dependencies

```bash
brew update
brew install python git ffmpeg opencv
```

### 3. Clone the Repository

```bash
git clone --recursive https://github.com/TheVoidMonarch/ace-attorney-bot
cd ace-attorney-bot
```

### 4. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

If you see an OpenCV error on Apple Silicon (M1/M2/M3):
```bash
pip3 install opencv-python-headless
```

### 5. Install ngrok

```bash
brew install ngrok/ngrok/ngrok
ngrok config add-authtoken <your-ngrok-token>
```

### 6. Fill In Your Credentials

```bash
nano credentials.txt
```

```
YOUR_TWILIO_ACCOUNT_SID
YOUR_TWILIO_AUTH_TOKEN
whatsapp:+14155238886
```

---

## Android Setup

Android uses **Termux** — a terminal emulator that gives you a real Linux environment without rooting your device.

### 1. Install Termux

> ⚠️ Do **not** install Termux from the Google Play Store — that version is outdated and unsupported.

Install from [F-Droid](https://f-droid.org/packages/com.termux/).

### 2. Update Termux and Install Dependencies

Open Termux and run:
```bash
pkg update && pkg upgrade -y
pkg install python git ffmpeg opencv -y
```

Allow Termux to access device storage (optional but useful):
```bash
termux-setup-storage
```

### 3. Install ngrok

```bash
pkg install wget unzip
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.zip
unzip ngrok-v3-stable-linux-arm64.zip
mv ngrok $PREFIX/bin/
ngrok config add-authtoken <your-ngrok-token>
```

### 4. Clone the Repository

```bash
git clone --recursive https://github.com/TheVoidMonarch/ace-attorney-bot
cd ace-attorney-bot
```

### 5. Install Python Dependencies

```bash
pip install -r requirements.txt
```

If OpenCV fails to install:
```bash
pip install opencv-python-headless
```

### 6. Fill In Your Credentials

```bash
nano credentials.txt
```

```
YOUR_TWILIO_ACCOUNT_SID
YOUR_TWILIO_AUTH_TOKEN
whatsapp:+14155238886
```

### 7. Prevent Android from Killing the Bot

Android aggressively kills background processes. Do both of these:

- Go to **Settings → Apps → Termux → Battery** and set it to **Unrestricted**
- Inside Termux, acquire a wake lock:
```bash
termux-wake-lock
```

### 8. Running Two Sessions at Once

Termux supports multiple sessions — swipe inward from the left edge of the screen to open the session drawer and tap **"New Session"**.

You'll need two sessions: one for the bot, one for ngrok (see [Running the Bot](#running-the-bot)).

> **Note:** On the free ngrok tier, your public URL changes every time you restart it. You'll need to update the Twilio webhook URL each time. A paid ngrok plan with a fixed domain avoids this.

---

## Twilio & Webhook Configuration

### 1. Set Up the WhatsApp Sandbox

1. Log into the [Twilio Console](https://console.twilio.com)
2. Go to **Messaging → Try it out → Send a WhatsApp message**
3. You'll see a sandbox number (e.g. `whatsapp:+14155238886`) and a join word
4. Every user who wants to use the bot must send a WhatsApp message to that number saying `join <your-sandbox-word>` once to activate the sandbox for their number

### 2. Start ngrok

```bash
ngrok http 5000
```

You'll see output like:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:5000
```

Copy the `https://` URL.

### 3. Set the Webhook in Twilio

1. In the Twilio Console, go to your **WhatsApp Sandbox Settings**
2. Set **"When a message comes in"** to:
```
https://abc123.ngrok.io/webhook
```
3. Set the method to **HTTP POST**
4. Click **Save**

---

## Video Hosting

Twilio requires a **publicly accessible URL** to send media — it cannot accept a direct file upload. You must implement `_get_public_video_url()` in `msg_queue.py`.

### Option A — Local Development (second ngrok tunnel)

Uncomment the file server block at the bottom of `msg_queue.py`, then run a second ngrok tunnel in another terminal/session:

```bash
ngrok http 8080
```

Return this from `_get_public_video_url`:
```python
return f'https://<your-8080-ngrok-id>.ngrok.io/{filename}'
```

### Option B — AWS S3

```python
import boto3
s3 = boto3.client('s3')
s3.upload_file(filename, 'your-bucket-name', filename, ExtraArgs={'ACL': 'public-read'})
return f'https://your-bucket-name.s3.amazonaws.com/{filename}'
```

Install the SDK: `pip install boto3`

### Option C — Google Cloud Storage

```python
from google.cloud import storage
client = storage.Client()
bucket = client.bucket('your-bucket-name')
blob = bucket.blob(filename)
blob.upload_from_filename(filename)
blob.make_public()
return blob.public_url
```

Install the SDK: `pip install google-cloud-storage`

---

## Running the Bot

Once everything is set up, you need two processes running at the same time.

**Terminal / Session 1 — the bot:**
```bash
cd ace-attorney-bot
python main.py        # or python3 on Linux/macOS
```

**Terminal / Session 2 — ngrok:**
```bash
ngrok http 5000
```

The bot is ready when you see:
```
* Running on http://0.0.0.0:5000
```

---

## Troubleshooting

**`"couldn't find codec for id 27"` on Linux**  
Your system ffmpeg is missing required encoders. You'll need to compile ffmpeg from source:
- [FFMPEG compilation guide (Ubuntu)](https://trac.ffmpeg.org/wiki/CompilationGuide/Ubuntu)
- [OpenCV compilation guide](https://docs.opencv.org/master/d2/de6/tutorial_py_setup_in_ubuntu.html)

**OpenCV won't install on Apple Silicon (M1/M2/M3)**  
Use the headless build instead:
```bash
pip install opencv-python-headless
```

**OpenCV won't install in Termux**  
Same fix:
```bash
pip install opencv-python-headless
```

**Twilio webhook returns errors**  
Make sure ngrok is running and the URL in Twilio matches exactly, including `/webhook` at the end. Check the ngrok inspector at `http://127.0.0.1:4040` to see incoming requests and any error responses.

**Video renders but never arrives in WhatsApp**  
`_get_public_video_url()` in `msg_queue.py` has not been implemented yet. See [Video Hosting](#video-hosting).

**ngrok URL keeps changing**  
Upgrade to a paid ngrok plan with a fixed static domain, or re-paste the new URL into Twilio each session.

**Android kills Termux in the background**  
Make sure battery optimisation is disabled for Termux and run `termux-wake-lock` inside Termux before starting.

---

## Contributing

Pull requests are welcome. For major changes please open an issue first.  
Original Telegram bot by [LuisMayo](https://github.com/LuisMayo) — give them a ⭐ too!

