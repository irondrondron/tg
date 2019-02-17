import logging
import os
import threading

logger = logging.getLogger(__name__)


class Controller:
    """
    # MVC
    # Model is data from telegram
    # Controller handles keyboad events
    # View is terminal vindow
    """

    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.lock = threading.Lock()

    def init(self):
        self.view.draw_chats(
            self.model.current_chat,
            self.model.get_chats()
        )
        msgs = self.model.get_current_msgs()
        self.view.draw_msgs(self.model.get_current_msg(), msgs)

    def run(self):
        try:
            self.handle()
        except Exception as e:
            logger.exception('Error happened on run')

    # def send_msg(self):
    #     import curses
    #     # curses.nocbreak()
    #     curses.echo()
    #     curses.curs_set(1)

    #     buff = ''
    #     while True:
    #         key = self.view.get_key(
    #             self.view.chats.h, self.view.chats.w)
    #         logger.info('Pressed in send msg: %s', key)
    #         if key == '^J':
    #             break
    #         elif key == '^G':
    #             # curses.cbreak()
    #             # curses.noecho()
    #             # self.view.chats.win.refresh()
    #             buff = ''
    #             break
    #         buff += key

    #     logger.info('Sending msg: %s', buff)
    #     curses.cbreak()
    #     curses.noecho()
    #     curses.curs_set(0)

    #     chat_id = self.model.get_current_chat_id()
    #     self.model.send_msg(chat_id, buff)
    #     self.view.draw_chats(
    #         self.model.current_chat,
    #         self.model.get_chats()
    #     )
    #     msgs = self.model.get_current_msgs()
    #     self.view.draw_msgs(msgs)

    def handle_msgs(self):
        while True:

            key = self.view.get_key(self.view.chats.h, self.view.chats.w)
            logger.info('Pressed key: %s', key)
            if key == 'q':
                return 'QUIT'
            elif key == ']':
                if self.model.next_chat():
                    self.refresh_chats()
            elif key == '[':
                if self.model.prev_chat():
                    self.refresh_chats()
            elif key == 'j':
                if self.model.next_msg():
                    self.refresh_msgs()
            elif key == 'k':
                if self.model.prev_msg():
                    self.refresh_msgs()
            elif key == 'e':
                # edit msg
                pass
            elif key == 'r':
                # reply to this msg
                # print to status line
                pass
            elif key == 'i':
                # write new message
                pass
            elif key == 'h':
                return 'BACK'

    def handle(self):
        self.handle_chats()

    def refresh_chats(self):
        self.view.draw_chats(
            self.model.current_chat,
            self.model.get_chats()
        )
        msgs = self.model.get_current_msgs()
        self.view.draw_msgs(self.model.get_current_msg(), msgs)

    def refresh_msgs(self):
        msgs = self.model.get_current_msgs()
        self.view.draw_msgs(self.model.get_current_msg(), msgs)

    def handle_chats(self):
        while True:

            key = self.view.get_key(self.view.chats.h, self.view.chats.w)
            logger.info('Pressed key: %s', key)
            if key == 'q':
                return
            elif key == 'l':
                rc = self.handle_msgs()
                if rc == 'QUIT':
                    return

            elif key == 'j':
                is_changed = self.model.next_chat()
                if is_changed:
                    self.refresh_chats()

            elif key == 'k':
                is_changed = self.model.prev_chat()
                if is_changed:
                    self.refresh_chats()

    def update_handler(self, update):
        logger.debug('===============Received: %s', update)
        _type = update['@type']
        if _type == 'updateNewMessage':
            logger.debug('Updating... new message')
            # with self.lock:
            chat_id = update['message']['chat_id']
            self.model.msgs.msgs[chat_id].append(update['message'])
            msgs = self.model.get_current_msgs()
            self.view.draw_msgs(msgs)
            try:
                notify(update['message']['content']['text']['text'])
            except Exception:
                logger.exception(
                    'Error happened on notify: %s', update['message'])
            # message_content = update['message']['content'].get('text', {})
        # we need this because of different message types: photos, files, etc.
        # message_text = message_content.get('text', '').lower()

        # if message_text == 'ping':
        #     chat_id = update['message']['chat_id']
        #     # print(f'Ping has been received from {chat_id}')
        #     self.tg.send_message(
        #         chat_id=chat_id,
        #         text='pong',
        #     )


def notify(msg, subtitle='New message', title='Telegram'):
    msg = '-message {!r}'.format(msg)
    subtitle = '-subtitle {!r}'.format(subtitle)
    title = '-title {!r}'.format(title)
    sound = '-sound default'
    icon_path = os.path.join(os.path.dirname(__file__), 'tg.png')
    icon = f'-appIcon {icon_path}'
    cmd = '/usr/local/bin/terminal-notifier'

    logger.debug('####: %s', f'{cmd} {icon} {sound} {title} {subtitle} {msg}')
    os.system(
        f'{cmd} {icon} {sound} {title} {subtitle} {msg}'
    )