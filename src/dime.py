import sys
import logging
import time
import threading
import queue
import copy
from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout

import synth


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)-12s %(levelname)-8s %(name)-16s %(message)s')
LOGGER = logging.getLogger(__name__)


class MessageProxyXMPP(ClientXMPP):
    def __init__(self, jid, password, message_queue):
        super(MessageProxyXMPP, self).__init__(jid, password)
        self._logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)
        self._message_queue = message_queue

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

    def session_start(self, event):
        self.send_presence()
        try:
            self.get_roster()
        except IqError as err:
            self._logger.error('There was an error getting the roster')
            self._logger.error(err.iq['error']['condition'])
            self.disconnect()
        except IqTimeout:
            self._logger.error('Server is taking too long to respond')
            self.disconnect()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):

            if self._message_queue.full():
                msg.reply("Can not synthetisize your message, too many messages pending").send()
                return

            # FIXME: using copy here due to reuse of msg object for response
            msg_cpy = copy.copy(msg)
            self._message_queue.put(msg_cpy)

            msg.reply("thanks for sending message '%s', message enqueued for synthesis... "
                      "(queue fill level: %d / %d)" % (msg['body'].strip(),
                                                       self._message_queue.qsize(),
                                                       self._message_queue.maxsize)).send()


class StoppableThread(threading.Thread):
    """thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition.

    source: http://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread-in-python
    """
    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class Dime(StoppableThread):

    def __init__(self, max_event_queue_size=4):
        super(Dime, self).__init__()
        self._logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)
        self._event_queue = queue.Queue(maxsize=max_event_queue_size)
        self._speech_synth = synth.SpeechSynth(synthesizer=synth.Festival)
        self._xmpp_mp = XmppMessageProcessor()

    @property
    def event_queue(self):
        return self._event_queue

    def check_system(self):
        return self._speech_synth.check_system()

    def run(self):
        self._logger.info("running, waiting on event queue...")
        while not self.stopped():
            try:
                queue_element = self._event_queue.get(timeout=1)
            except queue.Empty:
                self._logger.debug("timeout on empty queue, continue")
                continue

            text_to_say = self._xmpp_mp.get_text(queue_element)
            self._speech_synth.say(text_to_say)

        self._logger.info("exit gracefully")


class XmppMessageProcessor(object):
    def __init__(self):
        self._logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

    def get_text(self, msg):
        text = msg["body"]
        if "fuck" in msg["body"]:

            self._logger.fatal(msg['from'])

            text = "%s wanted me to say bad words!" % msg['from']
        return text


class DimeRunner(object):

    def __init__(self):
        self._logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

        # compose configuration
        self._dime_config = dict()
        self._dime_config["xmpp"] = dict()
        self._dime_config["xmpp"]["jid"] = "sally@10.0.30.10"
        self._dime_config["xmpp"]["pwd"] = "beer"

        self._dime = Dime()
        self._xmpp_proxy = MessageProxyXMPP(self._dime_config["xmpp"]["jid"],
                                            self._dime_config["xmpp"]["pwd"],
                                            self._dime.event_queue)

    def __del__(self):
        self._logger.debug("destructor called")
        self.stop()

    def start(self):
        if not self._dime.check_system():
            raise Exception("dime system not ready, exit immediately")

        self._dime.start()
        self._xmpp_proxy.connect()

        #         self._logger.fatal(self._xmpp.credentials)
        #
        # self._logger.fatal(self._xmpp.state)
        #
        # self._logger.fatal(ret)
        #
        # if not ret :
        #     self._logger.error("unable to connect jabber id '%s'", self._jabber_id)
        #     return

        self._xmpp_proxy.process(block=False)

    def stop(self):
        if self._xmpp_proxy:
            self._xmpp_proxy.abort()
        if self._dime:
            self._dime.stop()
            self._dime.join()

    def is_up_and_running(self):
        system_status = True

        bad_state = "disconnected"
        if self._xmpp_proxy.state.current_state() == bad_state:
            self._logger.error("%s reports state '%s'", self._xmpp_proxy, bad_state)
            system_status = False

        if not self._dime.is_alive():
            self._logger.error("%s thread ist dead", self._dime)
            system_status = False

        return system_status


if __name__ == "__main__":

    LOGGER.info("starting application")
    DIME_RUNNER = DimeRunner()

    try:
        DIME_RUNNER.start()
    except Exception as exception:
        LOGGER.error(exception)
        sys.exit(1)

    while True:
        try:
            LOGGER.debug("in main idle loop")
            if not DIME_RUNNER.is_up_and_running():
                break

            time.sleep(1)

        except KeyboardInterrupt:
            LOGGER.info("KeyboardInterrupt caught, shut application down")
            break

    DIME_RUNNER.stop()
    LOGGER.info("exit gracefully")
