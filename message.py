"""
message.py — WhatsApp message wrapper

Because WhatsApp (via Twilio) does not expose the original sender's name for
forwarded messages, users must send each line in the format:

    Name: message text

Images/stickers may be sent with an optional caption using the same format.
If no name prefix is found the sender's phone number is used as the character name.
"""

import re
import os
import requests
from objection_engine.beans.comment import Comment


class Message:
    def __init__(
        self,
        body: str,
        from_number: str,
        media_url: str | None = None,
        media_content_type: str | None = None,
        auth: tuple | None = None,
    ):
        """
        Parameters
        ----------
        body                : raw WhatsApp message text (may be empty for media-only)
        from_number         : sender's WhatsApp number (used as fallback name)
        media_url           : Twilio media URL if an image was attached
        media_content_type  : MIME type of the attached media
        auth                : (account_sid, auth_token) tuple for Twilio media download
        """

        # ------------------------------------------------------------------
        # Parse "Name: text" format
        # ------------------------------------------------------------------
        match = re.match(r'^([^:]+):\s*(.*)', body or '', re.DOTALL)
        if match:
            raw_name = match.group(1).strip()
            raw_text = match.group(2).strip()
        else:
            # No name prefix — use phone number as character name, whole body as text
            raw_name = from_number.replace('whatsapp:', '')
            raw_text = body or ''

        # Sanitise URLs in the message body
        self.text = re.sub(r'https?\S*', '(link)', raw_text) or '...'
        self.user = User(raw_name)

        # ------------------------------------------------------------------
        # Download attached image/sticker as evidence (if present)
        # ------------------------------------------------------------------
        if media_url and auth:
            self.evidence = self._download_media(media_url, media_content_type, auth)
        else:
            self.evidence = None

    # ------------------------------------------------------------------

    def _download_media(
        self,
        url: str,
        content_type: str | None,
        auth: tuple,
    ) -> str | None:
        """Download Twilio-hosted media and save it locally as a PNG."""
        try:
            response = requests.get(url, auth=auth, timeout=30)
            response.raise_for_status()

            # Derive a safe local filename from the URL
            unique_id = url.rstrip('/').split('/')[-1]
            ext = _content_type_to_ext(content_type)
            file_name = f'{unique_id}{ext}'

            with open(file_name, 'wb') as fh:
                fh.write(response.content)

            return file_name
        except Exception as exc:
            print(f'[message] Failed to download media: {exc}')
            return None

    # ------------------------------------------------------------------

    def to_comment(self) -> Comment:
        """Convert to the objection_engine Comment format."""
        return Comment(
            text_content=self.text,
            user_id=self.user.id,
            user_name=self.user.name,
            evidence_path=self.evidence,
        )


# ---------------------------------------------------------------------------

class User:
    def __init__(self, name: str):
        self.name = name
        # Derive a stable numeric ID from the name so objection_engine assigns
        # a consistent character sprite across all messages from this user.
        self.id = abs(hash(name)) % (10 ** 9)


# ---------------------------------------------------------------------------

def _content_type_to_ext(content_type: str | None) -> str:
    """Map a MIME type to a file extension."""
    mapping = {
        'image/jpeg': '.jpg',
        'image/png':  '.png',
        'image/gif':  '.gif',
        'image/webp': '.webp',
        'video/mp4':  '.mp4',
    }
    return mapping.get(content_type or '', '.png')
