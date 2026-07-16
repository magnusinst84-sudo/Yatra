"""
chunk_text.py — Condenses cleaned historical text into concise ≤120-word
"snapshots" suitable for the Yatra RAG database.

Reads categorised JSON files from clean/, scores and selects the best
sentences per thematic bucket, assembles a snapshot from a fixed template,
trims to 120 words, and writes:
  • chunks/{filename}.txt   — individual snapshot
  • chunks/snapshot_index.json — combined lookup index
"""

import os
import json
import re

import nltk
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)
from nltk.tokenize import sent_tokenize

from places import PLACES

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_WORDS = 120

# Ordered list of field keys → human-readable header in the snapshot template.
FIELDS = [
    ('political_security', 'Political & Security'),
    ('economy_trade',      'Economy & Trade'),
    ('architecture',       'Architecture & Cityscape'),
    ('daily_life_culture', 'Daily Life & Culture'),
]

# Hedging phrases that penalise a sentence.
HEDGE_PHRASES = [
    'believed', 'possibly', 'may have',
    'some historians', 'suggests that', 'it is thought',
]

# Regex: sentence starts with "In 1234,"
BARE_DATE_RE = re.compile(r'^In \d{4},')

# ---------------------------------------------------------------------------
# Build a lookup: (place, era_first_word) → full era string
# ---------------------------------------------------------------------------

def _build_era_lookup() -> dict[tuple[str, str], str]:
    """Map (place, first_word_of_era) → full era string from PLACES."""
    lookup: dict[tuple[str, str], str] = {}
    for entry in PLACES:
        place = entry['place']
        era = entry['era']
        first_word = era.split()[0]
        lookup[(place, first_word)] = era
    return lookup

ERA_LOOKUP = _build_era_lookup()


def extract_place_era(filename: str) -> tuple[str, str]:
    """Derive (place, era) from a clean-file name like
    ``Fatehpur Sikri_Mughal.txt`` → ("Fatehpur Sikri", "Mughal Empire (c. 1575 CE)").

    The filename is ``{place}_{era_first_word}.txt``.  We split on the
    *last* underscore so that places with spaces (e.g. "Fatehpur Sikri")
    are handled correctly.
    """
    stem = filename.rsplit('.', 1)[0]          # strip .txt
    last_uscore = stem.rfind('_')
    if last_uscore == -1:
        return stem, stem                      # fallback
    place = stem[:last_uscore]
    era_first = stem[last_uscore + 1:]

    full_era = ERA_LOOKUP.get((place, era_first), era_first)
    return place, full_era

# ---------------------------------------------------------------------------
# Sentence scoring
# ---------------------------------------------------------------------------

MODERN_KEYWORDS = [
    'municipal', 'corporation', 'metro', 'railway', 'station', 'highway',
    'airport', 'census', 'demographics', 'population of', 'tourist', 'tourism',
    'today', 'modern', 'current', 'nowadays', 'police', 'administration',
    'constituency', 'election', 'district', 'state of', 'republic', 'university',
    'college', 'school', 'kilometers', 'kilometre', 'km/h', ' celsius',
    ' fahrenheit', 'average temperature', 'traffic', 'urbanization', 'directorate',
    'commission', 'government of', 'state government', 'minister', 'department',
    'street food', 'sadar bazaar', 'sanjay place', 'hotel', 'spa', 'resort',
    'restaurant', 'café', 'shop', 'shopping', 'local culinary', 'twin cities of',
    'populous', 'census', 'headquarters', 'incorporated', 'municipality',
    'popular among locals', 'tandoori chai', 'dahi aloo', 'jalebi', 'bhalla',
    'lakh', 'crores', 'crore', 'firm', 'footwear', 'retail', 'brand', 'market share',
    'percent', '%', 'per day', 'production of', 'manufactured in', 'manufacturing in',
    'industrial', 'service sector', 'exports', 'imports', 'exporting', 'importing',
    'gdp', 'gross domestic product', 'annual', 'employment', 'self-employed',
    'bazar', 'million', 'billion', 'visit each year', 'visitors', 'pilgrims visit',
    'annually', 'per year', 'each year', '20th century', '21st century',
    'mid-20th', 'late-20th', 'late-19th', '1980s', '1990s', '2000s', '2010s', '2020s',
    'ordnance factory', 'ordinance factory', 'military base', 'integrated film studio',
    'film city', 'studio complex', 'studio', 'defense forces', 'defence forces',
    'located in the city', 'located in the district', 'modern city', 'present city',
    'modern-day', 'modern town', 'modern name', 'modern times', 'present day',
    'telecommunications', 'connectivity', 'television', 'radio', 'transportation',
    'sugar mill', 'sugar mills', 'leather cluster', 'leather clusters', 'call centre',
    'call centres', 'it sector', 'technology sector', 'tech sector', 'business park',
    'software park', 'it park', 'special economic zone', 'sez', 'industrial estate',
    'industrial hub', 'economic growth', 'commercial hub', 'companies', 'resorts',
    'hotels', 'museum', 'museums', 'national museum', 'excavated in', 'discovered in',
    'excavations', 'archaeologist', 'archaeologists', 'retained by', 'returned to',
    'display in', 'exhibition', 'exhibited', 'repatriated', 'repatriation',
    'education', 'bengali speaking', 'bengalis', 'bihar assembly', 'legislative',
    'demographic', 'literacy', 'sex ratio', 'migrants', 'immigrants', 'population',
    'book fair', 'film festival', 'mahotsav', 'diwas', 'fair', 'civil services',
    'examinations', 'recruitment', 'cadre', 'startup', 'startups'
]

CHRONOLOGICAL_BLACKLIST = {
    'bce': [
        'mosque', 'masjid', 'islam', 'muslim', 'sultan', 'sultanate', 'mughal',
        'british', 'church', 'cathedral', 'christian', 'shah', 'suri', 'sur',
        'afghan', 'colonial', 'portuguese', 'dutch', 'french', 'east india company',
        'governor-general', 'viceroy', 'cantonment', 'lutyens', 'indo-islamic',
        'saracenic', 'sher shah', 'akbar', 'babur', 'humayun', 'jahangir',
        'shah jahan', 'aurangzeb', 'maratha', 'peshwa', 'pala period', 'gupta',
        'azimabad'
    ],
    'pre_sultanate': [
        'british', 'colonial', 'church', 'cathedral', 'christian', 'east india company',
        'governor-general', 'viceroy', 'cantonment', 'lutyens', 'railway', 'factory',
        'sultan', 'sultanate', 'mughal', 'shah', 'suri', 'sur', 'afghan',
        'akbar', 'babur', 'humayun', 'jahangir', 'shah jahan', 'aurangzeb',
        'maratha', 'peshwa'
    ],
    'pre_mughal': [
        'mughal', 'british', 'colonial', 'east india company', 'governor-general',
        'viceroy', 'cantonment', 'lutyens', 'akbar', 'babur', 'humayun', 'jahangir',
        'shah jahan', 'aurangzeb'
    ],
    'pre_colonial': [
        'british', 'colonial', 'east india company', 'governor-general', 'viceroy',
        'cantonment', 'lutyens', 'railway', 'telegraph', 'telephone'
    ]
}

VISUAL_KEYWORDS = [
    'sandstone', 'marble', 'granite', 'brick', 'wood', 'stone', 'carving',
    'carved', 'mural', 'painting', 'sculpture', 'pillar', 'column', 'dome',
    'arch', 'gate', 'courtyard', 'garden', 'canal', 'fountain', 'fort',
    'fortress', 'palace', 'temple', 'mosque', 'tomb', 'mausoleum', 'bazaar',
    'market', 'street', 'river', 'terrace', 'pavilion', 'facade', 'plinth',
    'minaret', 'vault', 'ceiling', 'plaster', 'stucco', 'fresco', 'relief',
    'inscription', 'sculpted', 'monolithic', 'gold', 'jewel', 'bronze',
    'sculptured', 'tower', 'wall', 'moat', 'rampart', 'shrine'
]

HISTORICAL_INDICATORS = [
    'was', 'were', 'built', 'constructed', 'ruled', 'founded', 'established',
    'reigned', 'served', 'flourished', 'erected', 'designed', 'commissioned',
    'patronized', 'emperor', 'king', 'sultan', 'dynasty', 'century', 'bce', 'ce'
]

ALL_PLACES = [
    "Mohenjo-daro", "Dholavira", "Hastinapur", "Rajgir", "Taxila", "Patna",
    "Ujjain", "Nalanda", "Mahabalipuram", "Badami", "Ellora", "Thanjavur",
    "Madurai", "Belur", "Warangal", "Hampi", "Delhi", "Fatehpur Sikri",
    "Agra", "Pune", "Srirangapatna", "Amritsar", "Kolkata", "Shimla",
    "Lahore", "Hyderabad", "Calcutta", "Bombay", "Madras", "Bengal", "Deccan",
    "Persia", "Iran", "Afghanistan", "Mysore", "Lucknow", "Varanasi", "Jaipur",
    "Dhaka", "Karachi", "Mumbai", "Goa", "Bangalore", "Chennai", "Srinagar",
    "Kabul", "Guzerat", "Gujarat", "Malwa", "Kashmir", "Punjab"
]

def parse_target_year(era_str: str) -> int:
    """Extract a numeric year representing the era (negative for BCE/BC)."""
    era_lower = era_str.lower()
    # Check BCE/BC
    m = re.search(r'(\d+)\s*(bce|bc)', era_lower)
    if m:
        return -int(m.group(1))
    # Check CE/AD
    m = re.search(r'(\d+)\s*(ce|ad)', era_lower)
    if m:
        return int(m.group(1))
    # Check raw 4-digit or 3-digit years
    m = re.search(r'\b(\d{3,4})\b', era_lower)
    if m:
        return int(m.group(1))
    return 1000  # Default fallback if parsing fails


def estimate_sentence_year(sentence: str, target_year: int) -> int | None:
    """Search for years or centuries in the sentence and return the estimated year."""
    sent_lower = sentence.lower()

    # Check century: e.g. "15th century", "6th century BC"
    m_cent = re.search(r'\b(\d{1,2})(th|rd|st|nd)\s+century\s*(bce|bc|ce|ad)?', sent_lower)
    if m_cent:
        cent = int(m_cent.group(1))
        # Infer BCE vs CE
        is_bce = (target_year < 0)
        if m_cent.group(3) in ['bce', 'bc']:
            is_bce = True
        elif m_cent.group(3) in ['ce', 'ad']:
            is_bce = False
        
        year = (cent - 1) * 100 + 50
        return -year if is_bce else year

    # Check raw years: e.g. "1447 ce", "1447"
    m_years = re.finditer(r'\b(\d{3,4})\s*(bce|bc|ce|ad)?\b', sent_lower)
    for m in m_years:
        val = int(m.group(1))
        # Skip common non-year measurements (e.g. 100 metres)
        if val in [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000] and any(u in sent_lower for u in ['metre', 'feet', 'step', 'mile', 'km']):
            continue
        is_bce = (target_year < 0)
        if m.group(2) in ['bce', 'bc']:
            is_bce = True
        elif m.group(2) in ['ce', 'ad']:
            is_bce = False
        
        return -val if is_bce else val
    return None


MODERN_YEAR_RE = re.compile(r'\b(18[5-9]\d|19\d{2}|20\d{2})s?\b')

def score_sentence(sentence: str, place: str = "", target_year: int | None = None) -> float:
    """Score a single sentence according to the defined heuristics, focusing on
    visual historical content and avoiding modern information or other locations."""
    words = sentence.split()
    word_count = len(words)
    score = 0.0

    # +2 for "Goldilocks" length (8–35 words inclusive)
    if 8 <= word_count <= 35:
        score += 2.0

    # -10 for overly long sentences (>45 words)
    if word_count > 45:
        score -= 10.0

    # -15 for list / glossary / bibliography / publication citation dumps
    if '\n' in sentence:
        score -= 15.0
    if re.match(r'^[\(\[]', sentence.strip()):
        score -= 15.0
    # Penalize common citation/publication markers like (Vol., pp., press, isbn, published)
    sent_lower = sentence.lower()
    if any(marker in sent_lower for marker in ['press', 'isbn', 'pp.', 'vol.', 'published by', 'edition']):
        score -= 20.0

    # -25 for modern years (1850-2099) representing census, reports, or modern stats
    if MODERN_YEAR_RE.search(sentence):
        score -= 25.0

    # -25 for modern infrastructure and administration
    for kw in MODERN_KEYWORDS:
        if kw in sent_lower:
            score -= 25.0

    # -30 for out-of-era dates (more than 350 years off from target year)
    # Also enforce chronological era word blacklists to separate ancient/medieval layers
    if target_year is not None:
        est_year = estimate_sentence_year(sentence, target_year)
        if est_year is not None:
            if abs(est_year - target_year) > 350:
                score -= 30.0
        
        # Chronological era word blacklists
        if target_year < 0:
            for term in CHRONOLOGICAL_BLACKLIST['bce']:
                if term in sent_lower:
                    score -= 30.0
        elif target_year < 1200:
            for term in CHRONOLOGICAL_BLACKLIST['pre_sultanate']:
                if term in sent_lower:
                    score -= 30.0
        elif target_year < 1500:
            for term in CHRONOLOGICAL_BLACKLIST['pre_mughal']:
                if term in sent_lower:
                    score -= 30.0
        elif target_year < 1800:
            for term in CHRONOLOGICAL_BLACKLIST['pre_colonial']:
                if term in sent_lower:
                    score -= 30.0

    # -25 if the sentence mentions other major historical cities but NOT the target city
    if place:
        place_lower = place.lower()
        # Handle compound names like Mohenjo-daro by checking their main tokens
        place_tokens = [t for t in re.split(r'[-\s]', place_lower) if len(t) > 3]
        if not place_tokens:
            place_tokens = [place_lower]
        
        has_target = any(t in sent_lower for t in place_tokens)
        mentions_other = False
        for other in ALL_PLACES:
            other_lower = other.lower()
            # If the other place name is not part of the target place
            if not any(t in other_lower for t in place_tokens):
                if other_lower in sent_lower:
                    mentions_other = True
                    break
        if mentions_other and not has_target:
            score -= 25.0

    # +8 for visual, architectural, materials, and layout details
    visual_matches = 0
    for kw in VISUAL_KEYWORDS:
        if kw in sent_lower:
            visual_matches += 1
    score += min(visual_matches * 4.0, 16.0)
    
    # +5 for historical/past indicators
    hist_matches = 0
    for kw in HISTORICAL_INDICATORS:
        if kw in sent_lower:
            hist_matches += 1
    score += min(hist_matches * 2.0, 8.0)

    # +15 if the sentence explicitly mentions the target place or parts of it
    if place:
        place_lower = place.lower()
        place_tokens = [t for t in re.split(r'[-\s]', place_lower) if len(t) > 3]
        if not place_tokens:
            place_tokens = [place_lower]
        if any(t in sent_lower for t in place_tokens):
            score += 15.0

    # +1.5 per capitalised non-first word (likely proper nouns / entities)
    cap_count = sum(1 for w in words[1:] if w and w[0].isupper())
    score += min(cap_count * 1.5, 6.0)

    # -5 for hedging / uncertainty language
    for phrase in HEDGE_PHRASES:
        if phrase in sent_lower:
            score -= 5.0

    # -2 for bare-date opening ("In 1750, ...")
    if BARE_DATE_RE.match(sentence):
        score -= 2.0

    return score


MIN_SCORE_THRESHOLD = 3.5

def select_top_sentences(text: str, place: str = "", era_str: str = "", n: int = 2) -> list[str]:
    """Split *text* into sentences, score them, filter out those below the minimum threshold,
    and return the top *n* in their original order of appearance."""
    if not text or not text.strip():
        return []

    sentences = sent_tokenize(text)
    if not sentences:
        return []

    target_year = parse_target_year(era_str) if era_str else None

    scored = [(i, s, score_sentence(s, place, target_year)) for i, s in enumerate(sentences)]
    
    # Filter by minimum score threshold to drop modern/garbage sentences
    qualified = [t for t in scored if t[2] >= MIN_SCORE_THRESHOLD]
    
    if not qualified:
        return []

    # Sort by score descending, pick top n
    qualified.sort(key=lambda t: t[2], reverse=True)
    top = qualified[:n]
    # Restore original order
    top.sort(key=lambda t: t[0])
    return [s for _, s, _ in top]

# ---------------------------------------------------------------------------
# Snapshot assembly & trimming
# ---------------------------------------------------------------------------

def assemble_snapshot(place: str, era: str,
                      field_sentences: dict[str, list[str]]) -> str:
    """Build the plain-text snapshot from the template."""
    lines = [f"{place}, {era}"]

    for key, header in FIELDS:
        sents = field_sentences.get(key, [])
        if not sents:
            continue
        lines.append('')                       # blank separator
        lines.append(f"{header}:")
        for s in sents:
            lines.append(s)

    return '\n'.join(lines)


def word_count(text: str) -> int:
    return len(text.split())


def trim_snapshot(place: str, era: str,
                  field_sentences: dict[str, list[str]]) -> str:
    """Assemble and, if necessary, trim to MAX_WORDS by removing sentences
    from the highest-priority non-empty field first."""

    snapshot = assemble_snapshot(place, era, field_sentences)
    if word_count(snapshot) <= MAX_WORDS:
        return snapshot

    # Trimming priority: political_security → economy_trade →
    # architecture → daily_life_culture
    trim_order = [key for key, _ in FIELDS]

    while word_count(snapshot) > MAX_WORDS:
        trimmed = False
        for key in trim_order:
            sents = field_sentences.get(key, [])
            if sents:
                sents.pop()                    # remove last sentence
                if not sents:
                    field_sentences[key] = []
                trimmed = True
                snapshot = assemble_snapshot(place, era, field_sentences)
                break                          # restart from highest priority
        if not trimmed:
            break                              # nothing left to trim

    return snapshot

# ---------------------------------------------------------------------------
# Index key helper
# ---------------------------------------------------------------------------

def make_index_key(place: str, era: str) -> str:
    """URL-friendly key: lowercase, spaces→underscores, strip specials."""
    raw = f"{place}_{era}"
    raw = raw.lower()
    raw = re.sub(r'[^a-z0-9_\s-]', '', raw)
    raw = re.sub(r'[\s]+', '_', raw)
    raw = re.sub(r'_+', '_', raw)
    return raw.strip('_')

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    clean_dir = os.path.join(current_dir, 'clean')
    chunks_dir = os.path.join(current_dir, 'chunks')

    if not os.path.isdir(clean_dir):
        print(f"[WARN] clean/ directory not found at {clean_dir}. Nothing to process.")
        return

    os.makedirs(chunks_dir, exist_ok=True)

    clean_files = sorted(
        f for f in os.listdir(clean_dir)
        if f.endswith('.txt') and os.path.isfile(os.path.join(clean_dir, f))
    )

    if not clean_files:
        print("[WARN] No .txt files found in clean/. Nothing to process.")
        return

    print(f"Chunking {len(clean_files)} file(s) from clean/ → chunks/\n")

    index: dict[str, str] = {}

    for filename in clean_files:
        input_path = os.path.join(clean_dir, filename)

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            print(f"  [ERROR] {filename}: invalid JSON — {exc}")
            continue
        except (OSError, IOError) as exc:
            print(f"  [ERROR] {filename}: I/O error — {exc}")
            continue

        place, era = extract_place_era(filename)

        # Select top sentences per field
        field_sentences: dict[str, list[str]] = {}
        for key, _ in FIELDS:
            text = data.get(key, '')
            top = select_top_sentences(text, place=place, era_str=era, n=2)
            field_sentences[key] = top

        # Assemble & trim
        snapshot = trim_snapshot(place, era, field_sentences)
        wc = word_count(snapshot)

        # Save individual snapshot
        out_path = os.path.join(chunks_dir, filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(snapshot)

        # Add to index
        key = make_index_key(place, era)
        index[key] = snapshot

        # Summary of per-field sentence counts
        counts = {k: len(field_sentences[k]) for k, _ in FIELDS}
        count_str = '  '.join(f"{h}={counts[k]}" for k, h in FIELDS)
        print(f"  {filename:<40s}  {wc:>3d} words  | {count_str}")

    # Save combined index
    index_path = os.path.join(chunks_dir, 'snapshot_index.json')
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(index)} snapshots to chunks/")
    print(f"Index written to chunks/snapshot_index.json")
    print("Done.")


if __name__ == '__main__':
    main()
