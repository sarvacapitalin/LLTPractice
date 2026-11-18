from scripts.test_cell_extractor import extract_pdf_cells
import json

def extract_all_questions_robust(pdf_path, cid, total, missing_starts=None):
    if missing_starts is None:
        missing_starts = {}
    pages = extract_pdf_cells(pdf_path, cid)
    
    # First, flatten elements with page numbers
    all_elements = []
    for p_num, elems in pages:
        # filter table headers
        for x, y, c_idx, t in elems:
            t_s = t.strip()
            if p_num == 1 and t_s in ['12', '34567', 'S.NO.', 'QUESTIONS', 'RELEVANT FIGURE/SIGN', 'IF ANY', 'OPTION1', 'OPTION2', 'OPTION3', 'OPTION4', 'ANSWER', 'OPTION', 'S']:
                continue
            all_elements.append((p_num, x, y, c_idx, t_s))
            
    # Now find each question's bounding tokens
    # A question starts with its S.NO at 70 <= y <= 95 and c_idx == 0
    # or if in missing_starts, text starts with missing_starts[q]
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
                
    print(f'[{pdf_path}] Identified {len(q_ranges)} / {total} question boundaries.')
    
    parsed_questions = {}
    for idx in range(len(q_ranges)):
        q_num, start_idx = q_ranges[idx]
        end_idx = q_ranges[idx+1][1] if idx + 1 < len(q_ranges) else len(all_elements)
        q_tokens = all_elements[start_idx:end_idx]
        
        # Analyze q_tokens
        # Look for answer token:
        # In the table, Answer Option is 1, 2, 3, or 4.
        # It usually has y >= 680 or is the last token in a row, or matches a single digit 1-4.
        answers = []
        for p, x, y, c_idx, t in q_tokens:
            if y >= 680 and t in ['1', '2', '3', '4']:
                answers.append((y, t))
            elif c_idx > 0 and t in ['1', '2', '3', '4']:
                answers.append((y, t))
                
        # Also check last token in q_tokens
        last_t = q_tokens[-1][4]
        if last_t in ['1', '2', '3', '4']:
            answers.append((q_tokens[-1][2], last_t))
            
        parsed_questions[q_num] = {
            'tokens': q_tokens,
            'answers_found': answers
        }
        
    return parsed_questions

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
        pq = extract_all_questions_robust(name, cid, total, missing)
        no_ans = [q for q, data in pq.items() if not data['answers_found']]
        print(f'{name}: Questions without answers found: {len(no_ans)} -> {no_ans[:10]}')
