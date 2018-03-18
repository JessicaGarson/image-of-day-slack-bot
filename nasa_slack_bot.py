import os
import time
import re
from slackclient import SlackClient

from nasa import nasa_image

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
bot_id = None

RTM_READ_DELAY = 1
SPACE_COMMAND = 'image'
MENTION_REGEX = '^<@(|[WU].+?)>(.*)'


def parse_bot_commands(slack_events):
    for event in slack_events:
        if event['type'] == 'message' and not 'subtype' in event:
            user_id, message = parse_direct_mention(event['text'])


def parse_direct_mention(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel):
    default_response = 'Not sure what you mean. Try *{}* to get the image of the day.'.format(SPACE_COMMAND)
    response = None
    if command.startswith(SPACE_COMMAND):
        response = nasa_image()

    slack_client.api_call(
        'chat.postMessage',
        channel=channel,
        text=response or default_response
    )


if __name__ == '__main__':
    if slack_client.rtm_connect(with_team_state=False):
        print('NASA image of the day bot connected and running!')
        bot_id = slack_client.api_call('auth.test')['user_id']
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print('Connection failed. Exception traceback printed above.')
