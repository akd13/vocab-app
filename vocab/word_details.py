from nltk.corpus import wordnet


def get_definition_synonyms(word):
    try:
        synsets = wordnet.synsets(word)

        if synsets:
            first_synset = synsets[0]
            definition = first_synset.definition()

            synonyms = [lemma.name() for synset in synsets for lemma in synset.lemmas()]

            return definition, synonyms[:5]
        else:
            return "No definitions found", []

    except Exception as e:
        print("Exception is", e)
        return "An error occurred", []


# # Example usage:
# word = "example"
# definition, synonyms = get_definition_synonyms(word)
# print("WORD IS", word)
# print("DEFINITION IS", definition)
# print("SYNONYMS ARE", synonyms)
