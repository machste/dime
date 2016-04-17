import logging


class XmppMsgPassthrough(object):
    def __init__(self):
        self._logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)
        self._logger.info("using message filter '%s'", self)

    def get_text(self, msg):
        text = self._get_text(msg)
        self._logger.debug("text before filter: '%s', text after filter: '%s'", msg["body"], text)
        return text

    def _get_text(self, msg):
        return msg["body"]

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return self.__repr__()


class XmppMsgBadWordRefuser(XmppMsgPassthrough):
    def __init__(self):
        super(XmppMsgBadWordRefuser, self).__init__()

        # source https://en.wikipedia.org/wiki/Seven_dirty_words
        self._seven_dirty_words = ("shit", "piss", "fuck", "cunt", "cocksucker", "motherfucker", "tits")

    def _get_text(self, msg):
        text = msg["body"]
        if any(bad_word in text for bad_word in self._seven_dirty_words):
            user = repr(msg['from']).split('@')[0]
            text = "%s wanted me to say bad words! i can not do that!" % user

        return text


class XmppMsgBadWordReplacer(XmppMsgBadWordRefuser):
    def __init__(self):
        super(XmppMsgBadWordReplacer, self).__init__()

    def _get_text(self, msg):
        text = msg["body"]
        bad_words_found = set([word for word in self._seven_dirty_words if word in text])
        clean_text = []
        # remove all words which contain something from the 'bad word list'
        for word in text.split(' '):
            for bad_word in bad_words_found:
                if bad_word in word:
                    word = " 'bad word!' "
            clean_text.append(word)
        clean_text = " ".join(clean_text)

        return clean_text


class XmppMsgBadWordBlaming(XmppMsgBadWordRefuser):
    def __init__(self):
        super(XmppMsgBadWordBlaming, self).__init__()

    def _get_text(self, msg):
        text = msg["body"]

        bad_word_list = []
        for bad_word in self._seven_dirty_words:
            if bad_word in text:
               bad_word_list.append(bad_word)

        bad_words_found = list(set(bad_word_list))
        if len(bad_words_found):
            multiple = ""
            if len(bad_words_found) > 1:
                multiple = "words like "

            bad_word_string = self._get_text_enumeration(bad_words_found)
            user = repr(msg['from']).split('@')[0]
            text = "oh no! %s wanted me to say %s %s, i can not believe that! such a naughty guy!" % (user, multiple, bad_word_string)

        return text

    def _get_text_enumeration(self, word_list):
        if len(word_list) == 1:
            return word_list[0]

        ending = word_list[-2] + " and " + word_list[-1]

        text_enum = ""
        for word in word_list[:-2]:
            text_enum = text_enum + word + ", "

        text_enum = text_enum.strip(',')
        text_enum = text_enum + ending

        return text_enum
