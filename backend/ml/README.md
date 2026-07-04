# `backend/ml/` — ML/DL Layer

Training and inference for Asahlagi's machine learning components.

> See [`/ML.md`](../../ML.md) for full ML/DL strategy. This README is the **practical guide** for running training & inference.

## Structure

```
ml/
├── classifier/                  # DESTA — sklearn Random Forest
│   ├── data_generation.py      # synthetic dataset (10k samples)
│   ├── train.py                # train + save .pkl artifact
│   ├── inference.py            # load .pkl + predict (called from app)
│   └── artifacts/
│       └── classifier.pkl      # trained model (committed to repo)
├── generator/                   # AUDRY — fine-tuned IndoT5 (DL)
│   ├── inference.py            # load from HF Hub + generate questions
│   └── notebooks/
│       └── train_quiz_generator.ipynb  # Colab notebook (1-2h training)
├── requirements-ml.txt         # heavy training deps (separate from app)
└── README.md                   # this file
```

## When to use which file

| Task | Where to look |
|---|---|
| Run app, see ML predictions in action | Just run uvicorn — inference loads automatically |
| Re-train Desta's classifier locally | `python -m ml.classifier.train` from `backend/` |
| Re-train Audry's DL model | Open `ml/generator/notebooks/train_quiz_generator.ipynb` in Colab |
| Modify synthetic data generation | Edit `ml/classifier/data_generation.py` |
| Change DL model name / version | Edit `_MODEL_NAME` in `ml/generator/inference.py` |
| Test ML inference in isolation | Each `inference.py` has a `if __name__ == "__main__":` smoke test |

---

## Quickstart per role

### Desta — train sklearn classifier

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt   # already has sklearn

# Train
python -m ml.classifier.train

# Expected output:
#   Generating 10000 synthetic samples...
#   Training Random Forest...
#   Test accuracy: 94.2%
#   Saved artifact: ml/classifier/artifacts/classifier.pkl
```

After training, `classifier.pkl` is created. Commit it to the repo (small, < 5MB).

### Audry — train DL quiz generator

**You need a free Hugging Face account first**: https://huggingface.co/join

1. Generate a Write access token: Settings → Access Tokens → New token (role: Write)
2. Open `ml/generator/notebooks/train_quiz_generator.ipynb` in Google Colab
3. Switch runtime: Runtime → Change runtime type → T4 GPU
4. Run cells in order (provides instructions for HF login, dataset download, training, push)
5. Training takes 1-2 hours
6. Final cell pushes model to your HF account: `<your-username>/indot5-quizgen-asahlagi`

After training, edit `ml/generator/inference.py` to point `_MODEL_NAME` to your published model:

```python
_MODEL_NAME = "audry-asahlagi/indot5-quizgen-asahlagi"  # ← replace with your actual repo
```

Commit the updated `inference.py`.

---

## How models are loaded at app runtime

When the FastAPI app starts:

1. Python imports `app.services.quiz_generator`
2. That imports `ml.generator.inference`
3. `inference.py` loads the IndoT5 model from Hugging Face Hub (~10s, ~1GB cached locally on first run)
4. Same for `app.services.understanding_classifier` → `ml.classifier.inference` → loads `.pkl`

So the **first request after server boot is slow** (cold start ~25-50s for `/quiz/generate`). Subsequent requests skip model loading.

### Pre-warming for demo

Before the demo, hit a sample request to warm up:

```bash
curl http://localhost:8000/health
# Then trigger one quiz generation to load the model:
curl -X POST http://localhost:8000/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{"material_text": "Sample material untuk warmup. Min 100 chars supaya valid. Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore."}'
```

After warm-up, all subsequent demo requests will be 15-40s for generate, milliseconds for everything else.

---

## Fallback behavior

Both inference modules **gracefully fall back to rule-based** if model loading fails:

- `ml/generator/inference.py`: if HF Hub unreachable → use rule-based fill-in-the-blank from `app/services/quiz_generator.py` placeholder logic
- `ml/classifier/inference.py`: if `.pkl` missing → use rule-based threshold from `app/services/understanding_classifier.py` placeholder logic

Demo never breaks. But ML/DL accuracy claim only valid when models are actually loaded — verify at startup logs.

### Verifying model loaded

After `uvicorn` starts, check logs for:

```
INFO     ml.generator: Loaded IndoT5 from HF Hub: audry-asahlagi/indot5-quizgen-asahlagi
INFO     ml.classifier: Loaded classifier from artifacts/classifier.pkl (sklearn RandomForest)
```

If you see warnings like `WARNING ml.generator: HF Hub unreachable, using rule-based fallback`, the DL model isn't loaded. Fix before demo.

---

## Common issues

### "OSError: Can't load tokenizer for 'audry-asahlagi/indot5-quizgen-asahlagi'"
Audry hasn't pushed the model to HF Hub yet. Either:
- Wait for Audry to finish training & push
- Or temporarily switch `_MODEL_NAME` to base pretrained `Wikidepia/IndoT5-base` (lower quality, but app runs)

### "FileNotFoundError: classifier.pkl"
Desta hasn't trained the classifier yet. Either:
- Run `python -m ml.classifier.train` to generate it
- Or rely on rule-based fallback (still works)

### "Model loading is super slow on first run"
Expected — first run downloads ~1GB model from HF Hub to `~/.cache/huggingface/hub/`. Subsequent runs use cache (fast).

If you want to pre-download:
```bash
python -c "from transformers import T5ForConditionalGeneration; T5ForConditionalGeneration.from_pretrained('audry-asahlagi/indot5-quizgen-asahlagi')"
```

### "Inference is too slow on demo machine"
On weaker CPUs, per-question generation may exceed 8s. Options:
- Reduce `max_length` in `inference.py` (e.g., 48 instead of 64)
- Switch to greedy decoding (set `num_beams=1`) — faster but slightly lower quality
- Pre-generate quiz for demo materials (cache in storage)

---

## References

- `/ML.md` — full ML/DL strategy, dataset choices, model rationale
- `/ARCHITECTURE.md` §5b — ML layer structure
- Hugging Face docs: https://huggingface.co/docs/transformers
- TyDiQA dataset: https://huggingface.co/datasets/tydiqa
- scikit-learn RF docs: https://scikit-learn.org/stable/modules/ensemble.html#random-forests
