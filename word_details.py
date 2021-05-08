from PyDictionary import PyDictionary

dictionary = PyDictionary()


def get_definition_synonyms(word):
    try:
        return list(dictionary.meaning(word, disable_errors=True).values())[0][:2], list(dictionary.synonym(word))[:5]
    except Exception:
        return [], []
