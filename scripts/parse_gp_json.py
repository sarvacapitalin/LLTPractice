import json
import re

def build_gp_json():
    with open("scripts/gp_monotonic.json") as f:
        gp_data = json.load(f)
        
    print(f"Loaded {len(gp_data)} general principles from monotonic json.")
    
    questions = []
    
    for q_num_str in sorted(gp_data.keys(), key=lambda x: int(x)):
        q_num = int(q_num_str)
        item = gp_data[q_num_str]
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
            "id": f"TS_GP_{q_num:03d}",
            "category": "general_principles",
            "questionNumber": q_num,
            "answerIndex": ans_idx,
            "raw_elements": [e[2] for e in elems]
        })
        
    print(f"Processed {len(questions)} general principles.")
    return questions

if __name__ == "__main__":
    qs = build_gp_json()
    missing_ans = [q["questionNumber"] for q in qs if q["answerIndex"] is None]
    print(f"Missing answer index count: {len(missing_ans)}")
