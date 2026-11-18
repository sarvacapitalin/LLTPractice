import re
import json
from scripts.test_stream_tokens import get_row_stream

def segment_all(category_name, pdf_path, cmap_id, total_count):
    tokens = get_row_stream(pdf_path, cmap_id, category_name)
    n = len(tokens)
    
    questions = {}
    current_q = 1
    i = 0
    
    def is_q_start(idx, target_q):
        if idx >= n: return False
        p, x, y, t = tokens[idx]
        m = re.match(r'^' + str(target_q) + r'(?:\b|[A-Za-z])', t)
        if not m: return False
        rem = t[len(str(target_q)):].strip()
        if rem and re.search(r'[A-Za-z]', rem):
            return True
        if idx + 1 < n:
            next_t = tokens[idx + 1][3]
            if len(re.findall(r'[A-Za-z]', next_t)) >= 3:
                return True
        return False
        
    while i < n and current_q <= total_count:
        if is_q_start(i, current_q):
            p, x, y, t = tokens[i]
            q_toks = []
            rem = t[len(str(current_q)):].strip()
            if rem:
                q_toks.append((x, y, rem))
            j = i + 1
            target_next = current_q + 1
            while j < n:
                if target_next <= total_count and is_q_start(j, target_next):
                    break
                pj, xj, yj, tj = tokens[j]
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
