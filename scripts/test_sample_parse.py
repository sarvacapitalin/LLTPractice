import json
import re

def parse_full_question(tokens):
    """
    Parses token list into (question_text, [opt1, opt2, opt3, opt4], answer_idx)
    """
    # Look for answer digit at end
    ans_digit = None
    last_idx = len(tokens) - 1
    while last_idx >= 0:
        t = tokens[last_idx].strip()
        if t in ["1", "2", "3", "4"]:
            ans_digit = int(t)
            tokens = tokens[:last_idx]
            break
        m = re.search(r"(\d)$", t)
        if m and m.group(1) in ["1", "2", "3", "4"]:
            ans_digit = int(m.group(1))
            tokens = tokens[:last_idx] + [t[:-1].strip()]
            break
        last_idx -= 1
        
    full_str = " ".join(t.strip() for t in tokens if t.strip())
    # Clean multiple spaces
    full_str = re.sub(r"\s+", " ", full_str)
    
    return full_str, ans_digit

# Inspect 5 samples from signs, rules, principles
with open("scripts/signs_extracted_raw.json") as f:
    signs = json.load(f)
with open("scripts/rules_extracted_raw.json") as f:
    rules = json.load(f)
with open("scripts/principles_extracted_raw.json") as f:
    gp = json.load(f)

print("=== SAMPLES ===")
print("Sign 10:", parse_full_question(signs["10"][1]))
print("Rule 50:", parse_full_question(rules["50"][1]))
print("Principle 8:", parse_full_question(gp["8"][1]))
