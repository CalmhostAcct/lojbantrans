#!/usr/bin/env python3
"""
Lojban Translator (spaCy version)
---------------------------------
This tool translates English ↔ Lojban using a gloss dictionary and spaCy’s NLP pipeline.
It replaces NLTK tokenization and lemmatization with spaCy, adds semantic similarity fallback,
and supports both text and file-based input.
"""

import spacy
import json
import click
import re
import os
import string
import contractions

# === Load spaCy model ===
# Use en_core_web_lg for better vector similarity; _sm works if space is limited.
try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    nlp = spacy.load("en_core_web_sm")
    print("⚠️ Using small spaCy model (no word vectors). For better translation, install: python -m spacy download en_core_web_lg")

# === Digit mappings ===
lojban_digits = {
    "0": "no", "1": "pa", "2": "re", "3": "ci", "4": "vo",
    "5": "mu", "6": "xa", "7": "ze", "8": "bi", "9": "so"
}
english_digits = {v: k for k, v in lojban_digits.items()}

# === Built-in fallback dictionary ===
built_in_dict = {
    "dog": "gerku",
    "man": "nanmu",
    "love": "prami",
    "hello": "coi",
}

# === Dictionary loader ===
def load_gloss_dict():
    """Load the Lojban-English dictionary, fallback to a minimal built-in dict."""
    dict_path = os.path.join(os.path.dirname(__file__), "valsi_glosswords.json")
    try:
        with open(dict_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        gloss_dict = {}
        for item in data:
            for glossword in item["glosswords"]:
                gw = glossword.lower()
                if gw not in gloss_dict:
                    gloss_dict[gw] = item["word"]
        return gloss_dict
    except Exception:
        return built_in_dict

# === Utilities ===
def number_to_lojban(num_str):
    """Convert numeric string to Lojban digits."""
    return " ".join(lojban_digits[d] for d in num_str if d in lojban_digits)

def find_closest_gloss(word, gloss_dict, threshold=0.70):
    """Find semantically closest gloss entry using spaCy vector similarity."""
    if not word or not nlp(word).has_vector:
        return None
    word_vec = nlp(word)
    best_match, best_sim = None, 0
    for gloss in gloss_dict.keys():
        gloss_vec = nlp(gloss)
        if gloss_vec.has_vector:
            sim = word_vec.similarity(gloss_vec)
            if sim > best_sim:
                best_match, best_sim = gloss, sim
    return gloss_dict[best_match] if best_sim >= threshold else None

# === Translation: English → Lojban ===
def translate_text(text, verbose=False):
    text = contractions.fix(text)
    gloss_dict = load_gloss_dict()
    ignore_words = {"is", "are", "was", "were", "am", "the", "a", "an", "of", ",", "."}
    sentences = [s.text.strip() for s in nlp(text).sents]

    translated_output = []

    for sentence in sentences:
        doc = nlp(sentence.lower())
        translated_words = []

        for token in doc:
            if token.text in ignore_words or all(ch in string.punctuation for ch in token.text):
                continue

            # Numbers
            if token.like_num:
                translated = number_to_lojban(token.text)
            else:
                lemma = token.lemma_.lower()
                translated = gloss_dict.get(lemma)

                # Try phrase-level match (two- or three-word spans)
                if not translated:
                    for span_len in (3, 2):
                        for i in range(len(doc) - span_len + 1):
                            phrase = " ".join([t.lemma_.lower() for t in doc[i:i+span_len]])
                            if phrase in gloss_dict:
                                translated = gloss_dict[phrase]
                                break
                        if translated:
                            break

                # Try vector similarity fallback
                if not translated:
                    translated = find_closest_gloss(lemma, gloss_dict)

            if verbose:
                print(f"{token.text} → {translated if translated else '❌ not found'}")

            translated_words.append(translated if translated else f"[{token.text}]")

        # Assemble into a Lojban sentence (simplistic SVO pattern)
        if translated_words:
            if len(translated_words) == 1:
                lojban_sentence = translated_words[0]
            else:
                predicate = translated_words[-1]
                subject = translated_words[:-1]
                lojban_sentence = "lo " + " ".join(subject) + " cu " + predicate
        else:
            lojban_sentence = ""

        translated_output.append("u'i " + lojban_sentence)

    return "\n".join(translated_output)

# === Translation: Lojban → English ===
def translate_lojban(text, verbose=False):
    gloss_dict = {v: k for k, v in load_gloss_dict().items()}
    ignore_words = {"lo", "cu", "u'i"}

    sentences = [s.text.strip() for s in nlp(text).sents]
    translated_output = []

    for sentence in sentences:
        tokens = [t.text for t in nlp(sentence.lower())]
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

# === CLI Interface ===
@click.command()
@click.option('--text', help='Text to translate.')
@click.option('--file', type=click.Path(exists=True), help='Path to a text file to translate.')
@click.option('--reverse', is_flag=True, help='Translate from Lojban to English.')
@click.option('--verbose', is_flag=True, help='Show detailed gloss and similarity matches.')
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

    if save:
        with open(save, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\n✅ Translation saved to {save}")

if __name__ == '__main__':
    cli()
