#!/usr/bin/env python3
"""
Formatter agent — Canonicalize V2 candidates for MetaJudge expansion sprint.

Reads:  data/harvest/v2_raw_candidates.json (223 items)
        data/calibration.csv (existing 20-item pilot for dedup)
Writes: data/harvest/v2_canonicalized_candidates.json
        data/harvest/v2_alias_ledger.json
"""

import json
import re
import csv
import os
from typing import Any

BASE = "/home/user/workspace/metajudge"

# ---------------------------------------------------------------------------
# Load inputs
# ---------------------------------------------------------------------------

with open(f"{BASE}/data/harvest/v2_raw_candidates.json") as f:
    raw_candidates = json.load(f)

# Load pilot prompts for dedup checking
pilot_prompts = []
pilot_answers = []
with open(f"{BASE}/data/calibration.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        pilot_prompts.append(row["prompt"].strip().lower())
        pilot_answers.append((row["gold_answer"].strip().lower(), row.get("difficulty", "")))

print(f"Loaded {len(raw_candidates)} raw candidates, {len(pilot_prompts)} pilot items")

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def normalize_gold_answer(gold: str, answer_type: str) -> str:
    """Normalize gold answer per spec:
    - Lowercase everything
    - Strip leading/trailing whitespace
    - Remove trailing periods
    - Digits only for numeric (no commas, no units)
    - No articles (a, an, the) at the start
    """
    if gold is None:
        return ""
    g = gold.strip()
    
    # For numeric answers, strip all non-numeric except decimal point and minus
    if answer_type in ("integer", "decimal"):
        # Remove commas in numbers like 1,000
        g = g.replace(",", "")
        # Remove units: strip trailing non-numeric chars (km, mph, etc.)
        # But keep the numeric part
        g = re.sub(r'[^0-9.\-]', '', g)
        # Remove trailing period
        g = g.rstrip(".")
        return g
    
    # For all other types
    g = g.lower()
    # Remove trailing period
    g = g.rstrip(".")
    # Remove leading articles
    g = re.sub(r'^(the|a|an)\s+', '', g)
    # Strip whitespace
    g = g.strip()
    return g

def count_tokens(text: str) -> int:
    """Approximate token count by word split."""
    return len(text.strip().split())

def normalize_prompt(prompt: str, answer_type: str, gold_answer: str, raw_item: dict) -> tuple[str, str]:
    """
    Ensure prompt ends with proper forcing instruction.
    Returns (normalized_prompt, format_instruction_str).
    """
    p = prompt.strip()
    
    # Detect if prompt already ends with a forcing instruction
    # (pattern: "Answer with X only." or "Give X only." or "Answer X only.")
    forcing_pattern = re.compile(
        r'(Answer\s+(with\s+)?.*?\s+only\.?|Give\s+.*?\s+only\.?|Answer\s+yes\s+or\s+no\s+only\.?)\s*$',
        re.IGNORECASE
    )
    
    if forcing_pattern.search(p):
        # Already has forcing instruction; just ensure it ends with period
        if not p.endswith("."):
            p = p + "."
        fi = infer_format_instruction(p, answer_type, gold_answer)
        return p, fi
    
    # Need to add forcing instruction
    # Remove trailing punctuation first (but not if it's a question mark on the main question)
    if p.endswith(".") or p.endswith(":"):
        p = p.rstrip(".:")
    
    fi = infer_format_instruction("", answer_type, gold_answer)
    instruction = build_forcing_instruction(answer_type, gold_answer, raw_item)
    p = p + " " + instruction
    return p, fi

def infer_format_instruction(prompt: str, answer_type: str, gold_answer: str) -> str:
    """Infer the format_instruction string based on answer_type."""
    if answer_type in ("integer", "decimal"):
        return "digits_only"
    elif answer_type == "yes_no":
        return "yes_no"
    elif answer_type == "single_word":
        # Check for chemical symbol
        if gold_answer and re.match(r'^[A-Za-z]{1,3}$', gold_answer.strip()) and len(gold_answer.strip()) <= 3:
            return "symbol_only"
        if gold_answer and "/" in gold_answer:
            return "fraction_only"
        return "one_word_only"
    elif answer_type == "entity":
        # Infer from gold answer content
        if gold_answer:
            g = gold_answer.strip()
            # Check if it's a city name
            if any(kw in prompt.lower() for kw in ["capital", "city"]):
                return "city_name_only"
            # Country
            if any(kw in prompt.lower() for kw in ["country", "nation"]):
                return "country_name_only"
            # Planet
            if any(kw in prompt.lower() for kw in ["planet"]):
                return "planet_name_only"
            # Mountain
            if any(kw in prompt.lower() for kw in ["mountain"]):
                return "mountain_name_only"
            # Element
            if any(kw in prompt.lower() for kw in ["element"]):
                return "element_name_only"
            # Author / person
            if any(kw in prompt.lower() for kw in ["author", "wrote", "writer", "philosopher", "director", "inventor", "speaker"]):
                return "full_name_only"
            # Ocean
            if any(kw in prompt.lower() for kw in ["ocean"]):
                return "ocean_name_only"
            # Generic entity
            return "name_only"
        return "name_only"
    return "bare_value"

def build_forcing_instruction(answer_type: str, gold_answer: str, raw_item: dict) -> str:
    """Build a proper forcing instruction for the answer type."""
    prompt = raw_item.get("prompt", "").lower()
    
    if answer_type in ("integer", "decimal"):
        return "Answer with digits only."
    elif answer_type == "yes_no":
        return "Answer yes or no only."
    elif answer_type == "single_word":
        # Chemical symbol?
        if gold_answer and re.match(r'^[A-Za-z]{1,3}$', gold_answer.strip()) and "symbol" in prompt:
            return "Answer with the symbol only."
        if gold_answer and "/" in gold_answer:
            return "Answer as a fraction only."
        return "Answer with one word only."
    elif answer_type == "entity":
        if "capital" in prompt and "city" not in prompt:
            return "Answer with the city name only."
        if "city" in prompt:
            return "Answer with the city name only."
        if "country" in prompt or "nation" in prompt:
            return "Answer with the country name only."
        if "planet" in prompt:
            return "Answer with the planet name only."
        if "mountain" in prompt:
            return "Answer with the mountain name only."
        if "element" in prompt:
            return "Answer with the element name only."
        if "ocean" in prompt:
            return "Answer with the ocean name only."
        if "author" in prompt or "wrote" in prompt or "writer" in prompt:
            return "Answer with the author's name only."
        if "philosopher" in prompt:
            return "Answer with the philosopher's name only."
        if "director" in prompt:
            return "Answer with the director's name only."
        if "inventor" in prompt:
            return "Answer with the inventor's name only."
        if "speaker" in prompt:
            return "Answer with the speaker's full name only."
        if "currency" in prompt:
            return "Answer with the currency name only."
        if "language" in prompt:
            return "Answer with the language name only."
        if "organ" in prompt or "bone" in prompt:
            return "Answer with one word only."
        if "galaxy" in prompt:
            return "Answer with the name only."
        return "Answer with the name only."
    return "Answer with one word only."

def token_overlap(a: str, b: str) -> float:
    """Simple token overlap ratio for dedup check."""
    tokens_a = set(a.lower().split())
    tokens_b = set(b.lower().split())
    if not tokens_a or not tokens_b:
        return 0.0
    overlap = tokens_a & tokens_b
    return len(overlap) / max(len(tokens_a), len(tokens_b))

# Boilerplate tokens shared by all prompts — excluded from semantic dedup
BOILERPLATE_TOKENS = {
    "what", "is", "the", "a", "an", "of", "in", "to", "and", "with", "only",
    "answer", "digits", "number", "name", "give", "how", "many", "does",
    "have", "are", "there", "do", "did", "was", "were", "has", "had",
    "one", "no", "yes", "word", "city", "digit", "year", "only",
}

def semantic_dedup_tokens(prompt: str) -> set:
    """Extract only meaningful tokens for dedup (strip boilerplate)."""
    tokens = set(prompt.lower().split())
    cleaned = set()
    for t in tokens:
        t2 = t.strip("?.!,")
        if t2 and t2 not in BOILERPLATE_TOKENS and len(t2) > 2:
            cleaned.add(t2)
    return cleaned

def is_near_duplicate_of_pilot(prompt: str, gold_answer: str) -> bool:
    """Check if this item is semantically close to any pilot item.
    
    Uses content-bearing token overlap only — strips boilerplate like
    'Answer with digits only' which is shared by all numeric prompts.
    Threshold: >0.80 content overlap with min-token denominator.
    """
    p_tokens = semantic_dedup_tokens(prompt)
    if len(p_tokens) < 2:
        return False
    
    for pp in pilot_prompts:
        pp_tokens = semantic_dedup_tokens(pp)
        if not pp_tokens:
            continue
        overlap = p_tokens & pp_tokens
        # Use overlap / min-side for a stricter check
        ratio = len(overlap) / min(len(p_tokens), len(pp_tokens))
        if ratio > 0.80 and len(overlap) >= 3:
            return True
    return False

def build_aliases(canonical_answer: str, answer_type: str, gold_answer_raw: str, item: dict) -> tuple[list, list, str]:
    """
    Build accepted_aliases and rejected_near_misses for an item.
    Returns (accepted_aliases, rejected_near_misses, rationale).
    """
    c = canonical_answer
    accepted = [c]
    rejected = []
    rationale_parts = []

    if answer_type in ("integer", "decimal"):
        # Numeric equivalence
        rationale_parts.append("Numeric answer — accepted aliases include common decimal/integer equivalents.")
        
        # Try to parse
        try:
            val = float(c)
            is_int = (val == int(val))
            
            if is_int:
                int_val = int(val)
                # Integer with comma (not accepted but note)
                comma_form = f"{int_val:,}"
                if comma_form != str(int_val):
                    rejected.append(comma_form)
                    rationale_parts.append(f"Rejected '{comma_form}' (comma-formatted number — digits only required).")
                
                # Float form if it's an integer
                float_form = str(float(int_val))
                # e.g., "42.0"
                if float_form != c:
                    accepted.append(float_form)
                    rationale_parts.append(f"Accepted '{float_form}' (integer expressed as decimal).")
                
                # Word form for small numbers
                word_map = {
                    0:"zero",1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",
                    8:"eight",9:"nine",10:"ten",11:"eleven",12:"twelve",13:"thirteen",
                    14:"fourteen",15:"fifteen",16:"sixteen",17:"seventeen",18:"eighteen",
                    19:"nineteen",20:"twenty",21:"twenty-one",22:"twenty-two",23:"twenty-three",
                    24:"twenty-four",25:"twenty-five",26:"twenty-six",27:"twenty-seven",
                    28:"twenty-eight",29:"twenty-nine",30:"thirty",31:"thirty-one",
                    32:"thirty-two",33:"thirty-three",40:"forty",42:"forty-two",
                    45:"forty-five",50:"fifty",54:"fifty-four",56:"fifty-six",
                    63:"sixty-three",65:"sixty-five",72:"seventy-two",80:"eighty",
                    81:"eighty-one",88:"eighty-eight",90:"ninety",100:"one hundred",
                    101:"one hundred and one",118:"one hundred and eighteen",
                    206:"two hundred and six",
                }
                if int_val in word_map:
                    word = word_map[int_val]
                    # Accept word form for small numbers, reject for larger
                    if int_val <= 30:
                        accepted.append(word)
                        rationale_parts.append(f"Accepted word form '{word}' for small number {int_val}.")
                    else:
                        rejected.append(word)
                        rationale_parts.append(f"Rejected word form '{word}' — prompt requests digits only.")
                
                # With units (e.g., "65 cm") — rejected
                sample_units = ["km", "m", "cm", "mm", "kg", "g", "lb", "°C", "°F", "mph", "km/h", "%", "years", "days", "hours", "minutes", "seconds"]
                for unit in sample_units[:3]:
                    rejected.append(f"{int_val} {unit}")
                rejected_unit_note = f"Rejected forms with units (e.g., '{int_val} km') — digits only required."
                rationale_parts.append(rejected_unit_note)
                
            else:
                # Decimal
                # Leading zero variant: .05 vs 0.05
                if c.startswith("0."):
                    no_leading_zero = c[1:]  # ".05"
                    accepted.append(no_leading_zero)
                    rationale_parts.append(f"Accepted '{no_leading_zero}' (decimal without leading zero).")
                elif c.startswith("."):
                    with_zero = "0" + c  # "0.05"
                    accepted.append(with_zero)
                    rationale_parts.append(f"Accepted '{with_zero}' (decimal with leading zero).")
                
                # Percentage form
                try:
                    pct = val * 100
                    if pct == int(pct):
                        rejected.append(f"{int(pct)}%")
                        rationale_parts.append(f"Rejected '{int(pct)}%' — percentage form not accepted when prompt asks for decimal.")
                except:
                    pass
                    
        except (ValueError, TypeError):
            rationale_parts.append("Could not parse as numeric — no numeric aliases added.")
    
    elif answer_type == "yes_no":
        # Yes/no variants
        rationale_parts.append("Binary yes/no answer.")
        if c == "yes":
            accepted.extend(["yes", "y"])
            rejected.extend(["true", "correct", "affirmative", "1"])
            rationale_parts.append("Accepted 'y' as abbreviation for 'yes'. Rejected 'true'/'correct'/'1' — prompt specifies yes or no only.")
        elif c == "no":
            accepted.extend(["no", "n"])
            rejected.extend(["false", "incorrect", "0", "nope"])
            rationale_parts.append("Accepted 'n' as abbreviation for 'no'. Rejected 'false'/'incorrect'/'0' — prompt specifies yes or no only.")
        # Deduplicate accepted
        accepted = list(dict.fromkeys(accepted))
    
    elif answer_type == "entity":
        rationale_parts.append("Named entity answer — accepted aliases include common variants.")
        c_raw = gold_answer_raw  # original (pre-normalization) for entity aliases
        
        # Capitalized form
        if c != c_raw.lower():
            # Already normalized to lower; add title case
            title = c.title()
            if title != c and title not in accepted:
                accepted.append(title)
                rationale_parts.append(f"Accepted title-case form '{title}'.")
        
        # Handle specific multi-word entities
        prompt_lower = item.get("prompt", "").lower()
        note_lower = item.get("note", "").lower()
        
        # Hyphen variants
        if "-" in c:
            no_hyph = c.replace("-", " ")
            accepted.append(no_hyph)
            rationale_parts.append(f"Accepted hyphen-free form '{no_hyph}'.")
        elif " " in c:
            hyph = c.replace(" ", "-")
            # Only add if plausible
            if len(c.split()) == 2:
                rejected.append(hyph)
                rationale_parts.append(f"Rejected hyphenated form '{hyph}' — space form is canonical.")
        
        # Specific entity handling
        if c == "jupiter":
            rejected.append("saturn")
            rejected.append("neptune")
            rationale_parts.append("Rejected 'saturn'/'neptune' — common wrong answers.")
        elif c == "george orwell":
            accepted.append("orwell")
            accepted.append("eric arthur blair")
            rejected.append("george orwel")
            rationale_parts.append("Accepted 'orwell' (last name only) and birth name. Rejected common misspelling.")
        elif c == "vatican city":
            accepted.extend(["the vatican", "holy see", "vatican"])
            rationale_parts.append("Accepted 'the vatican', 'holy see', 'vatican' as common aliases.")
        elif c == "immanuel kant":
            accepted.append("kant")
            rejected.append("emmanuel kant")
            rationale_parts.append("Accepted 'kant' (surname only). Rejected alternate first-name spelling.")
        elif c == "alexander graham bell":
            accepted.append("bell")
            accepted.append("graham bell")
            rationale_parts.append("Accepted surname and partial name forms.")
        elif c == "canberra":
            rejected.append("sydney")
            rejected.append("melbourne")
            rationale_parts.append("Rejected 'sydney'/'melbourne' — common wrong answers.")
        elif c == "antarctic desert":
            accepted.extend(["antarctica", "antarctic", "antarctic polar desert", "the antarctic desert"])
            rationale_parts.append("Accepted common alternative phrasings for Antarctic Desert.")
        elif c == "mauna kea":
            accepted.append("maunakea")
            rejected.append("mount everest")
            rationale_parts.append("Accepted spelling variant 'maunakea'. Rejected 'mount everest' — common wrong answer.")
        elif c == "chimborazo":
            rejected.append("mount everest")
            rationale_parts.append("Rejected 'mount everest' — common wrong answer confusing height from sea level vs. from Earth's center.")
        elif c == "saturn":
            rejected.append("jupiter")
            rationale_parts.append("Rejected 'jupiter' — common wrong answer (most prominent rings, but Saturn has most known moons as of 2024).")
        elif c == "brazil":
            accepted.append("brasil")
            rationale_parts.append("Accepted 'brasil' — Portuguese/alternative spelling.")
        elif c == "wellington":
            rejected.append("auckland")
            rationale_parts.append("Rejected 'auckland' — common wrong answer (largest city, not capital).")
        elif c == "ottawa":
            rejected.append("toronto")
            rejected.append("montreal")
            rationale_parts.append("Rejected 'toronto'/'montreal' — common wrong answers.")
        elif c == "mercury":
            rejected.append("venus")
            rationale_parts.append("Rejected 'venus' — common wrong answer.")
        elif c == "nitrogen":
            rejected.append("oxygen")
            rationale_parts.append("Rejected 'oxygen' — common wrong answer (oxygen ~21%, nitrogen ~78%).")
        elif c == "hydrogen":
            rejected.append("helium")
            rationale_parts.append("Rejected 'helium' — common wrong answer for most abundant element in sun.")
        elif c == "atlantic":
            rejected.append("pacific")
            rationale_parts.append("Rejected 'pacific' — Pacific has lower average salinity than Atlantic.")
        elif c == "nintendo":
            rejected.append("atari")
            rejected.append("sony")
            rationale_parts.append("Rejected 'atari'/'sony' — common wrong answers.")
        elif c == "lithium":
            rejected.append("hydrogen")
            rationale_parts.append("Rejected 'hydrogen' — common wrong answer (hydrogen is first, lithium is first metal/third element).")
        elif c == "canada":
            rejected.append("russia")
            rejected.append("united states")
            rationale_parts.append("Rejected 'russia'/'united states' — Canada has most freshwater lakes by count.")
        elif c == "iron":
            accepted.append("fe")
            rationale_parts.append("Accepted 'fe' — chemical symbol is acceptable alternate.")
        elif c == "liver":
            rejected.append("heart")
            rejected.append("skin")
            rationale_parts.append("Rejected 'heart'/'skin' — common wrong answers (liver is largest internal organ; skin is largest overall but often excluded).")
        elif c == "femur":
            rejected.append("tibia")
            rationale_parts.append("Rejected 'tibia' — common wrong answer.")
        elif c == "lung":
            accepted.append("lungs")
            rationale_parts.append("Accepted plural 'lungs' as alias for 'lung'.")
        elif c == "arachnophobia":
            rejected.append("arachnophbia")
            rationale_parts.append("Rejected common misspelling 'arachnophbia'.")
        elif c == "equilateral":
            rejected.append("isoceles")
            rationale_parts.append("Rejected 'isoceles' — has only two equal sides.")
        elif c == "portuguese":
            accepted.append("portuguese language")
            rejected.append("spanish")
            rationale_parts.append("Accepted 'portuguese language'. Rejected 'spanish' — common wrong answer.")
        elif c == "milky way":
            accepted.extend(["the milky way", "milky way galaxy"])
            rationale_parts.append("Accepted 'the milky way' and 'milky way galaxy'.")
        elif c == "pound":
            accepted.extend(["pound sterling", "gbp"])
            rejected.append("euro")
            rationale_parts.append("Accepted 'pound sterling' and 'gbp'. Rejected 'euro' — UK uses pound.")
        elif c in ("nothing", "unspecified"):
            rationale_parts.append(f"Special sentinel value '{c}' — no aliases.")
        elif c == "moon landing":
            accepted.append("moon landing")
            rationale_parts.append("Fixed-form answer from constrained prompt.")
        elif c == "parchment":
            accepted.append("hemp")
            rationale_parts.append("Accepted 'hemp' — some sources note hemp parchment; parchment is canonical.")
        elif c == "provincetown":
            rejected.append("plymouth")
            rationale_parts.append("Rejected 'plymouth' — Pilgrims first landed at Provincetown, not Plymouth (common misconception).")
        elif c == "richard marquand":
            accepted.append("marquand")
            rationale_parts.append("Accepted surname only.")
        elif c == "marianne williamson":
            accepted.append("williamson")
            rationale_parts.append("Accepted surname only.")
        elif c == "yellow-green":
            accepted.extend(["yellow green", "yellowish green", "green-yellow"])
            rationale_parts.append("Accepted hyphen-free and directionally swapped forms.")
        elif c == "magic mirror on the wall":
            accepted.append("mirror mirror on the wall")
            rejected.append("who is the fairest of them all")
            rationale_parts.append("Accepted 'mirror mirror on the wall' (popular misquote that's also widely considered correct). Rejected the continuation of the phrase.")
        elif c == "arizona":
            accepted.append("arizona and hawaii")
            rejected.append("hawaii")
            rationale_parts.append("Note: Hawaii also doesn't observe DST but prompt likely asks for most-known answer. Arizona is canonical. Rejected Hawaii-only as incomplete.")
        elif c == "empty hand":
            accepted.extend(["empty hand", "empty-hand"])
            rationale_parts.append("Accepted hyphenated form.")
        elif c == "yen":
            accepted.append("japanese yen")
            rejected.append("yuan")
            rationale_parts.append("Accepted 'japanese yen'. Rejected 'yuan' — China's currency.")
        elif c == "ottawa":
            rejected.extend(["toronto", "montreal", "vancouver"])
        elif c == "1/4":
            accepted.extend(["one quarter", "one-quarter", "0.25", "25%"])
            rationale_parts.append("Accepted various forms: word, decimal, percentage.")
        
        # Deduplicate accepted
        accepted = list(dict.fromkeys(accepted))
    
    elif answer_type == "single_word":
        # Chemical symbols, formulas, etc.
        rationale_parts.append("Single-word or symbol answer.")
        c_raw_stripped = gold_answer_raw.strip()
        
        if c == "h2o":
            accepted.extend(["h₂o"])
            rejected.extend(["water", "H2O"])
            rationale_parts.append("Accepted Unicode subscript form. Rejected 'water' (word form) — formula requested.")
            # Actually H2O (capitalized) should be accepted since it's the chemical formula
            accepted.append("H2O")
            rationale_parts.append("Accepted uppercase 'H2O' — chemical formula canonically uppercase.")
        elif c == "na":
            accepted.append("Na")
            rejected.extend(["sodium", "natrium"])
            rationale_parts.append("Accepted 'Na' (capitalized symbol). Rejected full element name — symbol requested.")
        elif c == "k":
            accepted.append("K")
            rejected.extend(["potassium", "kalium"])
            rationale_parts.append("Accepted 'K' (capitalized symbol). Rejected full element name — symbol requested.")
        elif c == "fe":
            accepted.append("Fe")
            rejected.extend(["iron", "ferrum"])
            rationale_parts.append("Accepted 'Fe' (standard capitalization). Rejected full element name.")
        elif c == "arachnophobia":
            pass  # handled in entity section but might be single_word
        
        # Deduplicate
        accepted = list(dict.fromkeys(accepted))
    
    # Ensure canonical is always first and no duplicates
    if c not in accepted:
        accepted.insert(0, c)
    else:
        accepted.remove(c)
        accepted.insert(0, c)
    
    # Deduplicate rejected
    rejected = list(dict.fromkeys(rejected))
    # Remove from rejected anything that is also accepted
    rejected = [r for r in rejected if r not in accepted]
    
    rationale = " ".join(rationale_parts) if rationale_parts else "Standard alias coverage applied."
    return accepted, rejected, rationale

def check_format_gates(item: dict, normalized_prompt: str, gold_answer: str) -> list[str]:
    """
    Check format gates. Returns list of issues (empty = pass).
    """
    issues = []
    
    # Gate 1: Gold answer > 5 tokens
    token_count = count_tokens(gold_answer)
    if token_count > 5:
        issues.append(f"Gold answer has {token_count} tokens (>5 limit): '{gold_answer}'")
    
    # Gate 2: Prompt doesn't end with forcing instruction
    forcing_end = re.compile(
        r'(only\.?)\s*$',
        re.IGNORECASE
    )
    if not forcing_end.search(normalized_prompt):
        issues.append(f"Prompt does not end with a forcing instruction: '...{normalized_prompt[-60:]}'")
    
    # Gate 3: Answer has multiple natural forms that can't be collapsed
    # Check for ambiguous entity answers
    answer_type = item.get("answer_type", "")
    if answer_type == "entity":
        # Specific flagging for multi-natural-form answers
        multi_form_answers = {
            "moon landing": "Has constrained format in prompt",
            "magic mirror on the wall": "Popular misquote form also widely accepted",
            "arizona": "Hawaii also doesn't observe DST — Arizona is canonical but note ambiguity",
            "yellow-green": "Color has multiple equally natural forms (yellow-green vs green-yellow)",
            "parchment": "Some sources say hemp — minor ambiguity",
            "unspecified": "Sentinel value — special handling needed",
            "nothing": "Sentinel value — prompt constrains to this form",
        }
        ga_lower = gold_answer.lower()
        if ga_lower in multi_form_answers and "constrained" not in multi_form_answers[ga_lower]:
            issues.append(f"Multi-form answer risk: {multi_form_answers[ga_lower]}")
    
    # Gate 4: Time-sensitive items
    time_sensitive_keywords = [
        "current", "currently", "today", "latest", "recent", "now", "2024", "2025", "2026",
        "last year", "this year", "president", "prime minister", "ceo"
    ]
    prompt_lower = normalized_prompt.lower()
    note_lower = item.get("note", "").lower()
    
    for kw in time_sensitive_keywords:
        if kw in prompt_lower:
            # Jupiter moons as of 2024 is flagged
            if kw in ("2024", "2025", "2026"):
                issues.append(f"Potentially time-sensitive: prompt contains year reference '{kw}'")
            elif kw in ("current", "currently", "today", "latest", "recent", "now", "last year", "this year"):
                issues.append(f"Potentially time-sensitive: prompt contains '{kw}'")
            elif kw in ("president", "prime minister", "ceo"):
                issues.append(f"Potentially time-sensitive: prompt references a role '{kw}' that may change")
            break  # Only flag once per item
    
    # Gate 5: Deceptive/adversarial without plausible_wrong_answer
    difficulty = item.get("difficulty", "")
    if difficulty in ("deceptive", "adversarial"):
        pwa = item.get("plausible_wrong_answer", "")
        if not pwa or pwa.strip() == "":
            issues.append("Deceptive/adversarial item missing plausible_wrong_answer")
    
    return issues

# ---------------------------------------------------------------------------
# Override table: manually correct items that need special handling
# ---------------------------------------------------------------------------

# Items requiring special prompt overrides or answer corrections
PROMPT_OVERRIDES = {
    # v2_raw_069: constrained format prompt
    "v2_raw_069": None,  # keep as-is
    # v2_raw_083: multi-token gold answer
    "v2_raw_083": None,  # keep
    # v2_raw_090, 091, 165: "nothing" sentinel
    "v2_raw_090": None,
    "v2_raw_091": None,
    "v2_raw_165": None,
}

ANSWER_OVERRIDES = {
    # Lowercase all entity answers per spec
    # These are already handled in normalize_gold_answer but we note special cases
    "v2_raw_012": "h2o",      # H2O -> h2o (then alias covers H2O)
    "v2_raw_059": "yellow-green",  # chartreuse
    "v2_raw_069": "moon landing",  # constrained answer
    "v2_raw_083": "magic mirror on the wall",  # multi-token
    "v2_raw_093": "unspecified",   # Garden of Eden fruit is unspecified in the Bible
}

# Items that should be flagged as format issues despite our best rewrite
KNOWN_FORMAT_ISSUES = {
    "v2_raw_069": ["Constrained-choice prompt — answer options embedded in prompt; acceptable but unusual format."],
    "v2_raw_083": ["Gold answer is 4 tokens: 'magic mirror on the wall' — exceeds preferred 1-5 token limit."],
    "v2_raw_146": ["Gold answer is 2 tokens: 'empty hand' — acceptable but note multi-word entity."],
    "v2_raw_093": ["Gold answer is a sentinel/special value 'unspecified' — requires special grader handling."],
    "v2_raw_090": ["Gold answer is 'nothing' — sentinel value for 'not an acronym' answers; requires special grader."],
    "v2_raw_091": ["Gold answer is 'nothing' — sentinel value."],
    "v2_raw_165": ["Gold answer is 'nothing' — sentinel value."],
    "v2_raw_117": ["Gold answer '7 PM' contains uppercase and space — non-standard format. Time format required."],
    "v2_raw_184": ["Gold answer '1/4' is a fraction — non-standard format but prompt constrains to fraction form."],
    "v2_raw_075": ["Gold answer 'marianne williamson' is a 2-token proper name — acceptable but note."],
    "v2_raw_063": ["Gold answer 'richard marquand' is a 2-token proper name — acceptable."],
    "v2_raw_085": ["Note: Canada has most freshwater lakes — gold answer is factually correct."],
    "v2_raw_186": ["Note: Jupiter moon count is time-sensitive (as of 2024, 95 confirmed moons)."],
    "v2_raw_109": ["Note: Distance to Sun is approximate; prompt asks for nearest million km."],
    "v2_raw_215": ["Note: Verify number of portraits on US dollar bill — front has 2 (Washington + shield), back has different designs."],
}

# Dedup flags
DEDUP_FLAGS = {}

# ---------------------------------------------------------------------------
# Process all 223 items
# ---------------------------------------------------------------------------

canonicalized = []
alias_ledger = {}

for i, raw in enumerate(raw_candidates, start=1):
    cid = f"v2_{i:03d}"
    raw_id = raw.get("raw_id", f"v2_raw_{i:03d}")
    
    # Get fields
    prompt_raw = raw.get("prompt", "").strip()
    gold_raw = raw.get("gold_answer", "").strip()
    difficulty = raw.get("difficulty", "medium")
    item_family = raw.get("item_family", "")
    source = raw.get("source", "authored_v2")
    answer_type = raw.get("answer_type", "entity")
    note_raw = raw.get("note", "")
    pwa = raw.get("plausible_wrong_answer", "")
    reasoning_chain = raw.get("reasoning_chain", "")
    
    # Apply answer override if any
    if raw_id in ANSWER_OVERRIDES:
        gold_raw = ANSWER_OVERRIDES[raw_id]
    
    # Normalize gold answer
    gold_normalized = normalize_gold_answer(gold_raw, answer_type)
    
    # Special case: H2O should keep capital letters as gold (but lowercased per spec -> h2o)
    # The alias ledger will cover H2O
    
    # Normalize prompt
    prompt_normalized, format_instruction = normalize_prompt(prompt_raw, answer_type, gold_raw, raw)
    
    # Determine grader rule
    if answer_type in ("integer", "decimal"):
        grader_rule = "numeric_equivalence"
    elif answer_type == "yes_no":
        grader_rule = "yes_no_match"
    else:
        grader_rule = "alias_match"
    
    # Build aliases
    accepted_aliases, rejected_near_misses, alias_rationale = build_aliases(
        gold_normalized, answer_type, gold_raw, raw
    )
    
    # Check format gates
    format_issues = check_format_gates(raw, prompt_normalized, gold_normalized)
    
    # Apply known format issues
    if raw_id in KNOWN_FORMAT_ISSUES:
        for fi in KNOWN_FORMAT_ISSUES[raw_id]:
            if fi not in format_issues:
                format_issues.append(fi)
    
    # Check dedup against pilot
    if is_near_duplicate_of_pilot(prompt_normalized, gold_normalized):
        format_issues.append(f"DEDUP WARNING: Prompt is semantically similar to a pilot item.")
        DEDUP_FLAGS[cid] = True
    
    # Additional dedup: check gold answer + family overlap with pilot
    for pa, pdiff in pilot_answers:
        if pa == gold_normalized and len(gold_normalized) > 0:
            # Check domain similarity via item_family
            format_issues.append(f"DEDUP WARNING: Gold answer '{gold_normalized}' matches pilot item (difficulty: {pdiff}).")
            break
    
    format_pass = len(format_issues) == 0
    
    # Build the canonicalized item
    canon_item = {
        "prompt": prompt_normalized,
        "gold_answer": gold_normalized,
        "difficulty": difficulty,
        "item_family": item_family,
        "source": source,
        "answer_type": answer_type,
        "grader_rule": grader_rule,
        "format_instruction": format_instruction,
        "plausible_wrong_answer": pwa if pwa else "",
        "reasoning_chain": reasoning_chain if reasoning_chain else "",
        "note": note_raw,
        "canonical_id": cid,
        "format_pass": format_pass,
        "format_issues": format_issues,
    }
    
    # Build alias entry
    alias_entry = {
        "canonical_answer": gold_normalized,
        "accepted_aliases": accepted_aliases,
        "rejected_near_misses": rejected_near_misses,
        "alias_rationale": alias_rationale,
    }
    
    canonicalized.append(canon_item)
    alias_ledger[cid] = alias_entry

# ---------------------------------------------------------------------------
# Post-processing: fix specific known issues
# ---------------------------------------------------------------------------

# Fix item v2_117 (time format answer "7 PM") 
# The gold answer after normalization will be "7 pm" — that's fine
# Fix item v2_184 (fraction "1/4")
# normalize_gold_answer with type "entity" will handle it as lowercase "1/4"

# Check we have exactly 223 items
assert len(canonicalized) == 223, f"Expected 223, got {len(canonicalized)}"
assert len(alias_ledger) == 223, f"Expected 223 alias entries, got {len(alias_ledger)}"

# ---------------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------------

out_canon = f"{BASE}/data/harvest/v2_canonicalized_candidates.json"
out_alias = f"{BASE}/data/harvest/v2_alias_ledger.json"

with open(out_canon, "w") as f:
    json.dump(canonicalized, f, indent=2, ensure_ascii=False)

with open(out_alias, "w") as f:
    json.dump(alias_ledger, f, indent=2, ensure_ascii=False)

# ---------------------------------------------------------------------------
# Print summary
# ---------------------------------------------------------------------------

total = len(canonicalized)
pass_count = sum(1 for x in canonicalized if x["format_pass"])
fail_count = total - pass_count

print(f"\n=== CANONICALIZATION COMPLETE ===")
print(f"Total items: {total}")
print(f"Format PASS: {pass_count} ({100*pass_count//total}%)")
print(f"Format FAIL: {fail_count} ({100*fail_count//total}%)")

# Difficulty distribution
diff_dist = {}
for x in canonicalized:
    d = x["difficulty"]
    diff_dist[d] = diff_dist.get(d, 0) + 1
print(f"\nDifficulty distribution: {diff_dist}")

# Answer type distribution
at_dist = {}
for x in canonicalized:
    at = x["answer_type"]
    at_dist[at] = at_dist.get(at, 0) + 1
print(f"Answer type distribution: {at_dist}")

# Dedup flags
if DEDUP_FLAGS:
    print(f"\nDedup warnings: {list(DEDUP_FLAGS.keys())}")
else:
    print("\nNo dedup warnings.")

# Items with format issues
print(f"\nItems with format issues ({fail_count} total):")
for x in canonicalized:
    if not x["format_pass"]:
        print(f"  {x['canonical_id']} [{x['difficulty']}] [{x['answer_type']}]: {x['format_issues']}")

print(f"\nOutputs written to:")
print(f"  {out_canon}")
print(f"  {out_alias}")
