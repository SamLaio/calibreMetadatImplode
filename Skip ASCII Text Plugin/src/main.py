from calibre import force_unicode
from calibre.utils import filenames


_previous_ascii_text = None


def preserve_unicode(orig):
    return force_unicode(orig)


def set_enabled(enabled):
    global _previous_ascii_text
    if enabled:
        if filenames.ascii_text is not preserve_unicode:
            _previous_ascii_text = filenames.ascii_text
            filenames.ascii_text = preserve_unicode
    elif filenames.ascii_text is preserve_unicode and _previous_ascii_text is not None:
        filenames.ascii_text = _previous_ascii_text
        _previous_ascii_text = None
