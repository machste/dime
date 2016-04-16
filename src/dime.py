import sys
import logging
import time
import threading
import queue

import synth


logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
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
        self._logger = logging.getLogger(self.__class__.__name__)
        self._event_queue = queue.Queue(maxsize=max_event_queue_size)
        self._speech_synth = synth.SpeechSynth(synthesizer=synth.Festival)

    @property
    def event_queue(self):
        return self._event_queue

    def check_system(self):
        return self._speech_synth.check_system()

    def run(self):
        self._logger.info("in start, waiting on event queue...")

        while not self.stopped():

            try:
                queue_element = self._event_queue.get(timeout=1)
            except queue.Empty:
                self._logger.debug("timeout on empty queue, continue")
                continue

            self._logger.info("process event '%s' "
                              "using %s" % (queue_element, self._speech_synth))
            self._speech_synth.say(queue_element)

        self._logger.info("graceful exit from main loop")


if __name__ == "__main__":

    LOGGER.info("starting application")
    DIME = Dime()

    if not DIME.check_system():
        LOGGER.error("system not ready, exit immediately")
        sys.exit(1)

    DIME.start()

    for counter in range(20):
        if DIME.event_queue.full():
            LOGGER.warning("dime event queue full (queue size: %d), "
                           "wait...", DIME.event_queue.qsize())
            time.sleep(0.3)
            continue

        LOGGER.info("put element to dime element queue...")
        DIME.event_queue.put("i am text number %d" % counter)

        counter += 1

    DIME.stop()
    DIME.join()

    LOGGER.info("exit gracefully")
