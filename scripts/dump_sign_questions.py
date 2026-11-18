from scripts.verify_answers import get_official_pdf_answers
import json

ans_signs, det_signs = get_official_pdf_answers('road-signs-english.pdf', 299, 94)

# Print first 25 questions and their extracted tokens
for q_num in range(1, 26):
    q_det = det_signs[q_num]
    tokens = [t[2] for t in q_det['tokens']]
    print(f"=== Sign Q{q_num} (Ans: {q_det['chosen']}) ===")
    print("  Tokens:", tokens)
