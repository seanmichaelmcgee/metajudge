# Evidence Notebook — Execution Guide

**Time required:** ~2 minutes  
**Quota cost:** ~$0.05 (6 LLM calls on 2-row datasets)

---

## Option A: Upload the .ipynb (Recommended)

1. Go to https://www.kaggle.com/competitions/kaggle-measuring-agi
2. Click **"Join Hackathon"** if you haven't already
3. Go to the **Code** tab → click **"+ New Notebook"**
4. In the notebook editor, click **File → Upload Notebook**
5. Upload `metajudge_evidence.ipynb` from this directory
6. Click **"Run All"** (or run cells 1–5 sequentially with Shift+Enter)
7. Wait for all cells to complete (~30-60 seconds)
8. **Save the notebook version** (Ctrl+S or File → Save Version)

## Option B: Paste Cell-by-Cell

If upload doesn't work, paste each cell manually. The notebook has 5 code cells.
The full code is in `minimal_evidence_notebook.py` in this directory.

---

## What to Capture

After execution, take screenshots or copy outputs showing:

| Screenshot | What it proves |
|-----------|---------------|
| Cell 1 output | SDK imports work, default LLM name visible |
| Cell 2 output | Structured `schema=` returns typed object, single task runs |
| Cell 3 output | `.evaluate()` runs over DataFrame, returns results |
| Cell 4 output | Wrapper task calls sub-task via `.evaluate()`, returns composite float |
| Cell 5 output | `%choose` selects the top-level task for submission |

Also capture the **notebook header/URL bar** showing this is a competition-linked notebook.

---

## Expected Outputs

**Cell 1:**
```
SDK imported: kaggle_benchmarks
Default LLM: google/gemini-2.0-flash  (or similar)
Judge LLM:   google/gemini-2.0-flash  (or similar)
Environment OK
```

**Cell 2:**
```
  answer='Paris', conf=0.95, correct=True, score=0.950
Single run result: 0.95  (approximate — depends on model confidence)
```

**Cell 3:**
```
Evaluate returned 2 rows
  (DataFrame with question, gold_answer, result columns)
```

**Cell 4:**
```
Sub-results: [0.xx, 0.xx]
Composite score: 0.xxxx
Wrapper task returned: 0.xxxx
```

**Cell 5:**
```
(Kaggle's %choose confirmation — may show task name or a checkmark)
```

---

## If Something Fails

- **ImportError on `kaggle_benchmarks`**: You're not in a competition notebook environment. Make sure the notebook is linked to the competition.
- **`kbench.llm` is None**: The default model may not be loaded. Try `kbench.llms["google/gemini-2.0-flash"]` explicitly.
- **`.evaluate()` hangs**: Reduce n_jobs to 1 (already set). Check quota.
- **`%choose` fails**: Verify the task name matches exactly (`metacognition_suite`).
- **Any other error**: Copy the full traceback — it will tell us exactly what SDK assumption was wrong.

Report any failure as-is. A specific error message is more valuable than a workaround.
