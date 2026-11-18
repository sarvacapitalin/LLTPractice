from scripts.verify_answers import get_official_pdf_answers
from scripts.test_unified_parser import parse_question_tokens

for name, cid, total, missing in [
    ('rules-of-road-regulations-english.pdf', 180, 159, {}),
    ('general-driving-principles-english.pdf', 128, 159, {
        32: "THE MOST EFFECTIVE DEVICE FOR",
        128: "WHAT WILL HAPPEN IF THE WHEELS",
        144: "ALCOHOL MAY AFFECT ADVERSELY",
        150: "BOARDING AND ALIGHTING WHILE"
    })
]:
    ans_dict, det_dict = get_official_pdf_answers(name, cid, total, missing)
    empty_q = []
    empty_opt = []
    for q in range(1, total + 1):
        q_text, opts, ans_idx = parse_question_tokens(det_dict[q]['tokens'], q, ans_dict[q])
        if not q_text:
            empty_q.append(q)
        for i, o in enumerate(opts):
            if not o:
                empty_opt.append((q, i))
    print(f"{name}: Empty Qs: {len(empty_q)} {empty_q[:5]}, Empty Opts: {len(empty_opt)} {empty_opt[:5]}")
