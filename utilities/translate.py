import googletrans

def Translate(message, lang_code):
    t = googletrans.Translator()
    trans = t.translate(message, dest=lang_code)
    return trans.text