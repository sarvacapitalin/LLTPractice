from scripts.verify_answers import get_official_pdf_answers

signs_ans, signs_det = get_official_pdf_answers('road-signs-english.pdf', 299, 94)
rules_ans, rules_det = get_official_pdf_answers('rules-of-road-regulations-english.pdf', 180, 159)
gp_ans, gp_det = get_official_pdf_answers('general-driving-principles-english.pdf', 128, 159, {
    32: "THE MOST EFFECTIVE DEVICE FOR",
    128: "WHAT WILL HAPPEN IF THE WHEELS",
    144: "ALCOHOL MAY AFFECT ADVERSELY",
    150: "BOARDING AND ALIGHTING WHILE"
})

print(f"Signs extracted: {len(signs_ans)}")
print(f"Rules extracted: {len(rules_ans)}")
print(f"GP extracted: {len(gp_ans)}")

# Check values are all in [1, 2, 3, 4]
for name, ans_dict in [("Road Signs", signs_ans), ("Rules of Road", rules_ans), ("General Principles", gp_ans)]:
    invalid = {k: v for k, v in ans_dict.items() if v not in [1, 2, 3, 4]}
    print(f"{name}: invalid answers: {len(invalid)} -> {invalid}")
