import re
import json
from scripts.test_stream_tokens import get_row_stream

def get_segmented_questions(cat, pdf, cid, total):
    tokens = get_row_stream(pdf, cid, cat)
    n = len(tokens)
    
    def is_q_start(idx, target_q):
        if idx >= n: return False
        p, x, y, t = tokens[idx]
        m = re.match(r'^' + str(target_q) + r'(?:\b|[A-Za-z])', t)
        if not m: return False
        rem = t[len(str(target_q)):].strip()
        if rem and re.search(r'[A-Za-z]', rem): return True
        if idx + 1 < n:
            next_t = tokens[idx + 1][3]
            if len(re.findall(r'[A-Za-z]', next_t)) >= 3: return True
        return False
        
    questions = {}
    current_q = 1
    i = 0
    while i < n and current_q <= total:
        if is_q_start(i, current_q):
            p, x, y, t = tokens[i]
            q_toks = []
            rem = t[len(str(current_q)):].strip()
            if rem: q_toks.append((x, y, rem))
            j = i + 1
            target_next = current_q + 1
            while j < n:
                if target_next <= total and is_q_start(j, target_next): break
                pj, xj, yj, tj = tokens[j]
                if cat == 'road_signs' and tj == str(current_q) and xj < 200: break
                q_toks.append((xj, yj, tj))
                j += 1
            questions[current_q] = (p, q_toks)
            current_q += 1
            i = j - 1
        i += 1
    return questions

def extract_qa(q_num, p, toks, cat):
    # Find answerIndex
    ans_digit = None
    ans_tok_idx = None
    for idx in range(len(toks)-1, -1, -1):
        x, y, t = toks[idx]
        t_clean = t.strip()
        if t_clean in ['1', '2', '3', '4']:
            ans_digit = int(t_clean)
            ans_tok_idx = idx
            break
        m = re.search(r'(\d)$', t_clean)
        if m and m.group(1) in ['1', '2', '3', '4']:
            ans_digit = int(m.group(1))
            ans_tok_idx = idx
            break
            
    assert ans_digit is not None, f"No answer found for Q{q_num} in {cat}"
    ans_idx = ans_digit - 1
    
    content = toks[:ans_tok_idx] if ans_tok_idx is not None else toks
    
    # Separate question text from options
    # In Rules and Principles, find '0' placeholder if present
    zero_idx = None
    for idx, (x, y, t) in enumerate(content):
        if t.strip() == '0':
            zero_idx = idx
            break
            
    if zero_idx is not None:
        q_tokens = content[:zero_idx]
        opt_tokens = content[zero_idx+1:]
    else:
        # If no '0', question tokens are up to when options start
        # Check coordinates or heuristics
        if cat == 'road_signs':
            # For road signs, question is usually first 1-3 tokens
            # or tokens with x < 0 or y < 350
            if len(content) > 4:
                # check where options start
                opt_start = 1
                while opt_start < len(content) - 4 and any(w in content[opt_start][2] for w in ['WHAT', 'MEAN', 'LIGHT', 'SIGN', 'TRIANGLE', 'CIRCLE', 'INDICATES', 'REPRESENT', 'MEANS', 'ARE..', 'STREET.', 'ROAD']):
                    opt_start += 1
                q_tokens = content[:opt_start]
                opt_tokens = content[opt_start:]
            else:
                q_tokens = [content[0]]
                opt_tokens = content[1:]
        else:
            q_tokens = [content[0]]
            opt_tokens = content[1:]
            
    q_text = " ".join(t.strip() for _, _, t in q_tokens if t.strip()).strip()
    return q_text, opt_tokens, ans_idx

if __name__ == '__main__':
    for cat, pdf, cid, total in [
        ('road_signs', 'road-signs-english.pdf', 299, 94),
        ('rules_of_road', 'rules-of-road-regulations-english.pdf', 180, 159),
        ('general_principles', 'general-driving-principles-english.pdf', 128, 159)
    ]:
        qs = get_segmented_questions(cat, pdf, cid, total)
        print(f"[{cat}] Processed {len(qs)}/{total}")
        for q in [1, 2, 10, total]:
            p, toks = qs[q]
            q_text, opt_toks, ans_idx = extract_qa(q, p, toks, cat)
            print(f"  Q{q}: Text='{q_text[:40]}...' OptToksCount={len(opt_toks)} AnsIdx={ans_idx}")
