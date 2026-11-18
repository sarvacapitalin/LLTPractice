import json
import re

def test_parse_principles():
    with open("scripts/principles_extracted_raw.json") as f:
        gp_raw = json.load(f)
        
    print(f"Total general principles loaded: {len(gp_raw)}")
    
    parsed = []
    for q_id_str, (p_num, tokens) in gp_raw.items():
        q_num = int(q_id_str)
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
        parsed.append((q_num, ans, tokens[:2]))
        
    missing_ans = [p[0] for p in parsed if p[1] is None]
    print(f"Parsed {len(parsed)} principles. Missing answer keys: {len(missing_ans)}")
    if missing_ans:
        print(f"Missing answers: {missing_ans[:10]}")

if __name__ == "__main__":
    test_parse_principles()
