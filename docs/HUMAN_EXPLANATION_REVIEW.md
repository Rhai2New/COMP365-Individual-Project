# Student explanation-review procedure

Use `results/explanation_reviews/20261018T154535_622694Z_worksheet_704dd1d7/ratings.csv` as the blank worksheet. It has 40 delivered baseline/Qwen responses and no human scores. Additional Gemini worksheets are listed below. Each contains only delivered responses; missing API responses receive no score. Earlier `preliminary_AI_ratings.csv` and all `AI_assisted` rows are preliminary AI judgments, not independent human ratings.

1. Copy the blank worksheet to a file with your rater name. Avoid reading the AI scores first if you want an independent judgment.
2. Read [EXPLANATION_RUBRIC.md](EXPLANATION_RUBRIC.md). Open each row's original source, visible failure context, exact full response, and validation using the supplied paths. Read full responses even when section extraction is incomplete.
3. Enter four scores (0, 1, or 2), your name in `rater`, and `human` in `rater_type` only for judgments you personally made. Add an exact response substring in `evidence_quote` and your own rationale. Leave unreviewed rows blank. Preserve model/run identity and quoted explanation text.
4. Judge the explanation independently of patch success. Missing API responses are excluded. Section presence and word counts do not establish quality.
5. Validate your completed worksheet and calculate means:

```powershell
.\.venv\Scripts\python.exe explanation_review.py results\runs\20261018T131412_396245Z_benchmark_41bb2533 --ratings YOUR_REVIEW.csv
```

The command creates separate scored evidence. Report rater type, number actually rated, individual dimensions, scale 0-8, and any assistance received. Keep a separate worksheet for each independent rater and document disagreements. A single student review is not a multi-rater study or participant learning experiment.

## Authenticated Gemini worksheets

- `results/explanation_reviews/20261018T192906_275469Z_worksheet_f153bd84/ratings.csv` — source `results/gemini_sessions/20261018T191709_946022Z_staged_579ea3f4/runs/20261018T191710_229284Z_benchmark_876caa4e`.
- `results/explanation_reviews/20261018T192906_526278Z_worksheet_36b1ff42/ratings.csv` — source `results/gemini_sessions/20261018T191709_946022Z_staged_579ea3f4/runs/20261018T191824_916274Z_benchmark_b71c7f0b`.

Use `explanation_review.py SOURCE_RUN --ratings YOUR_COMPLETED_COPY.csv` separately for each shard. Leave original blank worksheets intact. Genuine human ratings remain zero until you personally complete and validate them. No explanation ratings were fabricated.
