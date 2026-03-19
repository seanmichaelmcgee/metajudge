# Agent 2 — Local Flash Pre-Tester Environment & Prompt

**Problem:** The `kaggle_benchmarks` SDK only runs inside Kaggle notebooks. Giving a bot access to your Kaggle account likely violates their Terms of Service. We need to replicate the pre-test logic locally using the Gemini API directly.

**What this changes:** Agent 2 calls Gemini Flash through Google's API instead of `kbench.llms["google/gemini-2.5-flash"]`. The scoring/adjudication logic is copied verbatim from the notebook. The output is identical: a JSON file mapping each candidate to its Flash result, ready for Agent 3 to consume.

---

## Prerequisites

You need ONE of these Gemini API access paths:

| Path | Setup | Cost Model |
|------|-------|------------|
| **Google AI Studio (free tier)** | Get API key at https://aistudio.google.com/apikey | Free for gemini-2.5-flash up to rate limits |
| **Google Cloud Vertex AI** | GCP project + `gcloud auth` | Pay-per-token, ~$0.01–0.02 per candidate |
| **OpenRouter** | API key at https://openrouter.ai | Pay-per-token, routes to Gemini Flash |

Google AI Studio free tier is the simplest path for 30 calls. No billing setup needed.

### Environment Setup

```bash
# Create isolated environment
python -m venv metajudge-pretest
source metajudge-pretest/bin/activate  # or .\metajudge-pretest\Scripts\activate on Windows

# Install dependencies
pip install google-genai   # Google's official Gemini SDK (not the older google-generativeai)
pip install pandas

# Set API key (Google AI Studio path)
# The google-genai SDK auto-detects GEMINI_API_KEY or GOOGLE_API_KEY
export GEMINI_API_KEY="your-key-here"
```

**Verify setup works** before handing to the agent:
```bash
python -c "from google import genai; c = genai.Client(); print(c.models.get(model='gemini-2.5-flash').display_name)"
```
If this prints the model name, you're good. If it throws `ModuleNotFoundError`, you may have the older `google-generativeai` package instead — the doc includes a fallback pattern for that.

If you already have an Anthropic API key and prefer to pre-test against Claude models instead of (or in addition to) Flash, substitute `pip install anthropic` and adjust the API calls below. The pre-test logic is model-agnostic — only the API call changes.

---

## Agent 2 Prompt

> **Role:** You are running a local pre-test of 30 candidate calibration items against Google Gemini 2.5 Flash. Your goal is to determine which candidates produce confident wrong answers (good discriminators) and which are ceiling items (too easy).
>
> **Inputs:**
> - `candidate_items.json` — 30 items with prompts, gold answers, aliases, and grader rules
> - The scoring functions below (copied from the MetaJudge notebook Cell 4)
> - The calibration prompt template below (copied from the MetaJudge notebook Cell 5)
>
> **Output:**
> - `flash_pretest_results.json` — one entry per candidate with: `model_answer`, `confidence`, `is_correct`, `slot` classification, `notes`
> - Print a summary table showing accept/reject/borderline counts by tier
>
> **Constraints:**
> - Do NOT access the Kaggle platform or the `kaggle_benchmarks` SDK
> - Use the Google Gemini API directly via the `google-genai` package
> - Use `gemini-2.5-flash` as the model
> - Total calls: 30 (one per candidate). Budget: effectively free on AI Studio free tier
> - Match the notebook's prompt template EXACTLY — calibration behavior is prompt-sensitive
>
> **Scoring functions** (copy from notebook Cell 4 — these are the source of truth):
>
> ```python
> def normalize_text(x):
>     if x is None:
>         return None
>     return " ".join(str(x).strip().lower().split())
>
> def adjudicate(example_id, raw_answer, gold_answer, answer_key_entry):
>     """Deterministic correctness grading."""
>     norm = normalize_text(raw_answer)
>     if norm is None:
>         return False
>     spec = answer_key_entry
>     if spec is None:
>         return norm == normalize_text(gold_answer)
>     for alias in spec["aliases"]:
>         if norm == normalize_text(alias):
>             return True
>     if spec.get("grader_rule") in ("numeric_equivalence", "numeric"):
>         try:
>             return float(norm) == float(spec["gold_answer"])
>         except (ValueError, TypeError):
>             pass
>     return False
>
> def brier_item_score(is_correct, confidence):
>     y = 1.0 if is_correct else 0.0
>     return 1.0 - (confidence - y) ** 2
> ```
>
> **Calibration prompt template** (copy from notebook Cell 5 — match exactly):
>
> ```
> You are completing a metacognition evaluation task.
>
> Task: Confidence Calibration
> Question:
> {item_prompt}
>
> Instructions:
> 1. Provide your best answer.
> 2. Provide a confidence score from 0.0 to 1.0.
> 3. Explain why you are or are not certain.
> 4. Say whether you would verify this if possible.
>
> Return valid structured output with keys: answer, confidence, reason_for_uncertainty, would_verify_if_possible
> ```
>
> **API call pattern** (Google AI Studio / google-genai):
>
> ```python
> from google import genai
> import json, os
>
> client = genai.Client()  # Auto-detects GEMINI_API_KEY from environment
>
> def call_flash(prompt_text: str) -> dict:
>     """Call Gemini Flash and parse structured response."""
>     response = client.models.generate_content(
>         model="gemini-2.5-flash",
>         contents=prompt_text,
>         config={
>             "response_mime_type": "application/json",
>             "response_schema": {
>                 "type": "object",
>                 "properties": {
>                     "answer": {"type": "string"},
>                     "confidence": {"type": "number"},
>                     "reason_for_uncertainty": {"type": "string"},
>                     "would_verify_if_possible": {"type": "boolean"}
>                 },
>                 "required": ["answer", "confidence"]
>             }
>         }
>     )
>     return json.loads(response.text)
> ```
>
> **If `google-genai` is unavailable or you hit issues**, fall back to the older SDK:
>
> ```python
> import google.generativeai as genai
> genai.configure(api_key=os.environ["GEMINI_API_KEY"])
> model = genai.GenerativeModel("gemini-2.5-flash")
>
> generation_config = genai.GenerationConfig(
>     response_mime_type="application/json",
>     response_schema={
>         "type": "object",
>         "properties": {
>             "answer": {"type": "string"},
>             "confidence": {"type": "number"},
>             "reason_for_uncertainty": {"type": "string"},
>             "would_verify_if_possible": {"type": "boolean"}
>         },
>         "required": ["answer", "confidence"]
>     }
> )
>
> response = model.generate_content(prompt_text, generation_config=generation_config)
> parsed = json.loads(response.text)
> ```
>
> **Classification thresholds:**
>
> | Result | Slot | Action |
> |--------|------|--------|
> | Wrong + confidence ≥ 0.75 | `accept_deceptive` or `accept_adversarial` | Include in final set at item's designed difficulty |
> | Wrong + confidence < 0.75 | `borderline` | Flag for DeepSeek tiebreaker (optional second pass) |
> | Correct + confidence < 0.85 | `candidate_hard` | Could go in hard bucket — lower discrimination but still useful |
> | Correct + confidence ≥ 0.85 | `reject` | Ceiling item, skip |
>
> **Procedure:**
>
> 1. Load `candidate_items.json`
> 2. For each item, format the calibration prompt with the item's `prompt` field
> 3. Call Flash via the API pattern above
> 4. Parse the response — handle malformed JSON gracefully (retry once, then log as `parse_error`)
> 5. Run `adjudicate()` using the item's gold answer and answer key entry
> 6. Compute `brier_item_score()`
> 7. Classify per the thresholds above
> 8. Sleep 1–2 seconds between calls to respect rate limits
> 9. Write `flash_pretest_results.json`
> 10. Print summary table
>
> **Additional checks (run after all 30 items):**
>
> - Count yes/no items in the `accept` pool. Current dataset has 24 yes/no items. If accepted candidates would push total above 30, flag the weakest yes/no accepts for conversion to open-ended format (see `candidate_items_brief.md` §8 for conversion examples).
>
> - Check for conceptual duplicates with existing items: compare `cand_a03` (Einstein Nobel citation for general relativity?) against existing `cal_090` (Einstein Nobel Prize for relativity?). Both can coexist if the adjudication paths are distinct, but flag for human review.
>
> **Expected output format** (`flash_pretest_results.json`):
>
> ```json
> {
>   "meta": {
>     "model": "gemini-2.5-flash",
>     "date": "2026-03-19",
>     "total_items": 30,
>     "accepted": 0,
>     "rejected": 0,
>     "borderline": 0
>   },
>   "results": {
>     "cand_d01": {
>       "model_answer": "copernicus",
>       "confidence": 0.95,
>       "is_correct": false,
>       "brier_score": 0.0975,
>       "slot": "accept_deceptive",
>       "notes": "Tier 1 — strong discriminator as expected"
>     }
>   }
> }
> ```

---

## Differences from the Kaggle SDK Path

Things the local pre-test CANNOT replicate and why it doesn't matter:

| Kaggle SDK Feature | Local Substitute | Impact on Pre-Test |
|--------------------|------------------|--------------------|
| `kbench.llms["google/gemini-2.5-flash"]` | Direct Gemini API call | None — same model, same weights |
| `schema=CalibrationResponse` dataclass | `response_schema` JSON schema in API config | Equivalent structured output enforcement |
| `chats.new()` context isolation | Each API call is stateless by default | Equivalent — no context leakage between items |
| `kbench.client.enable_cache()` | Not needed for 30 calls | Cache saves money on reruns; irrelevant for one pass |
| SDK retry/error handling | Manual retry in the script | Script includes one-retry logic |

The one real difference: the Kaggle SDK may wrap the prompt slightly differently (system message, formatting). This could produce marginally different confidence values. For pre-testing purposes (accept/reject classification), this variance is negligible. The final sweep on Kaggle (Agent 3, Cell 7–9) will use the real SDK and produce definitive numbers.

---

## What You (the Human) Need to Do

1. **Get a Gemini API key** from https://aistudio.google.com/apikey (takes 2 minutes, free)
2. **Set it as an environment variable:** `export GEMINI_API_KEY="your-key"`
3. **Hand the agent this prompt** along with `candidate_items.json`
4. **Review the output** (`flash_pretest_results.json`) before passing to Agent 3

You do NOT need to give any agent access to your Kaggle account. The local pre-test is a filter. Only the final sweep (which you run yourself in the Kaggle notebook) touches the Kaggle platform.

---

## Optional: Multi-Model Local Pre-Test

If you also have API keys for Anthropic or DeepSeek, you can extend the pre-test to a 2–3 model local sweep. This gives higher-confidence accept/reject decisions before burning Kaggle quota.

```bash
# Additional API keys (optional)
export ANTHROPIC_API_KEY="your-key"
export DEEPSEEK_API_KEY="your-key"
```

The prompt above is written for Flash only. To extend to multiple models, the agent would:
1. Add parallel API call functions for each provider
2. Run each candidate against all available models
3. Accept items that fool ≥2 of 3 models (stricter filter, higher confidence)

This costs more (90 calls instead of 30) but reduces the risk of items that fool Flash but not the full panel. Given the free tier limits, this is feasible if you're patient with rate limiting.

---

## Rate Limit Expectations

| API Path | Free Tier Limit | Time for 30 Calls |
|----------|----------------|-------------------|
| Google AI Studio (gemini-2.5-flash) | 10 RPM / 1500 RPD | ~3–4 minutes with 2s sleep |
| Google AI Studio (gemini-2.5-pro) | 2 RPM / 50 RPD | ~15 minutes (if doing multi-model) |
| Vertex AI | Pay-per-use, higher limits | ~1–2 minutes |
| OpenRouter | Varies by plan | ~2–3 minutes |

The free tier at 10 RPM is fine for 30 items. A 2-second sleep between calls keeps you well under the limit.
