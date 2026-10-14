"""Detection patterns for count_interview.py, Spanish.

Copy this file, translate the lists, and pass it with --patterns to count a
transcript in another language. Nothing else in the counter is language-aware.

Every list is lowercased and matched without accents, so "por que", "por qué"
and "porque" all hit the same entry.
"""

LANGUAGE = "es"

# Asking why, in its direct form. Counted only inside questions, so the
# conjunction in "porque es asi" never counts. This is the form that invites
# the interviewee to justify instead of tell; it is reported on its own to see
# whether it goes DOWN while the anchors and the hows go up.
# "para que" is left out on purpose: without the accent it is also the
# conjunction ("para que encuentres..."), and the counter folds accents away.
WHY = [
    "por que",
    "a que se debe",
    "que te llevo a",
    "que hizo que",
]

# Asking for the how, the signal, or the meaning: another way of going deeper
# that does not ask for a justification.
HOW = [
    "como te das cuenta",
    "como te diste cuenta",
    "como lo sabes",
    "como lo supiste",
    "como es eso",
    "como fue",
    "como lo haces",
    "como lo hiciste",
    "que seria",
    "en que sentido",
    "contame mas",
    "conta mas",
    "me contas",
]

# Opening the door wider or asking for the other side.
CONTRAST = [
    "de bueno",
    "de malo",
    "algo mas",
    "que mas",
    "alguna otra",
    "otra cosa",
    "distinto",
    "diferente",
]

# Anchoring in a concrete episode instead of a generality. Both the feminine
# ("la ultima vez") and masculine/other forms ("el ultimo", "el otro dia") have
# to be here: an interviewee answers "el ultimo reclamo" as often as "la ultima
# vez", and the masculine form was missing entirely.
CONCRETE = [
    "la ultima vez",
    "la ultima",
    "el ultimo",
    "la primera vez",
    "contame cuando",
    "contame de una vez",
    "acordate de",
    "un ejemplo",
    "un caso concreto",
    "que paso ese dia",
    "pensando en la ultima",
    "el otro dia",
    "ayer",
    "la semana pasada",
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
