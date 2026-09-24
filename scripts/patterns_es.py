"""Detection patterns for count_interview.py, Spanish.

Copy this file, translate the lists, and pass it with --patterns to count a
transcript in another language. Nothing else in the counter is language-aware.

Every list is lowercased and matched without accents, so "por que", "por qué"
and "porque" all hit the same entry.
"""

LANGUAGE = "es"

# Asking why. Anything that pushes for the reason behind an answer.
WHY = [
    "por que",
    "porque",
    "a que se debe",
    "contame mas",
    "conta mas",
    "como es eso",
    "en que sentido",
    "que te llevo a",
    "que hizo que",
]

# Anchoring in a concrete episode instead of a generality.
CONCRETE = [
    "la ultima vez",
    "la primera vez",
    "contame cuando",
    "contame de una vez",
    "acordate de",
    "un ejemplo",
    "un caso concreto",
    "que paso ese dia",
    "pensando en la ultima",
]

# A closing recap: the interviewer giving back what they understood.
RECAP = [
    "lo que entiendo",
    "lo que entendi",
    "te devuelvo",
    "resumiendo",
    "a ver si entendi",
    "dejame ver si",
    "entonces lo que me contas",
    "si tuviera que resumir",
]

# Closed questions: a question opening with a conjugated verb or auxiliary.
# Approximate by design, and the report says so.
CLOSED_OPENERS = [
    "te gusta", "te gustaria", "usarias", "pagarias", "comprarias",
    "tenes", "tenias", "podes", "podrias", "sabes", "sabias",
    "es ", "era ", "fue ", "esta ", "estaba ",
    "hay ", "habia ", "queres", "querrias", "crees", "creas",
    "usas", "usabas", "hiciste", "haces", "harias",
    "viste", "conoces", "conocias", "te parece",
]

# Leading questions. NOT counted: listed so the Guide can look for them by hand.
# Detecting these by pattern produces false confidence, and the criterion is
# too important to report badly.
LEADING_HINTS = [
    "no te parece que",
    "verdad que",
    "seguramente",
    "obviamente",
    "te resolveria",
    "no seria mejor",
]
