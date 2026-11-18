import re
import json
from scripts.test_stream_tokens import get_row_stream

def segment_all(category_name, pdf_path, cmap_id, total_count):
    tokens = get_row_stream(pdf_path, cmap_id, category_name)
    
    questions = {}
    current_q = 1
    i = 0
    n = len(tokens)
    
    def matches_q(tj, num):
        # Match number at start
        m = re.match(r'^' + str(num) + r'(?:\b|[A-Za-z])', tj)
        return bool(m)
    
    while i < n and current_q <= total_count:
        p, x, y, t = tokens[i]
        if matches_q(t, current_q):
            q_toks = []
            rem = t[len(str(current_q)):].strip()
            if rem:
                q_toks.append((x, y, rem))
            j = i + 1
            target_next = current_q + 1
            while j < n:
                pj, xj, yj, tj = tokens[j]
                if target_next <= total_count and matches_q(tj, target_next):
                    # Check if this token is actually target_next question number or an answer
                    # If target_next <= 4, is it an answer?
                    # An answer token is followed by another question number or is preceded by 4 options
                    # If target_next <= 4, check if xj < 200 (question number column) or if it's accompanied by text
                    if target_next <= 4 and tj in ['1', '2', '3', '4'] and xj > 250:
                        q_toks.append((xj, yj, tj))
                        j += 1
                        continue
                    break
                # Ignore road signs drop-shadow duplicates
                if category_name == 'road_signs' and tj == str(current_q) and xj < 200:
                    break
                q_toks.append((xj, yj, tj))
                j += 1
            questions[current_q] = (p, q_toks)
            current_q += 1
            i = j - 1
        i += 1
        
    return questions

if __name__ == '__main__':
    for cat, pdf, cid, total in [
        ('road_signs', 'road-signs-english.pdf', 299, 94),
        ('rules_of_road', 'rules-of-road-regulations-english.pdf', 180, 159),
        ('general_principles', 'general-driving-principles-english.pdf', 128, 159)
    ]:
        qs = segment_all(cat, pdf, cid, total)
        print(f"[{cat}] Successfully segmented: {len(qs)} / {total}")
        # Check answer detection
        valid_ans = 0
        for q, (p, toks) in qs.items():
            ans = None
            for x, y, t in reversed(toks):
                if t.strip() in ['1', '2', '3', '4']:
                    ans = int(t.strip())
                    break
                m = re.search(r'(\d)$', t.strip())
                if m and m.group(1) in ['1', '2', '3', '4']:
                    ans = int(m.group(1))
                    break
            if ans is not None:
                valid_ans += 1
            else:
                print(f"  Missing ans for Q{q} in {cat}: {[t for _,_,t in toks]}")
        print(f"[{cat}] Questions with valid answer: {valid_ans} / {total}")
