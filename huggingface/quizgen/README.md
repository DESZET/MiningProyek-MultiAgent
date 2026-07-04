---
title: Asahlagi Quiz Generator
emoji: 🎯
colorFrom: green
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Indonesian quiz generator (Asahlagi TP-G005)
---

# Asahlagi Quiz Generator (HF Space)

FastAPI service that generates multiple-choice quiz questions from Indonesian learning material using `Wikidepia/IndoT5-base`.

This Space is the cloud-hosted DL inference layer for the [Asahlagi capstone project](https://github.com/ravi-arnan/TempaCapstoneProject).

## Endpoints

### `GET /`
Health check.

```json
{
  "service": "asahlagi-quizgen",
  "model": "Wikidepia/IndoT5-base",
  "status": "ready"
}
```

### `POST /generate`
Generate quiz from material text.

**Request:**
```json
{
  "material_text": "Fotosintesis adalah proses pembentukan glukosa..."
}
```

**Response:**
```json
{
  "questions": [
    {
      "question": "Apa itu fotosintesis?",
      "options": ["...", "...", "...", "..."],
      "correct_option_index": 2
    }
  ]
}
```

Material must be 100-20,000 characters. Returns 3-5 questions.

## How this works

This Space runs `Wikidepia/IndoT5-base` (220M parameter Indonesian T5 transformer) on Hugging Face's CPU infrastructure (free tier). Model loads once at startup; subsequent requests use the cached model.

The Asahlagi backend (run locally by the team) calls this Space's `/generate` endpoint instead of running inference locally. If the Space is unreachable, the backend falls back to local CPU inference, then to rule-based generation.

## Notes

- **Free tier CPU**: ~6-15s per quiz (5 questions). For faster inference, can be upgraded to GPU at $0.60/hour.
- **Sleep policy**: free Spaces sleep after 48h of no traffic. Wake-up takes ~30-60s on next request.
- **Pre-demo warm-up**: hit `/` endpoint 5-10 minutes before any demo to ensure Space is awake.

## Project context

This is part of TP-G005's capstone project for the **Tempa** learning program.

Brand: [Asahlagi](https://github.com/ravi-arnan/TempaCapstoneProject) — *Asah lagi sampai paham.*
