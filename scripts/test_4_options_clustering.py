import re
from scripts.build_clean_english_extractor import get_segmented_questions, extract_qa

def cluster_tokens_into_4_options(opt_tokens):
    if not opt_tokens:
        return ["", "", "", ""]
        
    # If exactly 4 tokens, they are the 4 options!
    if len(opt_tokens) == 4:
        return [t.strip() for _, _, t in opt_tokens]
        
    # Otherwise, cluster by X coordinate into 4 columns
    # Find distinct X coordinate groups
    # Collect sorted unique X values with at least 35 units separation
    sorted_toks = sorted(opt_tokens, key=lambda el: el[0])
    
    # Simple 4-bin clustering based on min_x and max_x or sorted intervals
    min_x = sorted_toks[0][0]
    max_x = sorted_toks[-1][0]
    
    if max_x - min_x < 30:
        # All tokens have nearly same X (e.g. vertical layout or single TJ)
        # Split tokens evenly into 4
        k = len(opt_tokens)
        step = k / 4.0
        opts = []
        for i in range(4):
            sub = opt_tokens[int(round(i*step)):int(round((i+1)*step))]
            opts.append(" ".join(t.strip() for _, _, t in sub).strip())
        return opts

    # Find 4 cluster centroids or boundaries
    # The columns are approximately min_x + i * (max_x - min_x) / 3
    span = max_x - min_x
    options = [[], [], [], []]
    for x, y, t in opt_tokens:
        t_clean = t.strip()
        if not t_clean: continue
        col_idx = int(round((x - min_x) / (span / 3.0)))
        col_idx = max(0, min(3, col_idx))
        options[col_idx].append(t_clean)
        
    result = [" ".join(words).strip() for words in options]
    
    # If any column is empty, redistribute or fall back
    if any(len(o) == 0 for o in result):
        # Redistribute sequentially into 4 groups
        k = len(opt_tokens)
        step = k / 4.0
        result = []
        for i in range(4):
            sub = opt_tokens[int(round(i*step)):int(round((i+1)*step))]
            result.append(" ".join(t.strip() for _, _, t in sub).strip())
            
    return result

if __name__ == '__main__':
    for cat, pdf, cid, total in [
        ('road_signs', 'road-signs-english.pdf', 299, 94),
        ('rules_of_road', 'rules-of-road-regulations-english.pdf', 180, 159),
        ('general_principles', 'general-driving-principles-english.pdf', 128, 159)
    ]:
        qs = get_segmented_questions(cat, pdf, cid, total)
        empty_opts = 0
        for q in range(1, total + 1):
            p, toks = qs[q]
            q_text, opt_toks, ans_idx = extract_qa(q, p, toks, cat)
            opts = cluster_tokens_into_4_options(opt_toks)
            assert len(opts) == 4, f"Q{q} in {cat} does not have 4 options: {len(opts)}"
            if any(len(o) == 0 for o in opts):
                empty_opts += 1
                print(f"Empty option in Q{q} of {cat}: {opts}")
        print(f"[{cat}] All {total} questions have 4 options! Empty count = {empty_opts}")
