import re
import json

def parse_question_tokens(tokens):
    """
    Given a list of strings collected for a question:
    Extract:
    - question text
    - 4 options
    - answer number (1-4)
    """
    full_str = " ".join(tokens)
    
    # Check if there is an answer number at the very end
    # Often the last token is '1', '2', '3', '4' or ends with '1'..'4'
    ans = None
    # Look for standalone digit 1..4 at end or trailing digit
    for t in reversed(tokens):
        t_clean = t.strip()
        if t_clean in ["1", "2", "3", "4"]:
            ans = int(t_clean)
            break
        m = re.search(r"(\d)$", t_clean)
        if m and m.group(1) in ["1", "2", "3", "4"]:
            ans = int(m.group(1))
            break
            
    return ans, full_str

# Test on signs
with open("scripts/signs_extracted_raw.json") as f:
    signs_raw = json.load(f)

for q in ["1", "2", "3", "10", "45", "94"]:
    ans, text = parse_question_tokens(signs_raw[q][1])
    print(f"Sign Q{q}: Ans={ans} | Text snippet: {text[:80]}...")
