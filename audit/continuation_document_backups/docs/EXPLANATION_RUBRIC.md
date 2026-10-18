# Explanation-quality rubric v1

Score each delivered response independently of whether its patch passes. Read the original code, visible failure, full response, and test record. Do not infer that a passing patch makes its explanation correct. Use one reviewer worksheet per rater; independently double-score a subset if possible and report disagreements rather than silently averaging them away.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Root-cause accuracy | Missing, wrong, or contradictory diagnosis; generic inability to diagnose | Broadly relevant but incomplete or materially ambiguous mechanism | Correctly identifies the actual faulty construct and why it fails |
| Repair reasoning | Missing/incorrect rationale, or no usable repair reasoning | Relevant fix/change mentioned with limited causal explanation | Correctly connects a specific repair to restored behavior and a general rule |
| Beginner clarity | Missing, incoherent, or excessive repetitive text that obscures the point | Mostly readable but vague, redundant, or uses unexplained terms | Concise, understandable language with adequate explanation of needed concepts |
| Case specificity | Generic stock text or refers to the wrong mechanism | Identifies a relevant construct, but omits the key condition/operator/change | Identifies the actual code construct/condition/change for this case |

Total: 0?8. Report individual dimensions and total; report the number rated separately from delivered responses. Accuracy is a separate dimension from readability, and an explanation may be clear but wrong. A statement that the baseline could not diagnose the case is honest, but does not identify the root cause and earns accuracy/reasoning zero. Empty explanation sections earn zero for their corresponding dimensions. Missing API responses are excluded, never assigned a quality score of zero.

```powershell
.\.venv\Scripts\python.exe explanation_review.py "results\runs\RUN_DIRECTORY"
# Edit the new worksheet's ratings.csv, keeping exact response text/identities intact.
.\.venv\Scripts\python.exe explanation_review.py "results\runs\RUN_DIRECTORY" --ratings "results\explanation_reviews\WORKSHEET\ratings.csv"
```

Each scored row requires all four integer scores, `rater`, `rater_type` (`human` or `AI_assisted`), an exact `evidence_quote` substring, and a rationale. The tool validates provenance and arithmetic; it cannot automatically verify the semantic judgment. Review outputs are separate from sealed experimental evidence. The worksheet is the editable artifact; source responses and sealed run records remain unchanged. `structural_checks.csv` only measures section presence and word counts and must not be represented as semantic quality or learning effectiveness.
