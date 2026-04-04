# Partial Model Audit — v6.2

Models with incomplete task coverage. Scores reported per-task only (no MetaScore).


---

## claude-sonnet-4@20250514

### Calibration: 105 items | Acc=96/105 (91.4%) | 1-Brier=0.9110 | Norm=0.644

### sc_c2: 23 items | T1=100.0% T2=100.0% Δ=+0.000 | Norm=0.500 | Dmg=0

Transitions: {'maintain_correct': 15, 'neutral_revision': 8}


---

## gemma-4-31b

### Abstention: 68 items | UWAA=0.8051 | Norm=0.513 | ActAcc=48.5%

### sc_c1: 28 items | T1=96.4% T2=89.3% Δ=-0.071 | Norm=0.114 | Dmg=2

Transitions: {'maintain_correct': 21, 'damage': 2, 'neutral_revision': 4, 'stubborn_wrong': 1}


---

## gpt-5.4-2026-03-05

### Abstention: 72 items | UWAA=0.8201 | Norm=0.550 | ActAcc=59.7%

### sc_c1: 28 items | T1=82.1% T2=78.6% Δ=-0.036 | Norm=0.257 | Dmg=4

Transitions: {'damage': 4, 'failed_revision': 2, 'neutral_revision': 15, 'maintain_correct': 4, 'correction_gain': 3}

### sc_c2: 23 items | T1=100.0% T2=95.7% Δ=-0.043 | Norm=0.391 | Dmg=1

Transitions: {'maintain_correct': 16, 'neutral_revision': 6, 'damage': 1}
