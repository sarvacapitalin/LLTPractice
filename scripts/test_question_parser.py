import json
import re

def test_parse_rules():
    with open("scripts/rules_extracted_raw.json") as f:
        rules_raw = json.load(f)
        
    print(f"Total rules loaded: {len(rules_raw)}")
    
    parsed = []
    for q_id_str, (p_num, tokens) in rules_raw.items():
        q_num = int(q_id_str)
        # Parse tokens
        # Find answer digit at end
        ans = None
        for t in reversed(tokens):
            t_s = t.strip()
            if t_s in ["1", "2", "3", "4"]:
                ans = int(t_s)
                break
            m = re.search(r"(\d)$", t_s)
            if m and m.group(1) in ["1", "2", "3", "4"]:
                ans = int(m.group(1))
                break
        parsed.append((q_num, ans, tokens[:3]))
        
    missing_ans = [p[0] for p in parsed if p[1] is None]
    print(f"Parsed {len(parsed)} rules. Missing answer keys: {len(missing_ans)}")
    if missing_ans:
        print(f"Missing answers: {missing_ans[:10]}")

if __name__ == "__main__":
    test_parse_rules()
