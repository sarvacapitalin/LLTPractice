import json
import re

def clean_str(s):
    return re.sub(r"\s+", " ", s).strip()

def build_signs_json():
    with open("scripts/signs_monotonic.json") as f:
        signs_data = json.load(f)
        
    print(f"Loaded {len(signs_data)} signs from monotonic json.")
    
    questions = []
    
    for q_num_str in sorted(signs_data.keys(), key=lambda x: int(x)):
        q_num = int(q_num_str)
        item = signs_data[q_num_str]
        elems = item["elements"]
        
        # Classify sign type
        if q_num <= 42:
            sign_type = "mandatory"
        elif q_num <= 80:
            sign_type = "cautionary"
        else:
            sign_type = "informatory"
            
        img_name = f"assets/signs/sign_{q_num:03d}.png"
        
        # Collect full text and split on tab if available
        # Find answer digit at end
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
                
        # Default answer if not found
        ans_idx = (ans_digit - 1) if ans_digit else 0
        
        questions.append({
            "id": f"TS_RS_{q_num:03d}",
            "category": "road_signs",
            "signType": sign_type,
            "questionNumber": q_num,
            "image": img_name,
            "answerIndex": ans_idx,
            "raw_elements": [e[2] for e in elems]
        })
        
    print(f"Processed {len(questions)} road signs.")
    return questions

if __name__ == "__main__":
    qs = build_signs_json()
    missing_ans = [q["questionNumber"] for q in qs if q["answerIndex"] is None]
    print(f"Missing answer index count: {len(missing_ans)}")
