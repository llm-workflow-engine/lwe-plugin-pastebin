import os
import json
from urllib.parse import urlparse, urlunparse

from lwe.core.plugin import Plugin
import lwe.core.util as util

from pbwrap import Pastebin as PbWrap

EXPIRE_TIMES = [
    "N",
    "10M",
    "1H",
    "1D",
    "1W",
    "2W",
    "1M",
    "6M",
    "1Y",
]

VISIBILITY_MAP = {
    "public": 0,
    "unlisted": 1,
    "private": 2,
}


class Pastebin(Plugin):
    """
    Post a conversation to https://pastebin.com
    """

    def default_config(self):
        return {
            "paste_defaults": {
                "expire": "N",
                "format": "text",
                "visibility": "public",
            },
            "include_raw_link": False,
        }

    def setup(self):
        self.log.info(
            f"Setting up pastebin plugin, running with backend: {self.backend.name}"
        )
        self.api_developer_key = os.environ.get("PASTEBIN_API_DEVELOPER_KEY")
        self.api_user_key = os.environ.get("PASTEBIN_API_USER_KEY")
        self.default_expire = self.config.get("plugins.pastebin.paste_defaults.expire")
        self.default_format = self.config.get("plugins.pastebin.paste_defaults.format")
        self.default_visibility = self.config.get(
            "plugins.pastebin.paste_defaults.visibility"
        )
        self.include_raw_link = self.config.get("plugins.pastebin.include_raw_link")

    def get_shell_completions(self, _base_shell_completions):
        commands = {}
        commands[util.command_with_leader("pastebin")] = {
            "public": util.list_to_completion_hash(EXPIRE_TIMES),
            "unlisted": util.list_to_completion_hash(EXPIRE_TIMES),
            "private": util.list_to_completion_hash(EXPIRE_TIMES),
        }
        return commands

    def role_content_wrapper(self, role):
        return f"####################################\n{role.upper()}\n####################################"

    def content_from_conversation(self, conversation):
        content_parts = []
        for message in conversation["messages"]:
            content_parts.append(self.role_content_wrapper(message["role"]))
            if isinstance(message["message"], dict):
                message_content = json.dumps(message["message"], indent=2)
            else:
                message_content = message["message"]
            content_parts.append(message_content)
        return "\n\n".join(content_parts)

    def build_raw_url(self, url):
        parsed_url = urlparse(url)
        last_part = parsed_url.path.split("/")[-1]
        raw_url = urlunparse(
            (parsed_url.scheme, parsed_url.netloc, "/raw/" + last_part, "", "", "")
        )
        return raw_url

    def paste(self, conversation, visibility, expire, title=None):
        content = self.content_from_conversation(conversation)
        title = title or conversation["conversation"]["title"]
        self.log.info(
            f"Pasting conversation ({len(conversation['messages'])} messages) with visibility: {visibility}, expire: {expire}, title: {title}"
        )
        pb = PbWrap(self.api_developer_key)
        if self.api_user_key:
            pb.api_user_key = self.api_user_key
        paste_url = pb.create_paste(
            content,
            api_paste_private=visibility,
            api_paste_name=title,
            api_paste_expire_date=expire,
            api_paste_format=self.default_format,
        )
        if not util.is_valid_url(paste_url):
            raise ValueError(paste_url)
        return paste_url

    def command_pastebin(self, args):
        """
        Post a conversation to https://pastebin.com

        Arguments:
            visibility: Optional, one of: public, unlisted, private
            expire_time: Optional, on of: N, 10M, 1H, 1D, 1W, 2W, 1M, 6M, 1Y
            title: Optional, custom title, if not provided, conversation title will be used.

        Examples:
            # Use the defaults.
            {COMMAND}
            # An unlisted paste.
            {COMMAND} unlisted
            # Custom everything
            {COMMAND} public 10M My custom title
        """
        success, conversation_data, user_message = self.backend.get_conversation()
        if not success:
            return success, conversation_data, user_message
        if not conversation_data:
            return False, None, "No current conversation"
        visibility = self.default_visibility
        expire = self.default_expire
        title = None
        try:
            visibility, expire, title = args.split(maxsplit=2)
        except ValueError:
            try:
                visibility, expire = args.split()
            except ValueError:
                if args:
                    visibility = args
        if visibility in VISIBILITY_MAP:
            visibility = VISIBILITY_MAP[visibility]
        else:
            return False, None, f"Invalid visibility: {visibility}"
        if expire not in EXPIRE_TIMES:
            return False, None, f"Invalid expire: {expire}"
        try:
            result = self.paste(conversation_data, visibility, expire, title)
        except Exception as e:
            return False, None, e
        user_message_parts = [f"Paste URL: {result}"]
        if self.include_raw_link:
            user_message_parts.append(f"Raw URL: {self.build_raw_url(result)}")
        return True, result, "\n".join(user_message_parts)
