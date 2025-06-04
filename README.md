

# lojbantrans: Proof-of-concept English-Lojban translation engine

**`lojbantrans`** is a Python-based proof-of-concept command-line engine for translating English text into Lojban using a glossword dictionary. It can be used standalone or as a starting point.  
It produces readable, Lojban-inspired output that’s great for learners and conlang explorers.

---

## 🚀 How to Use

### 1. Install dependencies  
```bash
pip install -r requirements.txt
```

### 2. Run the tool
```bash
python app.py --text "Your English text here"
```

Use `--reverse` to translate from Lojban to English:

```bash
python app.py --text "coi" --reverse
```

Or translate from a file:
```bash
python app.py --file input.txt --save output.txt
```

---

### 💡 Example

```bash
python app.py --text "Cats are small mammals"
```

Output:
```
Lojban Translation:
u'i lo mlatu cmalu mabru cu zasti
```

---

## 📂 Project Files

- `app.py` – Main CLI script
- `valsi_glosswords.json` – Glossword-to-Lojban dictionary (required)

---

## ⚙️ Features

- ✅ Sentence splitting
- ✅ Lemmatization (handles plurals like "cats")
- ✅ Synonym fallback
- ✅ Number-to-Lojban digit conversion
- ✅ Verbose mode for debugging translations
- ✅ File input/output support
- ✅ Reverse mode (Lojban → English)
- ✅ Multi-word gloss detection

---

## 🧠 Notes

- Common English glue words like "is", "the", and "a" are ignored automatically.
- Translations follow a basic `lo ... cu ...` Lojban bridi structure.
- Outputs are **Lojban-ish** (aka *Lojbish*) and use valid roots, but aren't guaranteed to be grammatically perfect.
- Great for Lojban learners, conlangers, AI language tinkerers, and fans of logical languages.

---

## 🌱 Future Features
- Grammar-aware parsing with tools like `camxes` or `jbofihe`
- Attitudinal customization (`--attitude`) for expressive tone
