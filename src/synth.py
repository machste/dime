import logging
import os
import inspect

class SpeechSynthInterface(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

    def say(self, text):
        self._log_error()

    def check_system(self):
        self._log_error()

    def _log_error(self):
        self.logger.warning("template function called")


class Festival(SpeechSynthInterface):
    BINARY_NAME = "festival"

    def __init__(self):
        super(Festival, self).__init__()

    def say(self, text):
        language = "english"
        command_string = 'echo "%s" | %s --tts ' \
                         '--language %s' % (text, self.BINARY_NAME, language)

        self.logger.debug("fire up system command '%s' to synthesize '%s'", command_string, text)

        os.system(command_string)

    def check_system(self):
        self.logger.debug("check for binary '%s' on system", Festival.BINARY_NAME)
        command_string = "which %s" % Festival.BINARY_NAME
        ret = os.system(command_string)
        if ret == 0:
            return True

        self.logger.error("binary not found on your system")


class SpeechSynth(SpeechSynthInterface):

    def __init__(self, synthesizer=Festival):
        super(SpeechSynth, self).__init__()
        self._synthesizer = synthesizer()
        self.logger.debug("configure '%s' as "
                          "synthesizer", self._synthesizer.__class__.__name__)

    def __repr__(self):
        return "SpeechSynth (%s)" % self._synthesizer.__class__.__name__

    def __str__(self):
        return self.__repr__()

    def say(self, text):
        self._synthesizer.say(text)

    def check_system(self):
        return self._synthesizer.check_system()
