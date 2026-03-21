# MetaJudge Dataset Packaging Plan

## What to upload to Kaggle

### Option A: Single Kaggle Dataset (Recommended)
Create a Kaggle Dataset called `metajudge-benchmark` containing:
```
metajudge-benchmark/
├── metajudge_benchmark_v1.json  (102-item V4.2 dataset)
├── adjudication_registry.json   (102-entry grading registry)
└── metajudge/                   (scoring package)
    ├── __init__.py
    ├── scoring/
    │   ├── __init__.py
    │   ├── adjudication.py
    │   ├── grading_v2.py
    │   ├── calibration_metrics.py
    │   ├── composite_score.py
    │   └── abstention_metrics.py
    └── utils/
        ├── __init__.py
        └── text.py
```

### Upload Process
1. Create the directory structure locally
2. Go to https://www.kaggle.com/datasets/new
3. Upload the folder
4. Set slug to `metajudge-benchmark`
5. Set visibility to Public
6. The lean notebook references `/kaggle/input/metajudge-benchmark/`

### Versioning
When the dataset changes:
- V4.2: Current (7 IOED replacements)
- Future: Increment version, update notebook cell 0 header
