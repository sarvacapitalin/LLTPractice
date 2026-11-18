from scripts.test_cell_extractor import extract_pdf_cells
import json

def get_official_pdf_answers(pdf_path, cid, total, missing_starts=None):
    if missing_starts is None:
        missing_starts = {}
    pages = extract_pdf_cells(pdf_path, cid)
    
    all_elements = []
    for p_num, elems in pages:
        for x, y, c_idx, t in elems:
            t_s = t.strip()
            if p_num == 1 and t_s in ['12', '34567', 'S.NO.', 'QUESTIONS', 'RELEVANT FIGURE/SIGN', 'IF ANY', 'OPTION1', 'OPTION2', 'OPTION3', 'OPTION4', 'ANSWER', 'OPTION', 'S']:
                continue
            all_elements.append((p_num, x, y, c_idx, t_s))
            
    q_ranges = []
    current_q = 1
    for i, (p_num, x, y, c_idx, t_s) in enumerate(all_elements):
        matched = False
        if 70 <= y <= 95 and c_idx == 0 and t_s == str(current_q):
            matched = True
        elif current_q in missing_starts and t_s.startswith(missing_starts[current_q]):
            matched = True
            
        if matched:
            q_ranges.append((current_q, i))
            current_q += 1
            if current_q > total:
                break
                
    answers = {}
    details = {}
    for idx in range(len(q_ranges)):
        q_num, start_idx = q_ranges[idx]
        end_idx = q_ranges[idx+1][1] if idx + 1 < len(q_ranges) else len(all_elements)
        q_tokens = all_elements[start_idx:end_idx]
        
        # Look for tokens in column 7 (y >= 680)
        col7_tokens = [t for p, x, y, c_idx, t in q_tokens if y >= 680 and t in ['1', '2', '3', '4']]
        
        # Look for multi-cell c_idx tokens where the token is the last chunk
        chunk_answers = []
        for p, x, y, c_idx, t in q_tokens:
            if c_idx > 0 and t in ['1', '2', '3', '4']:
                chunk_answers.append(t)
                
        # Last token
        last_tok = q_tokens[-1][4]
        
        chosen_ans = None
        if col7_tokens:
            chosen_ans = int(col7_tokens[-1])
        elif chunk_answers:
            chosen_ans = int(chunk_answers[-1])
        elif last_tok in ['1', '2', '3', '4']:
            chosen_ans = int(last_tok)
        else:
            # Fallback scan from end of q_tokens
            for p, x, y, c_idx, t in reversed(q_tokens):
                if t in ['1', '2', '3', '4']:
                    chosen_ans = int(t)
                    break
                    
        answers[q_num] = chosen_ans
        details[q_num] = {
            'col7': col7_tokens,
            'chunk': chunk_answers,
            'last': last_tok,
            'chosen': chosen_ans,
            'tokens': [(y, c_idx, t) for p, x, y, c_idx, t in q_tokens]
        }
        
    return answers, details

if __name__ == '__main__':
    for name, cid, total, missing in [
        ('road-signs-english.pdf', 299, 94, {}),
        ('rules-of-road-regulations-english.pdf', 180, 159, {}),
        ('general-driving-principles-english.pdf', 128, 159, {
            32: "THE MOST EFFECTIVE DEVICE FOR",
            128: "WHAT WILL HAPPEN IF THE WHEELS",
            144: "ALCOHOL MAY AFFECT ADVERSELY",
            150: "BOARDING AND ALIGHTING WHILE"
        })
    ]:
        ans, det = get_official_pdf_answers(name, cid, total, missing)
        print(f'{name}: Extracted answers for {len(ans)} questions.')
        none_count = sum(1 for v in ans.values() if v is None)
        print(f'  None answers: {none_count}')
        # print first 10 answers
        first_10 = {k: ans[k] for k in range(1, 11)}
        print(f'  First 10: {first_10}')
