from django.utils.translation import activate, get_language, gettext


def translate(language, text):
    cur_language = get_language()
    try:
        activate(language)
        text =  gettext(text)
    finally:
        activate(cur_language)
    return text