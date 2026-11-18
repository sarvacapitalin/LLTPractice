import json, re, os
from scripts.verify_answers import get_official_pdf_answers
from scripts.test_refined_parser import parse_question_tokens_refined, clean_txt

ans_signs, det_signs = get_official_pdf_answers('road-signs-english.pdf', 299, 94)

# Handle known concatenated options in PDF font layout
known_splits = {
    62: {
        'opt2_raw': 'HUMP OR ROUGH ROADMAJOR ROAD AHEAD',
        'opt2': 'HUMP OR ROUGH ROAD',
        'opt3': 'MAJOR ROAD AHEAD'
    }
}

questions = []
for q in range(1, 95):
    q_text, opts, ans_idx = parse_question_tokens_refined(det_signs[q]['tokens'], q, ans_signs[q], 'road_signs')
    
    # Apply splits if needed
    if q in known_splits:
        opts[1] = known_splits[q]['opt2']
        opts[2] = known_splits[q]['opt3']
        
    # Sign classification
    if q <= 42:
        sign_type = "mandatory"
    elif q <= 80:
        sign_type = "cautionary"
    else:
        sign_type = "informatory"
        
    correct_opt = opts[ans_idx]
    
    # Translations
    # Telugu & Hindi
    q_te = f"ఈ రోడ్డు చిహ్నం అర్థమేమిటి ? (ప్రశ్న {q})" if "WHAT DOES THIS SIGN MEAN" in q_text.upper() else f"ప్రశ్న {q}: {q_text}"
    q_hi = f"इस सड़क चिन्ह का क्या अर्थ है? (प्रश्न {q})" if "WHAT DOES THIS SIGN MEAN" in q_text.upper() else f"प्रश्न {q}: {q_text}"
    
    if q == 1:
        q_te = "ఎరుపు రంగు (రెడ్) ట్రాఫిక్ సిగ్నల్ పడినప్పుడు ఏమిటి అర్ధం ?"
        q_hi = "यातायात की लालबत्ती का मतलब क्या है?"
    elif q == 2:
        q_te = "పసుపు రంగు లైటు వెలుగుతూ ఆరుతుంటే (బ్లింక్ అవుతుంటే) ఏమిటి అర్ధం ?"
        q_hi = "चमकती पीली बत्ती (फ्लैशिंग येलो) का मतलब क्या है?"
    elif q == 3:
        q_te = "ఎరుపు రంగు లైటు వెలుగుతూ ఆరుతుంటే (బ్లింక్ అవుతుంటే) ఏమిటి అర్ధం ?"
        q_hi = "चमकती लाल बत्ती (फ्लैशिंग रेड) का मतलब क्या है?"
    elif q == 4:
        q_te = "ఈ వృత్తాకార చిహ్నాలు దేనిని సూచిస్తాయి ?"
        q_hi = "वृत्ताकार चिन्ह क्या दर्शाते हैं?"
    elif q == 5:
        q_te = "ఈ త్రిభుజాకార చిహ్నాలు దేనిని సూచిస్తాయి ?"
        q_hi = "त्रिकोणीय चिन्ह क्या दर्शाते हैं?"
    elif q == 6:
        q_te = "ఈ దీర్ఘచతురస్రాకార చిహ్నాలు దేనిని సూచిస్తాయి ?"
        q_hi = "आयताकार चिन्ह क्या दर्शाते हैं?"
        
    opts_te = [f"ఎంపిక {i+1}: {opt}" for i, opt in enumerate(opts)]
    opts_hi = [f"विकल्प {i+1}: {opt}" for i, opt in enumerate(opts)]
    
    exp_en = f"Official Road Sign Rule: {correct_opt}."
    exp_te = f"అధికారిక రోడ్డు నిబంధన ప్రకారం సరైన సమాధానం: {correct_opt}."
    exp_hi = f"आधिकारिक सड़क नियम के अनुसार सही उत्तर: {correct_opt}."
    
    questions.append({
        "id": f"TS_RS_{q:03d}",
        "category": "road_signs",
        "signType": sign_type,
        "questionNumber": q,
        "image": f"assets/signs/sign_{q:03d}.png",
        "text": {
            "en": q_text,
            "te": q_te,
            "hi": q_hi
        },
        "options": {
            "en": opts,
            "te": opts_te,
            "hi": opts_hi
        },
        "answerIndex": ans_idx,
        "explanation": {
            "en": exp_en,
            "te": exp_te,
            "hi": exp_hi
        }
    })

print(f"Compiled {len(questions)} certified road signs.")
with open('data/questions/telangana/road-signs.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)
print("Saved data/questions/telangana/road-signs.json successfully.")
