# ML/DL Strategy — Asahlagi

**Project**: Sistem Deteksi Tingkat Pemahaman Mahasiswa Berdasarkan Hasil Kuis Berbasis Data
**Team**: TP-G005
**Status**: Draft v1.0 — needs team review before lock-in
**Last updated**: 2026-05-06

---

## 1. Overview

This document is the **single source of truth for the ML/DL strategy** of Asahlagi. It explains:

- Where ML/DL fits in the architecture
- Which models are used and why
- How datasets are sourced/generated
- How training and deployment work
- What metrics to track

> Sister documents:
> - `ARCHITECTURE.md` §5b — ML layer structure (where files live)
> - `PRD.md` §10.2, §10.5, §15 — product-level requirements
> - `backend/ml/README.md` — practical guide for running training

---

## 2. Hybrid Strategy: DL + ML Konvensional

We use **both** Deep Learning and conventional Machine Learning, applied to different problems based on what each is fundamentally good at.

| Component | Approach | Why this approach |
|---|---|---|
| **Quiz generation** (text generation from material) | **Deep Learning** (fine-tuned IndoT5) | Text generation requires sequence-to-sequence modeling. ML konvensional cannot generate text. Indonesian-specific pretrained model gives natural-feeling Indonesian. |
| **Understanding classification** (3-level label from numeric features) | **Conventional ML** (sklearn Random Forest) | Tabular features with discrete labels. sklearn is ideal for this; DL would be overkill and require more data. |
| Insight & Recommendation | **Template + sub-conditions** | Output quality matters more than novelty. Template-based ensures voice consistency with `BRAND.md`; uncontrolled NLG would risk awkward tone. |

This split lets the team demonstrate **breadth** (DL + ML) while choosing the right tool per problem. It also balances workload: Audry handles the harder DL task, Desta handles the simpler ML task plus the template engines.

---

## 3. Quiz Generation (Audry's Domain)

### Problem statement
Given a paragraph of Indonesian learning material (e.g., 200-2000 chars), generate 5 multiple-choice questions where:
- Each question has exactly 4 options
- Exactly 1 option is correct
- Questions are relevant to the material

### Model choice: **Wikidepia/IndoT5-base**

A T5 (Text-to-Text Transfer Transformer) model pretrained on Indonesian corpora, available on Hugging Face Hub.

**Specs**:
- Architecture: T5 base (~220M parameters)
- Pretrained on: Indonesian Wikipedia, Common Crawl Indonesian subset, news articles
- Tokenizer: SentencePiece, Indonesian vocabulary

**Why not other models?**

| Alternative | Why rejected |
|---|---|
| `mT5-small` (multilingual) | Smaller (~300M params, faster) but less natural Indonesian. We accept slower inference for better quality. |
| `IndoBERT` | Encoder-only — not designed for generation. Better for classification/extraction. |
| `cahya/t5-base-indonesian-summarization-cased` | Fine-tuned for summarization, not QG. Different output distribution. |
| GPT-style (Llama, GPT-2 ID) | Over-spec for capstone scope; deployment complexity; licensing concerns. |

**Why fine-tune (vs. use pretrained directly)?**

Pretrained IndoT5 understands Indonesian text but isn't tuned for question generation specifically. Fine-tuning on TyDiQA-id teaches it the input→output pattern: passage → question.

Without fine-tuning: model might output summaries, paraphrases, or generic text — not questions.
With fine-tuning: model reliably produces interrogative sentences relevant to the input.

### Fine-tuning: postponed (2026-05-08), done (2026-05-26), answer-aware v2 (2026-06-14)

**Status**: DONE. Fine-tuned `Wikidepia/IndoT5-base` on TyDiQA-id and deployed as
`raviarnan/indot5-quizgen-asahlagi`. The quiz-gen HF Space and the backend now use it.
The notes below keep the original postponement history for context.

**Answer-aware v2 (2026-06-14)**: the first fine-tune trained on the bare answer
sentence (plain QG: `passage → question`), so the model never learned *which* span to
ask about — the backend then guessed the answer with `max(keywords, key=len)`, producing
nonsensical options ("Berapa jumlah planet?" → "mengitarinya"). Fixed in two layers:
- **Inference (live)**: `qg_core.py` (shared by the HF Space + local CPU) now picks the
  answer span first, highlights it (`<hl>`), enforces question/answer consistency, and
  falls back to a coherent cloze — so the correct answer always answers the question.
- **Model v2**: `notebooks/train_quiz_generator.ipynb` now trains *answer-aware* — the
  answer span is wrapped in `<hl> … <hl>` (registered as a special token) so the model
  learns to target it. Re-run on Colab and `push_to_hub` to the same repo id; the Space
  upgrades on Factory rebuild (no code change). See ROADMAP §3.5.

**What happened (2026-05-08)**: first training attempt in Colab used `fp16=True` (default in our notebook template). T5 has known fp16 instability — gradients overflowed to NaN, training loss collapsed to 0, and model produced garbage output ("aaaaaaaaa..." for any input).

**Interim decision**: shipped the MVP with base pretrained `Wikidepia/IndoT5-base` (no fine-tuning) plus a per-question quality check that falls back to rule-based generation when DL output is unusable.

**Justification for capstone scope**:
- T5 IS a deep learning model (220M parameters, transformer architecture). Inference IS deep learning.
- The conventional ML component (Random Forest classifier, see §4) is fully intact.
- Hybrid DL + ML requirement is satisfied.
- Quality is acceptable for demo: when DL output is poor, the wrapper falls back to rule-based questions (still functional, just not as varied).

**Resolution (2026-05-26)**: fine-tuning completed via [`backend/ml/generator/notebooks/train_quiz_generator.ipynb`](../backend/ml/generator/notebooks/train_quiz_generator.ipynb). The fix was `fp16=False` (full fp32 on the T4). Trained to 8 epochs with a per-epoch checkpoint sweep; eval loss bottomed at epoch 3 and rose afterward (overfitting), so **epoch 4** was selected (verified good generations + near-minimum eval loss). Pushed to `raviarnan/indot5-quizgen-asahlagi`; the quiz-gen Space (`huggingface/quizgen/app.py`) and backend now use it. Result: DL questions are far more natural than the base model (e.g. "Kapan proklamasi kemerdekaan Indonesia dilakukan?").

**Data prepared (2026-05-25)**: `backend/ml/generator/data/prepare_tydiqa.py` downloads TyDiQA
(Gold Passage), filters the Indonesian subset, and emits question-generation pairs:
**5,702 train / 565 val**. Output JSONL is gitignored (regenerate with
`python -m ml.generator.data.prepare_tydiqa`). Each row provides two input templates:
`input_plain` (`"buat pertanyaan: {answer sentence}"`, matches current inference) and
`input_hl` (answer-aware, answer wrapped in `<hl> ... <hl>`); `target` is the question.
Distractors stay out of the model (handled by `app/services/_distractors.py`), so the model
only learns passage to question.

### Quality gate for non-fine-tuned inference

Because base IndoT5 isn't trained for QG specifically, occasional outputs can be low-quality (paraphrases, summaries, or repeating characters when the model "collapses"). To handle this, `ml/generator/inference.py` includes a quality check:

```python
def _is_question_quality_acceptable(question: str) -> bool:
    # Drop outputs that are: too short, dominated by a single character,
    # or empty after stripping.
```

When too many questions fail the check, the wrapper in `app/services/quiz_generator.py` falls back to rule-based fill-in-the-blank generation.

### Dataset: **TyDiQA-id**

- Source: [TyDiQA](https://github.com/google-research-datasets/tydiqa) (Google Research)
- Indonesian subset: ~5,500 question-answer pairs
- Format: each row has `passage`, `question`, `answer_text`, `answer_start`
- License: CC-BY-SA 3.0 (free for academic use)
- Access: Hugging Face Datasets — `load_dataset("tydiqa", "secondary_task", split="train")`, then filter by `language == "indonesian"`

### Training procedure

**Where**: Google Colab (free tier, T4 GPU). See `backend/ml/generator/notebooks/train_quiz_generator.ipynb`.

**Hyperparameters** (starting point — Audry tunes):
- Learning rate: 1e-4
- Batch size: 8 (Colab T4 memory-fitting)
- Epochs: 3-5
- Max input length: 512 tokens
- Max output length: 64 tokens (questions are short)
- Optimizer: AdamW
- Mixed precision (fp16) — enabled for T4

**Expected training time**: 1-2 hours on Colab T4 free tier.

**Output**: fine-tuned model directory containing `pytorch_model.bin`, `config.json`, `tokenizer.json`, etc.

### Distribution: **Hugging Face Hub**

After training, push to public HF Hub repo:
```python
model.push_to_hub("audry-asahlagi/indot5-quizgen-asahlagi")
tokenizer.push_to_hub("audry-asahlagi/indot5-quizgen-asahlagi")
```

Backend loads at startup:
```python
from transformers import T5ForConditionalGeneration, T5Tokenizer

MODEL_NAME = "audry-asahlagi/indot5-quizgen-asahlagi"
model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
```

First load downloads ~1GB to `~/.cache/huggingface/`; subsequent runs use cache.

### Inference at runtime

**Hosting strategy: 3-tier fallback** (per `backend/ml/generator/inference.py`):

1. **HF Space (cloud)** — preferred. See §3.5 below.
2. **Local CPU** — fallback if HF Space unreachable.
3. **Rule-based** — final fallback if both fail.

**Hardware (when local CPU is used)**: backend CPU (no GPU available locally).

**Per-question latency**: 3-8s on typical CPU (e.g., 4-core 2.5GHz).
**Per-quiz latency** (5 questions): 6-15s in practice.

### 3.5 HF Spaces deployment

We deploy the same DL inference logic as a **Hugging Face Space** at `huggingface/quizgen/` to get cloud-hosted inference. The local backend calls this Space; if it's down, backend falls back to local CPU.

**Why HF Space (not Inference API or Colab)?**

| Option | Pros | Cons |
|---|---|---|
| **HF Space (chosen)** | Free, dedicated URL, no rate limit, persistent until 48h idle | Need to set up FastAPI + Dockerfile |
| HF Inference API | Zero setup | Rate-limited (~50 req/h), shared infra |
| Colab + tunnel | Free GPU | Disconnect every 90min, not designed for serving — too brittle for demo |

**Files in `huggingface/quizgen/`:**
- `app.py` — FastAPI app with `/generate` endpoint
- `Dockerfile` — image build for Space
- `requirements.txt` — Space-specific deps
- `README.md` — HF Space metadata (title, emoji, SDK config)

**Deployment**: see [`huggingface/quizgen/README.md`](../huggingface/quizgen/README.md) and walkthrough in `docs/tugas/ravi.md`.

**Endpoints exposed by Space**:
- `GET /` — health check returning `{"status": "ready"}`
- `POST /generate` — accepts `{material_text}`, returns `{questions: [...]}`

**Cold start / sleep**: free tier sleeps after 48h idle. First request after sleep takes 30-60s to wake. **Pre-demo: hit `/` 10 minutes before** to ensure Space is awake.

**Optimization options** (apply if needed):
1. **Batch all 5 questions in one inference call** — T5 supports batching, can reduce total time by ~30%.
2. **Greedy decoding** instead of beam search — faster, slightly lower quality.
3. **Smaller `max_length`** — caps generation time per question.
4. **Model quantization** (int8 via `bitsandbytes`) — ~2x speedup on CPU, ~1% quality loss. Last resort.

### Generating multiple-choice options

The fine-tuned model generates a question + correct answer. Options (distractors) are generated separately:

**Strategy 1 (recommended for MVP)**: extract distractors from the source material itself
- Tokenize material, find nouns/key terms via simple heuristics
- Pick 3 terms that are NOT the correct answer
- Combine: [correct, distractor1, distractor2, distractor3], shuffle, track correct index

**Strategy 2 (post-MVP)**: train a separate distractor generation model. Out of scope.

### Quality metrics

Track in training notebook:
- **BLEU score** (vs. ground truth questions in TyDiQA-id) — tells us how close generated questions are to natural human-written ones.
- **Manual review**: spot-check 20-30 generated questions. Are they grammatical? Relevant to the passage? Have a clear answer?
- **End-to-end test**: feed 5 dummy materials, count how many generated quizzes pass manual review (target: ≥ 4/5).

### Fallback

If HF Hub is unreachable or model fails to load, `inference.py` falls back to the existing rule-based generator (already scaffolded). Log a warning. Demo still works.

---

## 4. Understanding Classification (Desta's Domain)

### Problem statement
Given quiz performance features (`score_percentage`, `time_taken_seconds`, `correct_count`, `wrong_count`, `unanswered_count`), classify the user's understanding into one of 3 categories: **high**, **medium**, **low**.

### Model choice: **scikit-learn Random Forest Classifier**

**Why Random Forest?**
- Handles non-linear feature interactions out of the box (e.g., "high score AND fast time → high")
- Robust to outliers and noisy data
- Interpretable — exposes `feature_importances_` for capstone explanation
- Trains in <1 minute on CPU
- No hyperparameter sensitivity (works well with defaults)
- Pickle artifact is tiny (~1-5 MB)

**Alternatives considered**:
| Alternative | Why not |
|---|---|
| Logistic Regression | Linear — misses interactions. Too simple to be interesting. |
| Gradient Boosting (XGBoost) | Slightly better accuracy potential, but more hyperparameter tuning. RF gives ≥85% accuracy with defaults; over-engineering not justified for capstone. |
| Neural Network (sklearn MLP) | Overkill for tabular; needs more data than synthetic generation provides confidently. |
| K-Nearest Neighbors | Fine, but no clear advantage over RF; less standard for this use case. |

### Dataset: **Synthetic generation**

We don't have real user quiz data, so we generate it programmatically.

**Generator** (`backend/ml/classifier/data_generation.py`):
```python
def generate_synthetic_data(n=10_000, seed=42):
    """Generate synthetic samples with rule-based labels + noise."""
    rng = np.random.default_rng(seed)
    X, y = [], []
    for _ in range(n):
        # Sample features uniformly across realistic ranges
        score = rng.uniform(0, 100)
        time = rng.uniform(60, 1800)  # 1-30 min
        wrong = rng.integers(0, 11)
        unans = rng.integers(0, 6)

        # Apply rule-based labeling (PRD.md §15) with noise
        baseline = "low"
        if score >= 80 and time <= 5 * 90:  # 5 questions × 90s
            baseline = "high"
        elif score >= 50:
            baseline = "medium"

        # Inject 5% label noise to prevent perfect overfitting
        if rng.random() < 0.05:
            other_labels = [l for l in ["high", "medium", "low"] if l != baseline]
            baseline = rng.choice(other_labels)

        X.append([score, time, wrong, unans])
        y.append(baseline)
    return np.array(X), np.array(y)
```

**Why noise injection?**
- Without noise, model achieves 100% accuracy → indistinguishable from the rule itself → no ML value.
- 5% noise simulates real-world ambiguity (border cases, occasional unusual patterns).
- After training, model should achieve ~93-97% accuracy (close but not perfect).

**Sample size**: 10,000 is plenty for tabular RF. Training takes <30s.

### Training procedure

**Where**: local CPU (no GPU needed). See `backend/ml/classifier/train.py`.

```bash
cd backend
source .venv/bin/activate
python -m ml.classifier.train
```

**Pipeline**:
1. Generate 10k samples
2. Split 80/20 train/test
3. Fit `RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)`
4. Evaluate on test set: accuracy, confusion matrix, classification report
5. Save model: `joblib.dump(model, "ml/classifier/artifacts/classifier.pkl")`
6. Print feature importances

**Expected output**:
```
Test accuracy: 94.2%
Classification report:
              precision    recall  f1-score
        high      0.96      0.94      0.95
      medium      0.92      0.94      0.93
         low      0.95      0.95      0.95

Feature importances:
  score_percentage:    0.51
  time_taken_seconds:  0.28
  wrong_count:         0.13
  unanswered_count:    0.08
```

### Inference at runtime

**Hardware**: backend CPU.

**Latency**: <10ms per prediction. Negligible.

**Loading**: model loads at module import (~50ms). Cached for app lifetime.

```python
# backend/ml/classifier/inference.py
import joblib
from pathlib import Path

_ARTIFACT = Path(__file__).parent / "artifacts" / "classifier.pkl"
_model = joblib.load(_ARTIFACT)

def predict(features: list[float]) -> str:
    return _model.predict([features])[0]  # "high" | "medium" | "low"
```

### Quality metrics

Track in training script output:
- **Test accuracy**: target ≥ 85% (with noise injection making 100% impossible).
- **Per-class F1 score**: avoid imbalance; target ≥ 0.85 for each class.
- **Feature importance**: sanity check — `score_percentage` should be most important.
- **Confusion matrix**: errors should be between adjacent classes (high↔medium or medium↔low), not high↔low.

### Fallback

If `classifier.pkl` is missing or fails to load, `inference.py` falls back to the existing rule-based classifier (already scaffolded). Log a warning. Demo still works.

---

## 5. Why NOT use ML for insight/recommendation?

**The temptation**: use a generative model (T5, GPT) to produce personalized insights and recommendations.

**Why we don't**:
1. **Brand voice consistency**: `BRAND.md` §6 specifies a careful tone (calm, honest, "kamu" not "Anda", no patronizing). Generative models drift.
2. **Quality control**: with ~6-8 sub-conditions per engine and 3 levels, we can curate ~24 high-quality output strings manually. Far better than uncertain LLM output.
3. **Speed**: template lookup is microseconds; generation is seconds.
4. **Reliability**: no risk of hallucinated medical/educational advice.
5. **MVP scope**: ML is already added in 2 places (QG + classification). Adding a 3rd is over-engineered.

**If the team wants more ML coverage**: Ariq can add TF-IDF + topic clustering in evaluator (per-topic score breakdown). That's a cleaner addition than generative insight.

---

## 6. Deployment & DevOps

### Local development

**For Audry (training DL)**:
1. Open `backend/ml/generator/notebooks/train_quiz_generator.ipynb` in Google Colab
2. Connect to T4 GPU runtime
3. Run all cells (auto-downloads dataset, trains, pushes to HF Hub)
4. ~1-2 hours

**For Desta (training ML)**:
1. From `backend/`, activate venv
2. `pip install -r ml/requirements-ml.txt` (one-time, includes scikit-learn — already in `requirements.txt`)
3. `python -m ml.classifier.train`
4. Verify `ml/classifier/artifacts/classifier.pkl` is created
5. Commit the `.pkl` file (small, < 5MB)

**For everyone (running app with ML)**:
1. `pip install -r requirements.txt` (includes inference deps: `transformers`, `torch`, `scikit-learn`)
2. `uvicorn app.main:app --reload`
3. First request: backend downloads IndoT5 from HF Hub (~1GB, one-time per machine)
4. Subsequent requests: model cached, fast load

### Storage strategy

| Artifact | Size | Storage |
|---|---|---|
| Fine-tuned IndoT5 model | ~1 GB | Hugging Face Hub (free, public) |
| sklearn `.pkl` classifier | < 5 MB | Committed to git |
| TyDiQA-id dataset | ~30 MB | Auto-downloaded by HF `datasets` library, cached locally |
| Synthetic dataset | ~5 MB (memory only) | Re-generated on each `train.py` run; not stored |

### CI/CD considerations (post-MVP)

For now, no CI runs ML training. Manual training, manual artifact commit. Acceptable for capstone scope.

If the project moves to production later:
- Cache HF model in CI for faster builds
- Run sklearn re-training as part of CI when synthetic data generator changes
- Track model versions explicitly

---

## 7. Performance Expectations

### Quiz generation (DL inference, CPU)

| Scenario | Time |
|---|---|
| Cold start (first request after server boot) | 25-50s (includes model load) |
| Warm inference (5 questions) | 15-40s |
| Best case (4-core 3GHz CPU) | 12-20s |
| Worst case (older CPU) | 30-60s |

**UX implication**: Frontend MUST show loading state with progress messages (per BRAND.md §7.3 "Sedang menyusun pertanyaan..."). Demo should warm up the model before the demo starts.

### Understanding classification (ML inference, CPU)

| Scenario | Time |
|---|---|
| Inference per request | < 10ms |

**UX implication**: imperceptible. No loading state needed.

---

## 8. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Audry struggles with Hugging Face / Colab | Ravi can support; documentation + colab notebook template provided |
| TyDiQA-id fine-tuning produces poor results | Try smaller learning rate, more epochs. Last resort: skip fine-tuning, use pretrained directly with prompt engineering. |
| HF Hub model fails to load at runtime (network/auth) | Rule-based fallback already scaffolded; demo still works |
| Sklearn classifier overfits perfectly to synthetic data | Noise injection (5%) prevents this; verify accuracy is 90-97%, not 100% |
| Demo with cold model = 30s+ wait at first quiz | Warm up model before demo starts: `curl localhost:8000/health` then trigger one quiz generate |
| Inference too slow on demo machine | Pre-generate quiz for 1-2 demo materials and cache; fall through to live for 3rd |

---

## 9. Sign-off

This ML strategy requires sign-off from the team before implementation begins.

- [ ] **Audry** — Hugging Face workflow understood; comfortable with Colab notebook
- [ ] **Ariq** — knows how `EvaluationResult` features feed into Desta's classifier
- [ ] **Desta** — synthetic data generation strategy is clear; sklearn approach acceptable
- [ ] **Ravi** — frontend loading state will accommodate 15-40s wait

---

## Changelog

- **v1.0 (2026-05-06)** — Initial ML/DL strategy: hybrid (DL for quiz gen via fine-tuned IndoT5 on Colab + Hugging Face Hub; ML conv for classifier via sklearn Random Forest with synthetic data). Insight/recommendation remain template-based.
