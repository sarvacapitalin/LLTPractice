from scripts.build_clean_english_extractor import get_segmented_questions, extract_qa
from scripts.test_4_options_clustering import cluster_tokens_into_4_options
from scripts.verify_answers import get_official_pdf_answers

ans_signs, det_signs = get_official_pdf_answers('road-signs-english.pdf', 299, 94)
qs = get_segmented_questions('road_signs', 'road-signs-english.pdf', 299, 94)

for q in range(1, 95):
    p, toks = qs[q]
    raw_q, opt_toks, raw_ans = extract_qa(q, p, toks, 'road_signs')
    opts = cluster_tokens_into_4_options(opt_toks)
    if q == 68:
        opts = ['ZIG ZAG ROAD', 'FERRY', 'HUMP OR ROUGH ROAD', 'STRAIGHT ROAD']
    exp_idx = ans_signs[q] - 1
    print(f"Q{q:02d} [AnsIdx {raw_ans}] Q: '{raw_q}'")
    for i, o in enumerate(opts):
        marker = " *" if i == raw_ans else ""
        print(f"   ({i+1}) {o}{marker}")
