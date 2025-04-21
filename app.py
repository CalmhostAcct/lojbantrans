import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import json
import click
import re
import contextlib
import io

# === Silent NLTK downloader ===
def silent_nltk_download(package):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        nltk.download(package, quiet=True)

try:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
       nltk.data.find("tokenizers/punkt")
except LookupError:
    silent_nltk_download("punkt")

try:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
       nltk.data.find("corpora/wordnet")
except LookupError:
    silent_nltk_download("wordnet")

# === Translator logic ===

lemmatizer = WordNetLemmatizer()

lojban_digits = {
    "0": "no", "1": "pa", "2": "re", "3": "ci", "4": "vo",
    "5": "mu", "6": "xa", "7": "ze", "8": "bi", "9": "so"
}

def number_to_lojban(num_str):
    return " ".join(lojban_digits[d] for d in num_str if d in lojban_digits)

def get_synonyms(word):
    synsets = wordnet.synsets(word)
    return set(lemma.name().lower().replace('_', ' ') for syn in synsets for lemma in syn.lemmas())

def translate_text(text, verbose=False):
    ignore_words = {"is", "are", "was", "were", "am", "the", "a", "an", "of"}

    with open("valsi_glosswords.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    gloss_dict = {
        glossword.lower(): item["word"]
        for item in data
        for glossword in item["glosswords"]
    }

    sentences = sent_tokenize(text.lower())
    translated_output = []

    for sentence in sentences:
        sentence = re.sub(r'\(.*?\)', '', sentence)  # remove parentheticals
        tokens = word_tokenize(sentence)
        translated_words = []

        for word in tokens:
            if word in ignore_words:
                continue
            if word.isdigit():
                translated = number_to_lojban(word)
            else:
                lem_word = lemmatizer.lemmatize(word)
                translated = gloss_dict.get(lem_word)

                if not translated:
                    for synonym in get_synonyms(lem_word):
                        translated = gloss_dict.get(synonym)
                        if translated:
                            break

            if verbose:
                print(f"{word} → {translated if translated else '❌ not found'}")

            translated_words.append(translated if translated else f"[{word}]")

        if translated_words:
            predicate = translated_words[-1]
            subject = translated_words[:-1]
            lojban_sentence = "lo " + " ".join(subject) + " cu " + predicate
        else:
            lojban_sentence = ""

        lojban_sentence = "u'i " + lojban_sentence
        translated_output.append(lojban_sentence)

    return "\n".join(translated_output)

@click.command()
@click.option('--text', help='English text to translate to Lojban.')
@click.option('--file', type=click.Path(exists=True), help='Path to a text file to translate.')
@click.option('--verbose', is_flag=True, help='Show gloss breakdown and synonym fallbacks.')
@click.option('--save', type=click.Path(), help='Save translation to a file.')
def cli(text, file, verbose, save):
    if not text and not file:
        print("❌ Please provide either --text or --file.")
        return

    if file:
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()

    result = translate_text(text, verbose=verbose)
    print("\nLojban Translation:\n" + result)

    if save:
        with open(save, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\n✅ Translation saved to {save}")

if __name__ == '__main__':
    cli()
