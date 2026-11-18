import re
import json
from scripts.parse_full_dataset import extract_elements, filter_header

def segment_dataset(pdf_path, cmap_id, total_count, category_name):
    pages = extract_elements(pdf_path, cmap_id)
    all_elems = []
    for p_num, elems in pages:
        cleaned = filter_header(elems, p_num)
        all_elems.extend([(p_num, x, y, t) for x, y, t in cleaned])
        
    # If general driving principles, inject the 4 missing question numbers
    if category_name == "general_principles":
        fixed = []
        for p, x, y, t in all_elems:
            if "THE MOST EFFECTIVE DEVICE FOR" in t:
                fixed.append((p, x, y, "32"))
            elif "WHAT WILL HAPPEN IF THE WHEELS" in t:
                fixed.append((p, x, y, "128"))
            elif "ALCOHOL MAY AFFECT ADVERSELY" in t:
                fixed.append((p, x, y, "144"))
            elif "BOARDING AND ALIGHTING WHILE" in t:
                fixed.append((p, x, y, "150"))
            fixed.append((p, x, y, t))
        all_elems = fixed

    questions = {}
    current_q = 1
    i = 0
    n = len(all_elems)
    while i < n and current_q <= total_count:
        p, x, y, t = all_elems[i]
        m = re.match(r"^" + str(current_q) + r"(?:\b|[A-Za-z])", t)
        if m:
            tokens = []
            rem = t[len(str(current_q)):].strip()
            if rem:
                tokens.append((x, y, rem))
            j = i + 1
            target_next = current_q + 1
            while j < n:
                pj, xj, yj, tj = all_elems[j]
                if target_next <= total_count and re.match(r"^" + str(target_next) + r"(?:\b|[A-Za-z])", tj):
                    break
                # Deduplicate identical repeats on road signs (drop shadows)
                if category_name == "road_signs" and re.match(r"^" + str(current_q) + r"$", tj):
                    break
                tokens.append((xj, yj, tj))
                j += 1
            questions[current_q] = (p, tokens)
            current_q += 1
            i = j - 1
        i += 1
        
    print(f"[{category_name}] Segmented {len(questions)} / {total_count} questions.")
    missing = [q for q in range(1, total_count + 1) if q not in questions]
    if missing:
        print(f"  Missing: {missing}")
        
    return questions

if __name__ == "__main__":
    signs_q = segment_dataset("road-signs-english.pdf", 299, 94, "road_signs")
    rules_q = segment_dataset("rules-of-road-regulations-english.pdf", 180, 159, "rules_of_road")
    gp_q = segment_dataset("general-driving-principles-english.pdf", 128, 159, "general_principles")
