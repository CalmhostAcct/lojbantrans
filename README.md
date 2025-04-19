
# lojbantrans

**`lojbantrans`** is a Python-based proof-of-concept command-line tool for translating English text into Lojban using glosswords.

---

## 🔧 How to Use

1. **Install dependencies** from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the tool**:
   ```bash
   python app.py --text "Your English text here"
   ```

---

### 💡 Example

```bash
python app.py --text "Hello World"
```

Output:
```
Lojban Translation:
u'i lo ... cu ...
```

---

## 📁 Files

- `app.py` – main CLI script
- `valsi_glosswords.json` – glossword-to-Lojban dictionary (required)

---

## 🧠 Notes

- Common English glue words like "is", "the", "a" are ignored automatically.
- The output is Lojban-ish (aka Lojbish) using valid Lojban roots, but may not always be grammatically perfect.
- A fun tool for Lojban learners, conlangers, or AI language hobbyists.

## Future Features
- Multi-word gloss detection
- Lojban-to-English reverse mode
- Grammar-aware output (using camxes or jbofihe)
