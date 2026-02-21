#!/usr/bin/env python
"""
Ace Attorney WhatsApp Bot — main.py

Receives incoming WhatsApp messages via a Twilio webhook and dispatches them
to a per-user Queue that eventually renders and returns an Ace Attorney video.

Setup:
  1. pip install -r requirements.txt
  2. Fill in credentials.txt (see README)
  3. Expose this server publicly (e.g. ngrok http 5000) and set the URL as
     your Twilio WhatsApp sandbox webhook:
       https://<your-ngrok>.ngrok.io/webhook
  4. python main.py

Message format for users:
  Send lines one at a time in the format:
      Name: message text
  Images/stickers can be sent with an optional caption in the same format.
  After 5 seconds of silence the video is generated automatically.
"""

import sys
sys.path.insert(0, './objection_engine')

import logging
from flask import Flask, request
from twilio.rest import Client
from msg_queue import Queue

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Load Twilio credentials from credentials.txt
# Line 1: Account SID
# Line 2: Auth Token
# Line 3: Your Twilio WhatsApp number, e.g.  whatsapp:+14155238886
# ---------------------------------------------------------------------------
with open('credentials.txt', 'r') as _f:
    _lines = [l.strip() for l in _f.read().splitlines() if l.strip()]
    ACCOUNT_SID   = _lines[0]
    AUTH_TOKEN    = _lines[1]
    WHATSAPP_FROM = _lines[2]   # must start with "whatsapp:"

twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
app = Flask(__name__)

# One Queue per user phone number
queue_list: dict = {}


@app.route('/webhook', methods=['POST'])
def webhook():
    """Entry point for all inbound WhatsApp messages from Twilio."""
    from_number        = request.form.get('From', '')          # e.g. whatsapp:+447700900000
    body               = request.form.get('Body', '').strip()
    num_media          = int(request.form.get('NumMedia', 0))
    media_url          = request.form.get('MediaUrl0')  if num_media > 0 else None
    media_content_type = request.form.get('MediaContentType0') if num_media > 0 else None

    logger.info('Inbound from %s | body=%r | media=%s', from_number, body, media_url)

    # Handle commands
    if body.lower() == '/start':
        twilio_client.messages.create(
            from_=WHATSAPP_FROM,
            to=from_number,
            body=(
                'Hi! I turn WhatsApp messages into Ace Attorney scenes.\n\n'
                'Send me messages one by one in this format:\n'
                '    *Name: message text*\n\n'
                'You can also send an image with a caption in the same format.\n'
                'After 5 seconds of silence I\'ll generate the video!'
            ),
        )
        return ('', 204)

    if body.lower() == '/about':
        twilio_client.messages.create(
            from_=WHATSAPP_FROM,
            to=from_number,
            body=(
                'Ace Attorney WhatsApp Bot\n'
                'Based on https://github.com/LuisMayo/ace-attorney-telegram-bot\n'
                'Powered by objection_engine'
            ),
        )
        return ('', 204)

    # Initialise a queue for this user if needed
    if from_number not in queue_list or queue_list[from_number] is None:
        queue_list[from_number] = Queue(
            from_number=from_number,
            chat_list=queue_list,
            client=twilio_client,
            whatsapp_from=WHATSAPP_FROM,
        )

    queue_list[from_number].add_message(body, media_url, media_content_type)

    # Twilio expects an empty 200 response when we handle replies ourselves
    return ('', 204)


def main():
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    main()
