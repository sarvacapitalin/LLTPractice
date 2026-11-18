import json
from scripts.verify_answers import get_official_pdf_answers

# Extract ground truth answers from PDFs
pdf_answers = {}
pdf_answers['road_signs'], det_signs = get_official_pdf_answers('road-signs-english.pdf', 299, 94)
pdf_answers['rules_of_road'], det_rules = get_official_pdf_answers('rules-of-road-regulations-english.pdf', 180, 159)
pdf_answers['general_principles'], det_gp = get_official_pdf_answers('general-driving-principles-english.pdf', 128, 159, {
    32: "THE MOST EFFECTIVE DEVICE FOR",
    128: "WHAT WILL HAPPEN IF THE WHEELS",
    144: "ALCOHOL MAY AFFECT ADVERSELY",
    150: "BOARDING AND ALIGHTING WHILE"
})

# Load compiled datasets
compiled = {}
with open('data/questions/telangana/road-signs.json') as f:
    compiled['road_signs'] = json.load(f)
with open('data/questions/telangana/rules-of-road.json') as f:
    compiled['rules_of_road'] = json.load(f)
with open('data/questions/telangana/general-principles.json') as f:
    compiled['general_principles'] = json.load(f)

# Audit comparison
for cat, q_list in compiled.items():
    total = len(q_list)
    matches = 0
    mismatches = []
    for q in q_list:
        q_num = q['questionNumber']
        json_ans_idx = q['answerIndex'] # 0-indexed
        pdf_ans_val = pdf_answers[cat].get(q_num) # 1-indexed (1, 2, 3, 4)
        expected_ans_idx = (pdf_ans_val - 1) if pdf_ans_val is not None else None
        
        if json_ans_idx == expected_ans_idx:
            matches += 1
        else:
            mismatches.append({
                'q_num': q_num,
                'json_ans': json_ans_idx,
                'expected_ans': expected_ans_idx,
                'pdf_val': pdf_ans_val,
                'question_en': q['text']['en'][:50]
            })
    print(f'[{cat}] Total: {total}, Matches: {matches}, Mismatches: {len(mismatches)}, Parity: {matches/total*100:.2f}%')
    if mismatches:
        print(f'  First 5 mismatches in {cat}:')
        for m in mismatches[:5]:
            print('   ', m)
