import re
import json
from scripts.parse_full_dataset import extract_elements

def get_row_stream(pdf_path, cmap_id, category_name):
    pages = extract_elements(pdf_path, cmap_id)
    all_tokens = []
    
    header_words = {
        'S.NO.', 'QUESTIONS', 'S.NO.QUESTIONS', 'RELEVANT FIGURE/SIGN', 'IF ANY',
        'RELEVANT', 'FIGURE/SIGN',
        'OPTION1', 'OPTION2', 'OPTION3', 'OPTION4', 'OPTION1OPTION2OPTION3OPTION4',
        'ANSWER', 'ANSWER ', 'OPTION', 'S'
    }
    
    header_len = 18 if category_name != 'general_principles' else 19
    
    for p_num, elems in pages:
        cur_elems = elems[header_len:] if p_num == 1 else elems
        for x, y, t in cur_elems:
            if t in header_words:
                continue
            all_tokens.append((p_num, x, y, t))
            
    if category_name == 'general_principles':
        fixed = []
        for p, x, y, t in all_tokens:
            if 'THE MOST EFFECTIVE DEVICE FOR' in t:
                fixed.append((p, -133.0, y, '32'))
            elif 'WHAT WILL HAPPEN IF THE WHEELS' in t:
                fixed.append((p, -133.0, y, '128'))
            elif 'ALCOHOL MAY AFFECT ADVERSELY' in t:
                fixed.append((p, -133.0, y, '144'))
            elif 'BOARDING AND ALIGHTING WHILE' in t:
                fixed.append((p, -133.0, y, '150'))
            fixed.append((p, x, y, t))
        all_tokens = fixed
        
    return all_tokens

if __name__ == '__main__':
    for name, cid, total, cat in [
        ('road-signs-english.pdf', 299, 94, 'road_signs'),
        ('rules-of-road-regulations-english.pdf', 180, 159, 'rules_of_road'),
        ('general-driving-principles-english.pdf', 128, 159, 'general_principles')
    ]:
        tokens = get_row_stream(name, cid, cat)
        print(f"{cat}: {len(tokens)} content tokens")
