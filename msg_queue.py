"""
msg_queue.py — Per-user render queue

Collects incoming messages and, after a 5-second quiet period, renders the
Ace Attorney video and sends it back via Twilio.

IMPORTANT — video delivery
--------------------------
Twilio's WhatsApp API requires a *publicly accessible* URL to send media;
it cannot accept a raw file upload.  You must implement `_get_public_video_url`
to host the rendered MP4 somewhere reachable (e.g. AWS S3, Google Cloud
Storage, or — for local development — an ngrok-exposed file server).

A simple ngrok dev helper is included as a comment at the bottom of this file.
"""

import os
import threading
from typing import List

from twilio.rest import Client
from objection_engine.renderer import render_comment_list

from message import Message


class Queue:
    def __init__(
        self,
        from_number: str,
        chat_list: dict,
        client: Client,
        whatsapp_from: str,
    ):
        self.from_number   = from_number
        self.chat_list     = chat_list
        self.client        = client
        self.whatsapp_from = whatsapp_from
        self.messages: List[Message] = []
        self.last_schedule: threading.Timer | None = None

        # Twilio credentials for authenticated media downloads
        self._auth = (client.username, client.password)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_message(
        self,
        body: str,
        media_url: str | None = None,
        media_content_type: str | None = None,
    ) -> None:
        """Append a message to the queue and (re)start the render timer."""
        msg = Message(
            body=body,
            from_number=self.from_number,
            media_url=media_url,
            media_content_type=media_content_type,
            auth=self._auth,
        )
        self.messages.append(msg)

        # Reset the 5-second countdown each time a new message arrives
        if self.last_schedule is not None:
            self.last_schedule.cancel()
        self.last_schedule = threading.Timer(5.0, self._create_video)
        self.last_schedule.start()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _estimate_time(thread: list) -> float:
        """Rough ETA in seconds based on character count and evidence count."""
        char_rate     = 0.089   # seconds per character
        evidence_rate = 2.0     # seconds per evidence image
        total_chars   = sum(len(item.text_content) for item in thread)
        evidences     = sum(1 for item in thread if item.evidence_path is not None)
        return round(char_rate * total_chars + evidence_rate * evidences, 2)

    def _send_text(self, body: str) -> None:
        """Send a plain-text WhatsApp message back to the user."""
        self.client.messages.create(
            from_=self.whatsapp_from,
            to=self.from_number,
            body=body,
        )

    def _send_video(self, public_url: str) -> None:
        """Send the rendered video to the user via a public media URL."""
        self.client.messages.create(
            from_=self.whatsapp_from,
            to=self.from_number,
            media_url=[public_url],
        )

    def _create_video(self) -> None:
        """Render the collected messages into a video and send it back."""
        # Mark this slot as free so new messages start a fresh queue
        self.chat_list[self.from_number] = None

        thread = [msg.to_comment() for msg in self.messages]

        # Use a filesystem-safe filename derived from the sender's number
        safe_id         = re.sub(r'\W', '_', self.from_number)
        output_filename = f'{safe_id}.mp4'

        eta_secs = Queue._estimate_time(thread)
        self._send_text(
            f'⚖️  Started processing your Ace Attorney scene!\n\n'
            f'ETA: {int(eta_secs / 60)} min(s) {round(eta_secs % 60, 2)} secs.'
        )

        render_comment_list(thread, output_filename=output_filename, resolution_scale=2)

        self._send_text('✅  Done! Uploading video…')

        try:
            public_url = self._get_public_video_url(output_filename)
            self._send_video(public_url)
        except NotImplementedError:
            self._send_text(
                '⚠️  Video rendered but could not be sent automatically.\n'
                'Implement `_get_public_video_url` in msg_queue.py to enable delivery.'
            )

        self._clean(output_filename, thread)

    def _get_public_video_url(self, filename: str) -> str:
        """
        Upload *filename* to a public host and return its URL.

        You must implement this for video delivery to work.

        Examples
        --------
        AWS S3:
            import boto3
            s3 = boto3.client('s3')
            s3.upload_file(filename, 'my-bucket', filename, ExtraArgs={'ACL': 'public-read'})
            return f'https://my-bucket.s3.amazonaws.com/{filename}'

        Google Cloud Storage:
            from google.cloud import storage
            gcs = storage.Client()
            bucket = gcs.bucket('my-bucket')
            blob = bucket.blob(filename)
            blob.upload_from_filename(filename)
            blob.make_public()
            return blob.public_url

        Local dev with ngrok file server (see bottom of this file):
            return f'https://<your-ngrok-id>.ngrok.io/videos/{filename}'
        """
        raise NotImplementedError(
            'Implement _get_public_video_url() to return a publicly accessible '
            'video URL so Twilio can deliver the video to WhatsApp.'
        )

    def _clean(self, output_filename: str, thread: list) -> None:
        """Remove temporary local files after upload."""
        for path in [output_filename] + [m.evidence_path for m in thread if m.evidence_path]:
            try:
                os.remove(path)
            except Exception as exc:
                print(f'[queue] cleanup error: {exc}')


# ---------------------------------------------------------------------------
# (Optional) Minimal local file server for development
# ---------------------------------------------------------------------------
# Run this alongside main.py to serve rendered videos over ngrok:
#
#   import http.server, socketserver, threading, pathlib
#
#   def start_file_server(directory='.', port=8080):
#       handler = http.server.SimpleHTTPRequestHandler
#       with socketserver.TCPServer(('', port), handler) as httpd:
#           httpd.serve_forever()
#
#   threading.Thread(target=start_file_server, daemon=True).start()
#
# Then set your ngrok tunnel to port 8080 and return:
#   f'https://<id>.ngrok.io/{filename}'
# from _get_public_video_url.

import re  # used in _create_video — imported here to keep it at module scope
