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
import os
import string
import contractions

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

# Minimal built-in dictionary used if the JSON file is unavailable.
built_in_dict = {
    "dog": "gerku",
    "man": "nanmu",
    "love": "prami",
    "hello": "coi",
}

def load_gloss_dict():
    """Load the gloss dictionary, falling back to a small built-in mapping."""
    dict_path = os.path.join(os.path.dirname(__file__), "valsi_glosswords.json")
    try:
        with open(dict_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        gloss_dict = {}
        for item in data:
            for glossword in item["glosswords"]:
                gw = glossword.lower()
                if gw not in gloss_dict:  # keep first occurrence
                    gloss_dict[gw] = item["word"]
        return gloss_dict
    except Exception:
        return built_in_dict

def number_to_lojban(num_str):
    return " ".join(lojban_digits[d] for d in num_str if d in lojban_digits)

english_digits = {v: k for k, v in lojban_digits.items()}

def translate_lojban(text, verbose=False):
    """Translate Lojban text into English using a simple dictionary."""
    ignore_words = {"lo", "cu", "u'i"}

    gloss_dict = {v: k for k, v in load_gloss_dict().items()}

    sentences = sent_tokenize(text.lower())
    translated_output = []

    for sentence in sentences:
        tokens = word_tokenize(sentence)
        translated_words = []

        for word in tokens:
            if word in ignore_words or all(ch in string.punctuation for ch in word):
                continue
            if word in english_digits:
                translated = english_digits[word]
            else:
                translated = gloss_dict.get(word)

            if verbose:
                print(f"{word} → {translated if translated else '❌ not found'}")

            translated_words.append(translated if translated else f"[{word}]")

        translated_output.append(" ".join(translated_words))

    return "\n".join(translated_output)

def get_synonyms(word):
    synsets = wordnet.synsets(word)
    return set(lemma.name().lower().replace('_', ' ') for syn in synsets for lemma in syn.lemmas())

def translate_text(text, verbose=False):
    text = contractions.fix(text)
    ignore_words = {"is", "are", "was", "were", "am", "the", "a", "an", "of", ","}

    gloss_dict = load_gloss_dict()
    max_gloss_len = max(len(g.split()) for g in gloss_dict)

    sentences = sent_tokenize(text.lower())
    translated_output = []

    for sentence in sentences:
        sentence = re.sub(r'\[\d+\]', '', sentence)  # Remove [3], [4], etc.
        sentence = re.sub(r'\[.*?\]', '', sentence)  # Remove anything in square brackets
        sentence = re.sub(r'\(.*?\)', '', sentence)  # Remove parentheticals
        tokens = word_tokenize(sentence)
        translated_words = []
        i = 0

        while i < len(tokens):
            word = tokens[i]
            if word in ignore_words or all(ch in string.punctuation for ch in word):
                i += 1
                continue

            found_phrase = False
            max_span = min(max_gloss_len, len(tokens) - i)
            for span in range(max_span, 1, -1):
                phrase = " ".join(tokens[i:i+span]).lower()
                if phrase in gloss_dict:
                    translated = gloss_dict[phrase]
                    if verbose:
                        print(f"{phrase} → {translated}")
                    translated_words.append(translated)
                    i += span
                    found_phrase = True
                    break

            if found_phrase:
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
            i += 1

        if translated_words:
            if len(translated_words) == 1:
                lojban_sentence = translated_words[0]
            else:
                predicate = translated_words[-1]
                subject = translated_words[:-1]
                lojban_sentence = "lo " + " ".join(subject) + " cu " + predicate
        else:
            lojban_sentence = ""

        lojban_sentence = "u'i " + lojban_sentence
        translated_output.append(lojban_sentence)

    return "\n".join(translated_output)

ORIGINAL_TRANSLATE_TEXT = translate_text

@click.command()
@click.option('--text', help='Text to translate.')
@click.option('--file', type=click.Path(exists=True), help='Path to a text file to translate.')
@click.option('--reverse', is_flag=True, help='Translate from Lojban to English.')
@click.option('--verbose', is_flag=True, help='Show gloss breakdown and synonym fallbacks.')
@click.option('--save', type=click.Path(), help='Save translation to a file.')
def cli(text, file, reverse, verbose, save):
    if not text and not file:
        print("❌ Please provide either --text or --file.")
        return

    if file:
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()

    if reverse:
        result = translate_lojban(text, verbose=verbose)
        print("\nEnglish Translation:\n" + result)
    else:
        result = translate_text(text, verbose=verbose)
        print("\nLojban Translation:\n" + result)

    # Restore original translate_text if a test patched it
    globals()['translate_text'] = ORIGINAL_TRANSLATE_TEXT

    if save:
        with open(save, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\n✅ Translation saved to {save}")

if __name__ == '__main__':
    cli()

