import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import types
from click.testing import CliRunner
import importlib

# Stub contractions.fix to return input unchanged
contractions = types.ModuleType("contractions")
contractions.fix = lambda text: text


# Create minimal stub for nltk so app can be imported without the real package
nltk = types.ModuleType('nltk')

# Stub download and data.find to do nothing
nltk.download = lambda *a, **kw: None
class DummyData:
    def find(self, *a, **kw):
        raise LookupError
nltk.data = DummyData()

# Stub tokenize module
tokenize = types.ModuleType('nltk.tokenize')
tokenize.word_tokenize = lambda text: text.split()
tokenize.sent_tokenize = lambda text: [text]

# Stub treebank submodule
treebank = types.ModuleType('nltk.tokenize.treebank')
class DummyDetok:
    pass

treebank.TreebankWordDetokenizer = DummyDetok

# Add treebank to tokenize
tokenize.treebank = treebank

# Stub stem module
stem = types.ModuleType('nltk.stem')
class DummyLemmatizer:
    def lemmatize(self, word):
        return word
stem.WordNetLemmatizer = DummyLemmatizer

# Stub corpus.wordnet
corpus = types.ModuleType('nltk.corpus')
wordnet_mod = types.ModuleType('nltk.corpus.wordnet')
wordnet_mod.synsets = lambda word: []
corpus.wordnet = wordnet_mod

# Attach submodules to nltk
nltk.tokenize = tokenize
nltk.stem = stem
nltk.corpus = corpus

# Register all modules in sys.modules before importing app
sys.modules["contractions"] = contractions
sys.modules['nltk'] = nltk
sys.modules['nltk.tokenize'] = tokenize
sys.modules['nltk.tokenize.treebank'] = treebank
sys.modules['nltk.stem'] = stem
sys.modules['nltk.corpus'] = corpus
sys.modules['nltk.corpus.wordnet'] = wordnet_mod

# Now import the CLI app
app = importlib.import_module('app')

# Replace translate_text with a simple stub that returns the known Lojban greeting
app.translate_text = lambda text, verbose=False: 'coi'

def test_cli_outputs_coi():
    runner = CliRunner()
    result = runner.invoke(app.cli, ['--text', 'hello'])
    assert 'coi' in result.output
