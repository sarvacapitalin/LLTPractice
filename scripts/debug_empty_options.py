from scripts.verify_answers import get_official_pdf_answers
from scripts.test_category_parser import parse_question_tokens_category

ans_rules, det_rules = get_official_pdf_answers('rules-of-road-regulations-english.pdf', 180, 159, {})

empty_cases = []
for q in range(1, 160):
    q_text, opts, ans_idx = parse_question_tokens_category(det_rules[q]['tokens'], q, ans_rules[q], 'rules_of_road')
    for i, o in enumerate(opts):
        if not o:
            empty_cases.append((q, i, det_rules[q]['tokens']))

print(f"Total empty option slots in Rules: {len(empty_cases)}")
# Print first 3
for q, i, tokens in empty_cases[:3]:
    print(f"\n--- Q{q} Opt {i} ---")
    for y, c, t in tokens:
        print(f"  y={y:6.2f}, c={c}: {t}")
