import json
import re

def build_rules_json():
    with open("scripts/rules_monotonic.json") as f:
        rules_data = json.load(f)
        
    print(f"Loaded {len(rules_data)} rules from monotonic json.")
    
    questions = []
    
    for q_num_str in sorted(rules_data.keys(), key=lambda x: int(x)):
        q_num = int(q_num_str)
        item = rules_data[q_num_str]
        elems = item["elements"]
        
        ans_digit = None
        for x, y, t in reversed(elems):
            parts = [p.strip() for p in t.split("\t") if p.strip()]
            for p in reversed(parts):
                if p in ["1", "2", "3", "4"]:
                    ans_digit = int(p)
                    break
                m = re.search(r"(\d)$", p)
                if m and m.group(1) in ["1", "2", "3", "4"]:
                    ans_digit = int(m.group(1))
                    break
            if ans_digit is not None:
                break
                
        ans_idx = (ans_digit - 1) if ans_digit else 0
        
        questions.append({
            "id": f"TS_RR_{q_num:03d}",
            "category": "rules_of_road",
            "questionNumber": q_num,
            "answerIndex": ans_idx,
            "raw_elements": [e[2] for e in elems]
        })
        
    print(f"Processed {len(questions)} rules.")
    return questions

if __name__ == "__main__":
    qs = build_rules_json()
    missing_ans = [q["questionNumber"] for q in qs if q["answerIndex"] is None]
    print(f"Missing answer index count: {len(missing_ans)}")
