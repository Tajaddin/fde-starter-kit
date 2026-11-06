# classify — LLM-as-classifier starter

Returns a `(label, confidence, reasoning)` triple per input. The included eval harness computes accuracy, mean confidence, and accuracy on the high-confidence subset (≥ 0.7) so you can see if confidence is calibrated.

```bash
pip install -e ".[anthropic,dev]"
python app.py
```

The classifier is just a single chat call; the value-add is parsing the JSON robustly, clipping confidence to [0, 1], and falling back to the first label on parse failure (instead of crashing the pipeline).
