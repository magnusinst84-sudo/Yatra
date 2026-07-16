"""
clean_text.py — Cleans raw scraped Wikipedia sections and categorises them
into four thematic buckets for the Yatra RAG database.

Reads JSON files from raw/, strips citation markers, assigns each section
to the best-matching bucket based on title keywords, and writes one
cleaned JSON output per input file into clean/.
"""

import os
import json
import re

# ---------------------------------------------------------------------------
# Thematic bucket definitions
# ---------------------------------------------------------------------------

FIELD_KEYWORDS = {
    'political_security': [
        'government', 'military', 'war', 'rule', 'defence', 'politics',
        'empire', 'dynasty', 'battle', 'administration', 'king', 'sultan',
        'emperor', 'revolt', 'conflict', 'treaty', 'conquest',
    ],
    'economy_trade': [
        'trade', 'commerce', 'agriculture', 'guild', 'industry', 'market',
        'economy', 'revenue', 'tax', 'merchants', 'crafts', 'currency',
        'goods', 'production', 'resources',
    ],
    'architecture': [
        'architecture', 'buildings', 'city', 'monument', 'urban', 'fort',
        'temple', 'palace', 'structure', 'engineering', 'design',
        'construction', 'walls', 'gates', 'housing', 'infrastructure',
    ],
    'daily_life_culture': [
        'culture', 'religion', 'festival', 'cuisine', 'clothing',
        'daily life', 'society', 'art', 'literature', 'tradition',
        'customs', 'people', 'education', 'music', 'dance', 'rituals',
        'family',
    ],
}

# Priority order (highest → lowest) used as a tiebreaker when two buckets
# have the same keyword-match count.
BUCKET_PRIORITY = [
    'political_security',
    'economy_trade',
    'architecture',
    'daily_life_culture',
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Matches any bracketed citation / note marker, e.g.
#   [12]  [34, 35]  [citation needed]  [note 1]  [a]  [nb 2]
CITATION_RE = re.compile(r'\[[^\]]*?\]')


def strip_citations(text: str) -> str:
    """Remove all square-bracket citation markers from *text*."""
    return CITATION_RE.sub('', text)


BLACKLISTED_TITLE_KEYWORDS = [
    'modern', 'post independence', 'demographics', 'police', 'administration',
    'politics', 'utilities', 'metro', 'air', 'rail', 'road', 'development',
    'university', 'college', 'school', 'media', 'movie', 'film', 'sister city',
    'sister cities', 'see also', 'further reading', 'external link', 'source',
    'reference', 'bibliography', 'geography', 'climate', 'environment', 'tourism',
    'tourist', 'transport', 'healthcare', 'sports', 'demography', 'utility'
]

def classify_section(title: str) -> str | None:
    """Return the best-matching bucket name for *title*, or ``None``
    if no keywords match at all or if the title contains blacklisted terms."""

    title_lower = title.lower()
    
    # Skip any blacklisted sections (modern/irrelevant topics)
    for black_kw in BLACKLISTED_TITLE_KEYWORDS:
        if black_kw in title_lower:
            return None

    best_bucket = None
    best_count = 0

    for bucket in BUCKET_PRIORITY:
        keywords = FIELD_KEYWORDS[bucket]
        count = sum(1 for kw in keywords if kw in title_lower)
        if count > best_count:
            best_count = count
            best_bucket = bucket
        # Equal counts: BUCKET_PRIORITY iteration order guarantees
        # the higher-priority bucket wins (it was encountered first).

    return best_bucket  # None when best_count stayed at 0


def process_file(input_path: str, output_path: str) -> dict:
    """Read a raw JSON file, clean + classify its sections, and write
    the bucketed output. Returns a summary dict for logging."""

    with open(input_path, 'r', encoding='utf-8') as f:
        sections = json.load(f)

    # Initialise empty buckets
    buckets: dict[str, list[str]] = {b: [] for b in BUCKET_PRIORITY}

    total_sections = len(sections)
    kept = 0
    dropped = 0

    for section in sections:
        title = section.get('title', '')
        text = section.get('text', '')

        # Clean citation markers from text
        cleaned_text = strip_citations(text).strip()

        if not cleaned_text:
            dropped += 1
            continue

        bucket = classify_section(title)

        if bucket is None:
            dropped += 1
            continue

        buckets[bucket].append(cleaned_text)
        kept += 1

    # Concatenate each bucket's sections into a single string
    output = {b: '\n\n'.join(texts) for b, texts in buckets.items()}

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return {
        'total': total_sections,
        'kept': kept,
        'dropped': dropped,
        'per_bucket': {b: len(texts) for b, texts in buckets.items()},
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(current_dir, 'raw')
    clean_dir = os.path.join(current_dir, 'clean')

    # Ensure raw/ exists
    if not os.path.isdir(raw_dir):
        print(f"[WARN] raw/ directory not found at {raw_dir}. Nothing to process.")
        return

    # Ensure clean/ exists
    os.makedirs(clean_dir, exist_ok=True)

    # Collect all .txt files (they contain JSON despite the extension)
    raw_files = sorted(
        f for f in os.listdir(raw_dir)
        if f.endswith('.txt') and os.path.isfile(os.path.join(raw_dir, f))
    )

    if not raw_files:
        print("[WARN] No .txt files found in raw/. Nothing to process.")
        return

    print(f"Processing {len(raw_files)} file(s) from raw/ → clean/\n")

    for filename in raw_files:
        input_path = os.path.join(raw_dir, filename)
        output_path = os.path.join(clean_dir, filename)

        try:
            stats = process_file(input_path, output_path)
        except json.JSONDecodeError as exc:
            print(f"  [ERROR] {filename}: invalid JSON — {exc}")
            continue
        except (OSError, IOError) as exc:
            print(f"  [ERROR] {filename}: I/O error — {exc}")
            continue

        bucket_summary = '  '.join(
            f"{b}={stats['per_bucket'][b]}"
            for b in BUCKET_PRIORITY
        )
        print(
            f"  {filename:<40s}  "
            f"total={stats['total']:>3d}  "
            f"kept={stats['kept']:>3d}  "
            f"dropped={stats['dropped']:>3d}  "
            f"| {bucket_summary}"
        )

    print("\nDone.")


if __name__ == '__main__':
    main()
