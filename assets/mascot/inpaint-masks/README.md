# Asahi expression set — inpaint recipe

Goal: produce Asahi's expression variants **without breaking consistency**. The trick is
to change **only the eyes/mouth** and keep everything else (hair, face shape, shirt,
background) byte-for-byte identical. Inpainting with a tight mask does exactly that.

> Why this works where the old approach failed: re-generating the *whole* image per
> expression drifts the face — she looks like a different person each time. Masked
> inpaint freezes the character and only repaints the small region you allow.

## Two methods

1. **Face-swap inpaint** (cheap, perfectly consistent) — for pure facial expressions
   (`high`, `low`): mask only brows + mouth on `../asahi-base-full.png`, eyes protected.
   Inherently front-facing because it reuses the base.
2. **Gesture pose via SeaArt "Maintain Character Consistency"** — for hand gestures
   (`wave`, `think`): generate a new pose from the base as reference. Costs ~41 credits,
   produces brighter colors (tone-match on cutout with `-modulate 101,80`).

> **ALL poses must be FRONT-FACING.** The consistency app tends to tilt the head / use a
> 3/4 angle. Always include: `facing forward toward the viewer, head straight and centered,
> looking directly at the viewer, front view, symmetrical composition`. This keeps the whole
> set uniform with the front-facing base.

## Files here

| File | Purpose |
|---|---|
| `brush-guide.png` | the full-hair base with the **brows + mouth** regions tinted — replicate this brush in SeaArt (leave the eyes alone) |

SeaArt uses a brush, not an uploaded mask, so just paint the tinted regions from
`brush-guide.png`. (Earlier fixed mask PNGs were removed when the base was re-rendered.)

## Source image

- **Expression source (opaque):** `../asahi-base-full.png` (1536×1464) — the full-hair
  render. Inpaint expressions on THIS, then cut out the background afterwards.
- **App base (transparent):** `../asahi-base-transparent.png` = `frontend/public/mascot/asahi-base.png`.
  This is the **`mid`** mood (warm neutral smile) — no inpaint needed for it.
- The original cropped v1 art is kept as `../asahi-base.png` for reference only.

## What to make

Four variants, inpainted on `asahi-base-full.png` (mask = **brows + mouth only**, eyes
protected). After each, the background gets cut out (rembg, done locally) and the result
saved into **`frontend/public/mascot/`** with these exact names — the `Asahi` component
already points at them:

| File | Mood | Expression |
|---|---|---|
| `asahi-high.png` | high score | proud, bright open smile |
| `asahi-low.png`  | low score  | gentle, kind, slightly concerned (never pitying/crying) |
| `asahi-think.png`| loading/thinking | focused, glancing up |
| `asahi-wave.png` | greeting / empty state | cheerful, playful wink |

(`asahi-base.png` already covers `mid`.)

## LOCKED RECIPE (validated 2026-06-12)

Key lesson from the first calibration pass: **do NOT mask the eyes.** Letting the model
repaint the eyes drifts their color (base emerald → lime/sparkle). Instead mask only the
**eyebrows + mouth** and leave the eyes untouched — every expression then keeps the exact
base emerald eyes, and emotion comes from the mouth + brows. Eye-related prompt tags are
therefore dropped from the per-expression additions.

- Model: **Soft Glow Anime** (Illustrious) or similar soft Illustrious checkpoint.
- Mask: **eyebrows + mouth only** (eyes left unpainted).
- Denoise / redraw strength: **0.5** (→ 0.55 if change too subtle, → 0.45 if it drifts).
- Euler a · Steps 30 · CFG 5 · Clip skip 2 · Restore Faces OFF · 2:3 (1024×1536).

## Prompts

**Base tags** (keep on every expression so the style/character hold — same as BRAND.md §12):

```
masterpiece, best quality, 1girl, solo, long cream hair with mint-green gradient tips,
emerald green eyes, white collared shirt, emerald necktie, green chevron hairclip,
soft cel shading, clean lineart, bright soft lighting, pastel palette, upper body
```

**Per-expression addition** (append to the base tags — mouth/brow only, eyes are protected):

- **high** → `proud confident expression, open happy smile showing slight teeth, relaxed eyebrows, faint blush, joyful`
- **low** → `gentle reassuring soft small smile, slightly raised worried inner eyebrows, soft caring expression`
- **think** → `thoughtful focused expression, closed mouth slight pout, one raised eyebrow, curious look`
- **wave** → `cheerful friendly big open smile, both eyebrows raised happily, greeting, bright and welcoming`

**Negative** (all):

```
lowres, bad anatomy, asymmetric eyes, extra eyes, deformed, blurry, jpeg artifacts,
different character, off-model, inconsistent style, watermark, text, signature, crying, tears, frown
```

## Settings (Automatic1111 / Forge / reForge — "Inpaint")

- Model: an **anime SDXL** close to the base style — Illustrious-XL or Animagine-XL
  (BRAND.md §12). Matching the base model is what keeps the lineart/shading seamless.
- Upload `../asahi-base-full.png`, then mask the **brows + mouth** region (see
  `brush-guide.png`) — leave the eyes unpainted.
- **Inpaint area: Only masked**
- **Masked content: original**
- **Denoising strength: 0.5** (raise toward 0.65 if the change is too timid; lower toward
  0.4 if it drifts off-model)
- Mask blur: 6 · Steps: 28 · CFG: 6–7 · same sampler you used for the base
- Seed: keep fixed across the four so the repaints feel like one set.

### ComfyUI
Use a "VAE Encode (for Inpaint)" + "Set Latent Noise Mask" with the same mask and a
0.5 denoise; rest as above.

### Krita (AI Diffusion plugin) or fully manual
Open the base at 1024×1536, select the masked region (or just paint on a new layer inside
it), repaint the eyes/mouth in the same clean-lineart style, flatten, export. Because the
shapes are simple and the region is tiny, a careful manual edit in Krita/Photopea works
without any AI.

## SeaArt AI (free) — step by step

SeaArt's inpaint uses a **brush** (you paint the region) rather than an uploaded mask, so
use `brush-guide.png` as the reference for exactly where to paint.

1. **Create → Inpaint** (or open the image editor and pick the Inpaint / Partial Redraw tool).
2. **Upload** `asahi-base.png`. Keep the canvas at **1024×1536** — don't crop or resize.
3. **Model**: pick an anime SDXL checkpoint — *Illustrious-XL*, *NoobAI-XL*, or *Animagine-XL*.
   (Style won't be a perfect match to the original render, but low denoise + only-masked hides the seam.)
4. **Brush the mask**: paint over the **eyebrows** and the **mouth** only — **leave the eyes
   unpainted** (see LOCKED RECIPE above; painting the eyes drifts their color). Use a soft brush.
5. **Prompt**: paste the base tags + the per-expression addition (below). Paste the negative.
6. **Settings**: Denoising / Redraw strength **≈ 0.5**, "Inpaint area = only masked",
   "Masked content = original" (SeaArt may label these "Partial redraw" / "Keep original").
   Steps 28, CFG 6–7.
7. **Generate** 4 candidates, pick the most on-model, **download** the full 1024×1536 PNG.
8. Repeat for each expression. Save into `frontend/public/mascot/` as `asahi-high.png`,
   `asahi-low.png`, `asahi-think.png`, `asahi-wave.png`.

Tip: do `high` first as a calibration — if the eyes/mouth barely change, raise denoise to
0.6; if her face drifts off-model, drop to 0.4.

## Verify alignment

After exporting, diff against the base — only the masked area should differ:

```bash
# from assets/mascot/
compare -metric AE asahi-base.png ../../frontend/public/mascot/asahi-high.png diff.png
# the highlighted pixels should sit only inside the eyes/mouth region
```

If pixels changed outside the mask, the inpaint tool re-encoded the whole image — switch
"Inpaint area" to **Only masked** and "Masked content" to **original**.
