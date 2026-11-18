import os, sys, re, json
from scripts.test_robust_extractor import decode_stream_robust
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, get_page_contents
from scripts.verify_answers import get_official_pdf_answers

def test_full_extraction(cat, pdf, cid, total, header_len):
    with open(pdf, 'rb') as f:
        pdf_bytes = f.read()
    cmap = parse_cmap(get_obj_stream(pdf_bytes, cid))
    pages = get_page_contents(pdf_bytes)
    
    all_elems = []
    for p_idx, (p_id, c_id) in enumerate(pages):
        raw_elems = decode_stream_robust(get_obj_stream(pdf_bytes, c_id), cmap)
        cur_elems = raw_elems[header_len:] if p_idx == 0 else raw_elems
        for x, y, t in cur_elems:
            all_elems.append((p_idx + 1, x, y, t.strip()))
            
    header_words = {'S.NO.', 'QUESTIONS', 'RELEVANT FIGURE/SIGN', 'OPTION1', 'OPTION2', 'OPTION3', 'OPTION4', 'ANSWER', 'S.NO.QUESTIONS', 'OPTION1OPTION2OPTION3OPTION4', 'ANSWER ', 'IF ANY', 'RELEVANT', 'FIGURE/SIGN', 'S'}
    filtered = [e for e in all_elems if e[3] and e[3] not in header_words]
    
    q_ranges = {}
    current_q = 1
    for i, (p, x, y, t) in enumerate(filtered):
        m = re.match(r'^(\d{1,3})$', t)
        if m and int(m.group(1)) == current_q:
            q_ranges[current_q] = i
            current_q += 1
            if current_q > total: break
        elif t.startswith(str(current_q)) and len(t) > len(str(current_q)):
            q_ranges[current_q] = i
            current_q += 1
            if current_q > total: break
            
    official_ans, _ = get_official_pdf_answers(pdf, cid, total, {
        32: "THE MOST EFFECTIVE",
        128: "WHAT WILL HAPPEN",
        144: "ALCOHOL MAY AFFECT",
        150: "BOARDING AND ALIGHTING"
    })
    
    extracted = []
    issues = []
    for q in range(1, total + 1):
        start_idx = q_ranges[q]
        end_idx = q_ranges[q+1] if q+1 in q_ranges else len(filtered)
        toks = filtered[start_idx:end_idx]
        
        # Remove S.No from start
        first_t = toks[0][3]
        m = re.match(r'^' + str(q) + r'(.*)$', first_t)
        if m and m.group(1).strip():
            content_toks = [(toks[0][1], toks[0][2], m.group(1).strip())] + [(t[1], t[2], t[3]) for t in toks[1:]]
        else:
            content_toks = [(t[1], t[2], t[3]) for t in toks[1:]]
            
        # Check answer token at end
        if content_toks and content_toks[-1][2] in ['1', '2', '3', '4']:
            content_toks = content_toks[:-1]
        elif content_toks and re.search(r'[1-4]$', content_toks[-1][2]):
            t_last = content_toks[-1][2]
            content_toks[-1] = (content_toks[-1][0], content_toks[-1][1], t_last[:-1].strip())
            
        # Filter '0' placeholder
        content_toks = [t for t in content_toks if t[2] != '0']
        
        # Separate Question text vs Options
        # Notice: In the PDF, question text tokens always come before the options.
        # How do we know where options start?
        # In Rules: If scenario figure present, options are at x >= 550.
        # If no scenario figure, options start at x >= 340 (or x >= 270 in GP).
        # But wait! On page 1, x coordinates are negative!
        # On Page 1:
        # Question text is at x < 0.
        # Options are at x > 0!
        p_num = toks[0][0]
        if p_num == 1:
            q_part = [t[2] for t in content_toks if t[0] < 0]
            opt_part = [t for t in content_toks if t[0] >= 0]
        else:
            # For pages >= 2:
            # Check if this question row has options starting at ~550 (figure present)
            # or ~350 (no figure in Rules), or ~270 (in GP)
            if cat == 'rules_of_road':
                # If there are tokens with 340 <= x <= 450, they are Option 1!
                # Unless they are question tokens. But question tokens have x <= 140!
                q_part = [t[2] for t in content_toks if t[0] < 250]
                opt_part = [t for t in content_toks if t[0] >= 250]
            else: # general_principles
                q_part = [t[2] for t in content_toks if t[0] < 250]
                opt_part = [t for t in content_toks if t[0] >= 250]
                
        q_text = " ".join(q_part).strip()
        q_text = re.sub(r"\s+", " ", q_text)
        
        # Cluster options
        if not opt_part:
            opts = ["", "", "", ""]
        elif len(opt_part) == 4:
            opts = [t[2] for t in opt_part]
        else:
            min_x = min(t[0] for t in opt_part)
            max_x = max(t[0] for t in opt_part)
            span = max_x - min_x
            if span < 30:
                k = len(opt_part)
                step = k / 4.0
                opts = [" ".join(opt_part[int(round(i*step)):int(round((i+1)*step))][j][2] for j in range(len(opt_part[int(round(i*step)):int(round((i+1)*step))]))) for i in range(4)]
            else:
                bins = [[], [], [], []]
                for x, y, t in opt_part:
                    col = int(round((x - min_x) / (span / 3.0)))
                    col = max(0, min(3, col))
                    bins[col].append(t)
                opts = [" ".join(b).strip() for b in bins]
                if any(len(o) == 0 for o in opts):
                    k = len(opt_part)
                    step = k / 4.0
                    opts = []
                    for i in range(4):
                        sub = opt_part[int(round(i*step)):int(round((i+1)*step))]
                        opts.append(" ".join(t[2] for t in sub).strip())
                        
        opts = [re.sub(r"\s+", " ", o).strip() for o in opts]
        ans_idx = official_ans[q] - 1
        
        # Validation checks
        if len(q_text.split()) < 3:
            issues.append((q, "short question", q_text))
        if any(len(o) == 0 for o in opts):
            issues.append((q, "empty option", opts))
        if len(opts) != 4:
            issues.append((q, "not 4 options", opts))
            
        extracted.append((q, q_text, opts, ans_idx))
        
    print(f"[{cat}] Extracted {len(extracted)} / {total} questions. Issues: {len(issues)}")
    if issues:
        print("Sample issues:", issues[:10])
    return extracted

if __name__ == "__main__":
    rules = test_full_extraction('rules_of_road', 'rules-of-road-regulations-english.pdf', 180, 159, 18)
    gp = test_full_extraction('general_principles', 'general-driving-principles-english.pdf', 128, 159, 19)
