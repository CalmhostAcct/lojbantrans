import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
import json
import click

# Ensure 'punkt' tokenizer is available
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

@click.command()
@click.option('--text', prompt='English text to translate',
              help='The English text you want to translate to Lojban.')
def translate_text(text):
    ignore_words = {"is", "are", "was", "were", "am", "the", "a", "an", "of"}
    text_to_translate = text.lower()
    tokens = word_tokenize(text_to_translate)
    translated_words = []

    with open("valsi_glosswords.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    gloss_dict = {
        glossword.lower(): item["word"]
        for item in data
        for glossword in item["glosswords"]
    }

    for word in tokens:
        if word in ignore_words:
            continue
        translated = gloss_dict.get(word)
        translated_words.append(translated if translated else word)

    if translated_words:
        predicate = translated_words[-1]
        subject = translated_words[:-1]
        lojban_sentence = "lo " + " ".join(subject) + " cu " + predicate
    else:
        lojban_sentence = ""

    lojban_sentence = "u'i " + lojban_sentence
    print("Lojban Translation:\n" + lojban_sentence)


if __name__ == '__main__':
    translate_text()

