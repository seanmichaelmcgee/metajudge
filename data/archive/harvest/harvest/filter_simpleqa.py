"""
Filter SimpleQA dataset to produce calibration candidates for exact-string-match grading.
"""

import csv
import ast
import json
import re
from collections import Counter


# ── helpers ────────────────────────────────────────────────────────────────────

def approx_tokens(s: str) -> int:
    return len(s.strip().split())

def has_punctuation_dependency(answer: str) -> bool:
    """Flags answers where punctuation is load-bearing (e.g., abbrev., Jr., etc.)"""
    # Periods mid-word (e.g., "U.S.A.", "Jr.", "St.")
    if re.search(r'\b[A-Za-z]+\.[A-Za-z]', answer):
        return True
    # Trailing period (not numeric sentence-end)
    if answer.strip().endswith('.') and not re.match(r'^\d', answer.strip()):
        return True
    # Comma-separated list
    if ',' in answer:
        return True
    # Semicolon
    if ';' in answer:
        return True
    return False

def has_unit(answer: str) -> bool:
    """Flags answers that include measurement units."""
    unit_pattern = r'\b(km|mi|m|cm|mm|kg|lb|lbs|g|mg|L|ml|°|degrees?|percent|%|mph|kph|ft|feet|inch|inches|acres?|hectares?)\b'
    return bool(re.search(unit_pattern, answer, re.IGNORECASE))

def is_multi_part(answer: str) -> bool:
    """Flags answers with conjunctions suggesting multi-part structure."""
    # "X and Y", "X & Y"
    if re.search(r'\band\b|\b&\b', answer, re.IGNORECASE):
        # Allow if single person name with "and" unlikely — check token count
        if approx_tokens(answer) > 3:
            return True
    return False

def has_synonym_risk(answer: str) -> bool:
    """Flags known synonym pairs that could create ambiguity."""
    risky = [
        (r'\bgrey\b', r'\bgray\b'),
        (r'\bcolour\b', r'\bcolor\b'),
        (r'\bcentre\b', r'\bcenter\b'),
        (r'\banalyse\b', r'\banalyze\b'),
    ]
    low = answer.lower()
    for a, b in risky:
        if re.search(a, low) or re.search(b, low):
            return True
    return False

# Time-sensitive keyword patterns
TIME_SENSITIVE_PATTERNS = [
    r'\bcurrent(ly)?\b', r'\bpresident\b', r'\bprime minister\b', r'\bCEO\b',
    r'\bchairman\b', r'\bchairperson\b', r'\bgovernor\b', r'\bmayor\b',
    r'\bminister\b', r'\bleader\b', r'\bhead of\b', r'\brecent\b',
    r'\blatest\b', r'\btoday\b', r'\bnow\b', r'\bcurrently\b',
    r'\bthis year\b', r'\blast year\b', r'\bthis month\b',
    r'\b202[3-9]\b', r'\b203\d\b',  # recent years
    r'\bworld record\b',  # records change
    r'\brichest\b', r'\bpoorest\b', r'\bbiggest\b', r'\blargest\b',  # superlatives change
    r'\bmost popular\b', r'\bbest-selling\b',
]

def is_time_sensitive(question: str) -> bool:
    low = question.lower()
    for pat in TIME_SENSITIVE_PATTERNS:
        if re.search(pat, low, re.IGNORECASE):
            return True
    return False

def has_multi_form_risk(answer: str) -> bool:
    """Flags answers that are well-known by multiple names."""
    multi_form = [
        # Famous mountains / places
        'everest', 'sagarmatha', 'chomolungma',
        # Common dual-name entities
        'myanmar', 'burma', 'peking', 'beijing', 'bombay', 'mumbai',
        'calcutta', 'kolkata', 'madras', 'chennai', 'saigon',
        # Currency symbols
        'usd', 'eur', 'gbp', 'dollar', 'euro', 'pound',
    ]
    low = answer.lower()
    for term in multi_form:
        if term in low:
            return True
    return False

# Answer type → item_family mapping
ANSWER_TYPE_TO_FAMILY = {
    'Date': 'factual_recall',
    'Number': 'numeric',
    'Person': 'factual_recall',
    'Place': 'geography',
    'Other': 'factual_recall',
}

TOPIC_TO_FAMILY = {
    'Science and technology': 'science',
    'Geography': 'geography',
    'History': 'history',
    'Music': 'factual_recall',
    'Art': 'factual_recall',
    'Sports': 'factual_recall',
    'Politics': 'history',
    'TV shows': 'factual_recall',
    'Video games': 'factual_recall',
    'Other': 'factual_recall',
    'Language': 'language',
}

def get_item_family(topic: str, answer_type: str, question: str, answer: str) -> str:
    q_low = question.lower()
    a_low = answer.lower()
    
    # Override by content
    if any(w in q_low for w in ['country', 'city', 'capital', 'continent', 'river', 'mountain', 'ocean', 'lake', 'island', 'coast', 'region', 'province', 'state', 'born in', 'located in']):
        return 'geography'
    if answer_type == 'Number' or re.match(r'^\d+$', answer.strip()):
        return 'numeric'
    if any(w in q_low for w in ['discovered', 'invented', 'element', 'atomic', 'chemical', 'species', 'genus', 'formula', 'physics', 'chemistry', 'biology', 'planet', 'star', 'orbit', 'wavelength']):
        return 'science'
    if any(w in q_low for w in ['war', 'battle', 'treaty', 'revolution', 'dynasty', 'empire', 'founded', 'established', 'century', 'ancient', 'medieval', 'renaissance', 'colonial']):
        return 'history'
    if any(w in q_low for w in ['word', 'language', 'letter', 'alphabet', 'grammar', 'etymology', 'latin', 'greek', 'prefix', 'suffix', 'syllable', 'phoneme']):
        return 'language'
    
    return TOPIC_TO_FAMILY.get(topic, 'factual_recall')

def estimate_difficulty(question: str, answer: str, topic: str, answer_type: str) -> str:
    """Heuristic difficulty based on question type and answer obscurity."""
    q_low = question.lower()
    a_low = answer.lower()
    
    # Very common knowledge → easy
    easy_signals = [
        r'\bwhat (is|are) the (capital|currency|largest)\b',
        r'\bhow many (planets|continents|oceans)\b',
        r'\bwhich (country|planet|element)\b',
    ]
    for pat in easy_signals:
        if re.search(pat, q_low):
            return 'easy'
    
    # Specific person/award → hard
    hard_signals = [
        r'\baward\b', r'\bprize\b', r'\bmedal\b', r'\bhonor\b',
        r'\bwon the\b.*\bin \d{4}\b',
        r'\bfirst .* to\b',
        r'\bwho (was|is) the .* of\b',
    ]
    for pat in hard_signals:
        if re.search(pat, q_low):
            return 'hard'
    
    # Date answers — medium unless very famous event
    if answer_type == 'Date':
        famous_date_patterns = [
            r'\bmoon landing\b', r'\bwwi\b', r'\bww2\b', r'\bwwii\b',
            r'\bworld war\b', r'\bindependence\b', r'\bborn\b.*\beinstein\b',
        ]
        for p in famous_date_patterns:
            if re.search(p, q_low):
                return 'easy'
        return 'medium'
    
    # Numbers
    if answer_type == 'Number':
        return 'medium'
    
    # Named person (most are medium/hard)
    if answer_type == 'Person':
        return 'hard'
    
    # Place
    if answer_type == 'Place':
        # Common capitals etc.
        common_places = ['paris', 'london', 'rome', 'berlin', 'tokyo', 'washington', 'beijing', 'moscow']
        if a_low.strip() in common_places:
            return 'easy'
        return 'medium'
    
    return 'medium'

def canonicalize(answer: str) -> str:
    """Lowercase, strip, remove trailing period."""
    s = answer.strip().lower()
    # Remove trailing period if not a decimal number
    if s.endswith('.') and not re.match(r'^\d+\.$', s):
        s = s[:-1]
    return s

def build_aliases(answer: str, canonical: str) -> list:
    """Build a list of accepted alias forms for the answer."""
    aliases = []
    
    # Always include original stripped form if different from canonical
    orig_stripped = answer.strip()
    if orig_stripped.lower() != canonical:
        aliases.append(orig_stripped)
    
    # Numeric: if answer is a year, add common forms
    if re.match(r'^\d{4}$', canonical):
        # No aliases needed for bare years
        pass
    
    # If answer is a number with comma separators
    if re.match(r'^\d{1,3}(,\d{3})+$', canonical):
        aliases.append(re.sub(r',', '', canonical))  # no commas form
    
    # Bare number without commas
    if re.match(r'^\d+$', canonical):
        # add comma form for large numbers
        n = int(canonical)
        if n >= 1000:
            aliases.append(f"{n:,}")
    
    return list(set(aliases))

def survival_note(question: str, answer: str, topic: str, answer_type: str) -> str:
    """Generate a brief note explaining why this item survives filtering."""
    parts = []
    
    tok = approx_tokens(answer)
    parts.append(f"{tok}-token answer")
    
    if answer_type == 'Number' or re.match(r'^\d+$', answer.strip()):
        parts.append("numeric → digit form unambiguous")
    elif answer_type == 'Date':
        parts.append("date answer → single canonical form")
    elif answer_type == 'Person':
        parts.append("unique named person")
    elif answer_type == 'Place':
        parts.append("unique place name")
    
    if topic:
        parts.append(f"topic: {topic}")
    
    return "; ".join(parts)


# ── MAIN FILTER ────────────────────────────────────────────────────────────────

def main():
    rows = []
    with open('/home/user/workspace/metajudge-agi/data/harvest/simple_qa_test_set.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                meta = ast.literal_eval(row['metadata'])
                row['_topic'] = meta.get('topic', '')
                row['_answer_type'] = meta.get('answer_type', '')
            except:
                row['_topic'] = ''
                row['_answer_type'] = ''
            rows.append(row)

    print(f"Loaded {len(rows)} rows")

    rejected_reasons = Counter()
    candidates = []

    for row in rows:
        question = row['problem'].strip()
        answer = row['answer'].strip()
        topic = row['_topic']
        answer_type = row['_answer_type']

        # ── FILTER 1: Token length 1-5
        tok = approx_tokens(answer)
        if tok > 5:
            rejected_reasons['too_long_answer'] += 1
            continue

        # ── FILTER 2: No punctuation-dependent answers
        if has_punctuation_dependency(answer):
            rejected_reasons['punctuation_dependent'] += 1
            continue

        # ── FILTER 3: No units
        if has_unit(answer):
            rejected_reasons['unit_in_answer'] += 1
            continue

        # ── FILTER 4: No multi-part answers
        if is_multi_part(answer):
            rejected_reasons['multi_part'] += 1
            continue

        # ── FILTER 5: No synonym ambiguity
        if has_synonym_risk(answer):
            rejected_reasons['synonym_risk'] += 1
            continue

        # ── FILTER 6: No time-sensitive questions
        if is_time_sensitive(question):
            rejected_reasons['time_sensitive'] += 1
            continue

        # ── FILTER 7: No multi-form name risk
        if has_multi_form_risk(answer):
            rejected_reasons['multi_form_name'] += 1
            continue

        # ── FILTER 8: Exclude politics (too many current-events / leader questions)
        # Keep history but skip pure politics
        if topic == 'Politics':
            # Only keep if answer_type is Date or Number (more stable)
            if answer_type not in ('Date', 'Number'):
                rejected_reasons['politics_non_date'] += 1
                continue

        # ── FILTER 9: Skip answers that are purely abbreviations (ambiguous rendering)
        if re.match(r'^[A-Z]{2,6}$', answer.strip()):
            rejected_reasons['abbreviation'] += 1
            continue

        # ── FILTER 10: Skip answers ending with ordinal suffixes like "1st", "2nd" — potential rendering issue
        # Actually keep these; they're unambiguous numerics
        
        # ── FILTER 11: No "None" or empty answers
        if not answer or answer.lower() in ('none', 'n/a', 'unknown', 'various'):
            rejected_reasons['empty_or_none'] += 1
            continue

        # ── BUILD CANDIDATE ────────────────────────────────────────────────────
        canonical = canonicalize(answer)
        aliases = build_aliases(answer, canonical)
        item_family = get_item_family(topic, answer_type, question, answer)
        difficulty = estimate_difficulty(question, answer, topic, answer_type)
        note = survival_note(question, answer, topic, answer_type)

        candidates.append({
            "prompt": question,
            "gold_answer": canonical,
            "difficulty": difficulty,
            "item_family": item_family,
            "source": "simpleqa",
            "aliases": aliases,
            "note": note,
            "_raw_answer": answer,
            "_topic": topic,
            "_answer_type": answer_type,
        })

    print(f"\nCandidates after filtering: {len(candidates)}")
    print(f"\nRejection reasons:")
    for reason, count in rejected_reasons.most_common():
        print(f"  {reason}: {count}")

    # ── DIVERSITY SAMPLING ─────────────────────────────────────────────────────
    # We have many candidates. Sample for diversity across item_family and difficulty.
    # Target: 100-150 with good coverage.
    
    from collections import defaultdict
    import random
    random.seed(42)

    # Group by family
    by_family = defaultdict(list)
    for c in candidates:
        by_family[c['item_family']].append(c)
    
    print(f"\nFamily distribution (pre-sample):")
    for fam, items in sorted(by_family.items()):
        print(f"  {fam}: {len(items)}")
    
    # Stratified sample: proportional, minimum 10 per family, cap at 30 per family
    # except factual_recall which gets more
    sampled = []
    family_targets = {
        'factual_recall': 40,
        'numeric': 20,
        'geography': 20,
        'science': 15,
        'history': 15,
        'language': 10,
    }
    
    for fam, target in family_targets.items():
        pool = by_family.get(fam, [])
        # Prefer items with 1-2 token answers (most unambiguous)
        pool_short = [c for c in pool if approx_tokens(c['gold_answer']) <= 2]
        pool_long = [c for c in pool if approx_tokens(c['gold_answer']) > 2]
        
        random.shuffle(pool_short)
        random.shuffle(pool_long)
        selected = (pool_short + pool_long)[:target]
        sampled.extend(selected)
        print(f"  Sampled {fam}: {len(selected)} (pool: {len(pool)})")
    
    print(f"\nTotal sampled: {len(sampled)}")

    # Remove internal fields before writing
    output = []
    for item in sampled:
        output.append({
            "prompt": item["prompt"],
            "gold_answer": item["gold_answer"],
            "difficulty": item["difficulty"],
            "item_family": item["item_family"],
            "source": item["source"],
            "aliases": item["aliases"],
            "note": item["note"],
        })

    # Write to file
    import os
    os.makedirs('/home/user/workspace/metajudge-agi/data/harvest', exist_ok=True)
    with open('/home/user/workspace/metajudge-agi/data/harvest/simpleqa_candidates.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(output)} candidates to simpleqa_candidates.json")

    # Print sample output
    print("\nSample candidates:")
    for item in output[:5]:
        print(json.dumps(item, indent=2))

    return output, candidates

if __name__ == '__main__':
    output, candidates = main()
