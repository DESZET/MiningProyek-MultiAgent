"""Shared utility for distractor generation."""

import difflib

def _pick_similar_length_distractors(correct: str, pool: list[str], n: int = 3) -> list[str]:
    """Pick distractors with similar length to correct answer but ensure they aren't too similar string-wise."""
    target_len = len(correct)
    
    common_suffixes = ('nya', 'kan', 'i', 'an', 'ku', 'mu')
    common_prefixes = ('me', 'pe', 'di', 'ter', 'ke', 'se', 'ber')
    
    def get_affixes(word):
        w = word.lower()
        pref = next((p for p in common_prefixes if w.startswith(p)), '')
        suff = next((s for s in common_suffixes if w.endswith(s)), '')
        return pref, suff

    correct_pref, correct_suff = get_affixes(correct)
    is_capitalized = correct[0].isupper() if correct else False
    
    def score_candidate(cand):
        score = abs(len(cand) - target_len) * 2
        cand_pref, cand_suff = get_affixes(cand)
        if correct_pref and cand_pref != correct_pref:
            score += 3
        if correct_suff and cand_suff != correct_suff:
            score += 3
        return score

    # Sort candidates by heuristic score
    candidates = sorted(
        [w for w in pool if w.lower() != correct.lower()],
        key=score_candidate
    )
    
    selected = []
    for cand in candidates:
        # Avoid highly similar words (e.g., plurals/singulars like 'proses' vs 'prosesnya')
        similarity = difflib.SequenceMatcher(None, correct.lower(), cand.lower()).ratio()
        if similarity < 0.8:
            if is_capitalized and cand and cand[0].islower():
                cand = cand[0].upper() + cand[1:]
            elif not is_capitalized and cand and cand[0].isupper():
                cand = cand[0].lower() + cand[1:]
            
            if not any(cand.lower() == s.lower() for s in selected):
                selected.append(cand)
                
        if len(selected) == n:
            break
            
    # Fallback if not enough distinct candidates found
    for cand in candidates:
        if len(selected) == n:
            break
        if is_capitalized and cand and cand[0].islower():
            cand = cand[0].upper() + cand[1:]
        elif not is_capitalized and cand and cand[0].isupper():
            cand = cand[0].lower() + cand[1:]
            
        if not any(cand.lower() == s.lower() for s in selected):
            selected.append(cand)
            
    return selected
