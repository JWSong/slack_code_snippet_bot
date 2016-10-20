import json
import logging
import urllib

import aiohttp
from slacker import Slacker
from snippet_bot.snippet_executor import SnippetExecutor

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Bot(object):
    def __init__(self, token):
        self.token = token
        self.slack = Slacker(self.token)
        self.response = self.slack.rtm.start()

    async def run(self):
        assert self.response.body['ok'], "Error connecting to RTM."
        logger.info('rtm connected')

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.response.body['url']) as ws:
                async for msg in ws:
                    assert msg.tp == aiohttp.MsgType.text
                    msg = json.loads(msg.data)
                    if msg.get('file') is not None:
                        lang = msg['file'].get('filetype')
                        file_url = msg['file'].get('url_private_download')
                        if file_url:
                            req = urllib.request.Request(file_url)
                            req.add_header('Authorization', 'Bearer ' + self.token)
                            code = urllib.request.urlopen(req).read()

                            attachment = [{}]
                            user_input = msg['file'].get('initial_comment') and msg['file']['initial_comment']['comment'] or ''
                            with SnippetExecutor(code, lang, user_input) as (output, status):
                                color = status and '#DC143C' or '#32CD32'
                                attachment[0]['color'] = color
                                attachment[0]['text'] = output
                                attachment[0]['pretext'] = status == 0 and \
                                    "This is your output!" or \
                                    "Oops.. Sorry, something went wrong!"

                                self.slack.chat.post_message(
                                    msg.get('channel'), None, attachments=json.dumps(attachment), as_user=True
                                )
