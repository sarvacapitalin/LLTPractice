import json

with open("data/questions/telangana/road-signs.json", "r", encoding="utf-8") as f:
    signs = json.load(f)

for s in signs:
    q = s["questionNumber"]
    if q == 86:
        s["text"] = {
            "en": "IF THE DRIVER IS GIVING THIS HAND SIGNAL, WHAT DOES HE MEAN?",
            "te": "డ్రైవర్ ఈ చేతి సంకేతాన్ని ఇస్తుంటే, దాని అర్థం ఏమిటి?",
            "hi": "यदि चालक यह हाथ का संकेत दे रहा है, तो उसका क्या अर्थ है?"
        }
        s["options"] = {
            "en": [
                "HE INTENDS TO MOVE TO THE LEFT OR TO TURN LEFT",
                "HE INTENDS TO MOVE OUT TO THE RIGHT OR TURN RIGHT",
                "HE INTENDS TO STOP",
                "HE INTENDS TO SLOW DOWN"
            ],
            "te": [
                "ఎడమ వైపునకు వెళ్లడానికి లేదా ఎడమకు తిరగడానికి ఉద్దేశిస్తున్నాడు",
                "కుడి వైపునకు వెళ్లడానికి లేదా కుడికి తిరగడానికి ఉద్దేశిస్తున్నాడు",
                "వాహనాన్ని ఆపడానికి ఉద్దేశిస్తున్నాడు",
                "వాహనం వేగాన్ని తగ్గించడానికి ఉద్దేశిస్తున్నాడు"
            ],
            "hi": [
                "वह बाईं ओर मुड़ने या जाने का इरादा रखता है",
                "वह दाईं ओर मुड़ने या जाने का इरादा रखता है",
                "वह वाहन रोकने का इरादा रखता है",
                "वह वाहन की गति धीमी करने का इरादा रखता है"
            ]
        }
        s["answerIndex"] = 0
        s["explanation"] = {
            "en": "Official RTA Key: Option 1. (⚠️ Exam Tip: In motor vehicle rules, extending the right arm horizontally signals a right turn, but the official computerized RTA question bank marks Option 1 for this test question).",
            "te": "అధికారిక RTA సమాధానం: ఎంపిక 1. (⚠️ పరీక్ష చిట్కా: మోటారు వాహన నిబంధనల ప్రకారం కుడి చేయి చాచడం కుడి మలుపును సూచిస్తుంది, కానీ కంప్యూటర్ RTA పరీక్షలో ఈ ప్రశ్నకు ఎంపిక 1 సరైన సమాధానంగా నిర్ణయించబడింది).",
            "hi": "आधिकारिक RTA उत्तर: विकल्प 1. (⚠️ परीक्षा टिप: मोटर वाहन नियमों में दायां हाथ सीधा फैलाना दाएं मुड़ने का संकेत है, लेकिन आधिकारिक RTA परीक्षा में इस प्रश्न का उत्तर विकल्प 1 अंकित है)।"
        }
    elif q == 87:
        s["text"] = {
            "en": "IF THE DRIVER IS GIVING THIS HAND SIGNAL, WHAT DOES HE MEAN?",
            "te": "డ్రైవర్ ఈ చేతి సంకేతాన్ని ఇస్తుంటే, దాని అర్థం ఏమిటి?",
            "hi": "यदि चालक यह हाथ का संकेत दे रहा है, तो उसका क्या अर्थ है?"
        }
        s["options"] = {
            "en": [
                "HE INTENDS TO MOVE TO THE LEFT OR TO TURN LEFT",
                "HE INTENDS TO MOVE OUT TO THE RIGHT OR TURN RIGHT",
                "HE INTENDS TO STOP",
                "HE INTENDS TO SLOW DOWN"
            ],
            "te": [
                "ఎడమ వైపునకు వెళ్లడానికి లేదా ఎడమకు తిరగడానికి ఉద్దేశిస్తున్నాడు",
                "కుడి వైపునకు వెళ్లడానికి లేదా కుడికి తిరగడానికి ఉద్దేశిస్తున్నాడు",
                "వాహనాన్ని ఆపడానికి ఉద్దేశిస్తున్నాడు",
                "వాహనం వేగాన్ని తగ్గించడానికి ఉద్దేశిస్తున్నాడు"
            ],
            "hi": [
                "वह बाईं ओर मुड़ने या जाने का इरादा रखता है",
                "वह दाईं ओर मुड़ने या जाने का इरादा रखता है",
                "वह वाहन रोकने का इरादा रखता है",
                "वह वाहन की गति धीमी करने का इरादा रखता है"
            ]
        }
        s["answerIndex"] = 1
        s["explanation"] = {
            "en": "Official RTA Key: Option 2 ('HE INTENDS TO MOVE OUT TO THE RIGHT OR TURN RIGHT').",
            "te": "అధికారిక RTA సమాధానం: ఎంపిక 2 (కుడి వైపునకు వెళ్లడానికి లేదా కుడికి తిరగడానికి ఉద్దేశిస్తున్నాడు).",
            "hi": "आधिकारिक RTA उत्तर: विकल्प 2 (वह दाईं ओर मुड़ने या जाने का इरादा रखता है)।"
        }
    elif q == 88:
        s["text"] = {
            "en": "IF THE DRIVER IS GIVING THIS HAND SIGNAL, WHAT DOES HE MEAN?",
            "te": "డ్రైవర్ ఈ చేతి సంకేతాన్ని ఇస్తుంటే, దాని అర్థం ఏమిటి?",
            "hi": "यदि चालक यह हाथ का संकेत दे रहा है, तो उसका क्या अर्थ है?"
        }
        s["options"] = {
            "en": [
                "HE INTENDS TO MOVE TO THE LEFT OR TO TURN LEFT",
                "HE INTENDS TO MOVE OUT TO THE RIGHT OR TURN RIGHT",
                "HE INTENDS TO STOP",
                "HE INTENDS TO SLOW DOWN"
            ],
            "te": [
                "ఎడమ వైపునకు వెళ్లడానికి లేదా ఎడమకు తిరగడానికి ఉద్దేశిస్తున్నాడు",
                "కుడి వైపునకు వెళ్లడానికి లేదా కుడికి తిరగడానికి ఉద్దేశిస్తున్నాడు",
                "వాహనాన్ని ఆపడానికి ఉద్దేశిస్తున్నాడు",
                "వాహనం వేగాన్ని తగ్గించడానికి ఉద్దేశిస్తున్నాడు"
            ],
            "hi": [
                "वह बाईं ओर मुड़ने या जाने का इरादा रखता है",
                "वह दाईं ओर मुड़ने या जाने का इरादा रखता है",
                "वह वाहन रोकने का इरादा रखता है",
                "वह वाहन की गति धीमी करने का इरादा रखता है"
            ]
        }
        s["answerIndex"] = 2
        s["explanation"] = {
            "en": "Official RTA Key: Option 3 ('HE INTENDS TO STOP'). Raising forearm vertically signals stopping.",
            "te": "అధికారిక RTA సమాధానం: ఎంపిక 3 (వాహనాన్ని ఆపడానికి ఉద్దేశిస్తున్నాడు). ముంజేయిని నిలువుగా పైకెత్తడం ఆగడాన్ని సూచిస్తుంది.",
            "hi": "आधिकारिक RTA उत्तर: विकल्प 3 (वह वाहन रोकने का इरादा रखता है)। हाथ को लंबवत ऊपर उठाना रुकने का संकेत है।"
        }
    elif q == 89:
        s["text"] = {
            "en": "IF THE DRIVER IS GIVING THIS HAND SIGNAL, WHAT DOES HE MEAN?",
            "te": "డ్రైవర్ ఈ చేతి సంకేతాన్ని ఇస్తుంటే, దాని అర్థం ఏమిటి?",
            "hi": "यदि चालक यह हाथ का संकेत दे रहा है, तो उसका क्या अर्थ है?"
        }
        s["options"] = {
            "en": [
                "HE INTENDS TO MOVE TO THE LEFT OR TO TURN LEFT",
                "HE INTENDS TO MOVE OUT TO THE RIGHT OR TURN RIGHT",
                "HE INTENDS TO STOP",
                "HE INTENDS TO SLOW DOWN"
            ],
            "te": [
                "ఎడమ వైపునకు వెళ్లడానికి లేదా ఎడమకు తిరగడానికి ఉద్దేశిస్తున్నాడు",
                "కుడి వైపునకు వెళ్లడానికి లేదా కుడికి తిరగడానికి ఉద్దేశిస్తున్నాడు",
                "వాహనాన్ని ఆపడానికి ఉద్దేశిస్తున్నాడు",
                "వాహనం వేగాన్ని తగ్గించడానికి ఉద్దేశిస్తున్నాడు"
            ],
            "hi": [
                "वह बाईं ओर मुड़ने या जाने का इरादा रखता है",
                "वह दाईं ओर मुड़ने या जाने का इरादा रखता है",
                "वह वाहन रोकने का इरादा रखता है",
                "वह वाहन की गति धीमी करने का इरादा रखता है"
            ]
        }
        s["answerIndex"] = 3
        s["explanation"] = {
            "en": "Official RTA Key: Option 4 ('HE INTENDS TO SLOW DOWN'). Moving the extended arm up and down signals slowing down.",
            "te": "అధికారిక RTA సమాధానం: ఎంపిక 4 (వాహనం వేగాన్ని తగ్గించడానికి ఉద్దేశిస్తున్నాడు). చేతిని పైకి క్రిందికి ఊపడం వేగం తగ్గించడాన్ని సూచిస్తుంది.",
            "hi": "आधिकारिक RTA उत्तर: विकल्प 4 (वह वाहन की गति धीमी करने का इरादा रखता है)। हाथ को ऊपर-नीचे हिलाना धीमा करने का संकेत है।"
        }
    elif q == 90:
        s["text"] = {
            "en": "IF THE DRIVER IS GIVING THIS HAND SIGNAL, WHAT DOES HE MEAN?",
            "te": "డ్రైవర్ ఈ చేతి సంకేతాన్ని ఇస్తుంటే, దాని అర్థం ఏమిటి?",
            "hi": "यदि चालक यह हाथ का संकेत दे रहा है, तो उसका क्या अर्थ है?"
        }
        s["options"] = {
            "en": [
                "HE INTENDS TO MOVE TO THE LEFT OR TO TURN LEFT",
                "HE INTENDS TO MOVE OUT TO THE RIGHT OR TURN RIGHT",
                "HE INTENDS TO STOP",
                "HE INTENDS TO GIVE WAY, TO BE OVERTAKEN"
            ],
            "te": [
                "ఎడమ వైపునకు వెళ్లడానికి లేదా ఎడమకు తిరగడానికి ఉద్దేశిస్తున్నాడు",
                "కుడి వైపునకు వెళ్లడానికి లేదా కుడికి తిరగడానికి ఉద్దేశిస్తున్నాడు",
                "వాహనాన్ని ఆపడానికి ఉద్దేశిస్తున్నాడు",
                "వెనుక వాహనం ఓవర్‌టేక్ చేయడానికి సైడ్ ఇవ్వడానికి ఉద్దేశిస్తున్నాడు"
            ],
            "hi": [
                "वह बाईं ओर मुड़ने या जाने का इरादा रखता है",
                "वह दाईं ओर मुड़ने या जाने का इरादा रखता है",
                "वह वाहन रोकने का इरादा रखता है",
                "वह पीछे वाले वाहन को ओवरटेक करने की अनुमति दे रहा है"
            ]
        }
        s["answerIndex"] = 3
        s["explanation"] = {
            "en": "Official RTA Key: Option 4 ('HE INTENDS TO GIVE WAY, TO BE OVERTAKEN'). Waving arm forward signals other vehicles to overtake.",
            "te": "అధికారిక RTA సమాధానం: ఎంపిక 4 (వెనుక వాహనం ఓవర్‌టేక్ చేయడానికి సైడ్ ఇవ్వడం). చేతిని ముందుకు వెనుకకు తిప్పడం ఓవర్‌టేక్ చేయమని సూచిస్తుంది.",
            "hi": "आधिकारिक RTA उत्तर: विकल्प 4 (पीछे वाले वाहन को ओवरटेक करने की अनुमति देना)।"
        }

with open("data/questions/telangana/road-signs.json", "w", encoding="utf-8") as f:
    json.dump(signs, f, indent=2, ensure_ascii=False)

print("Updated Q86-Q90 with authentic trilingual text, options, and official RTA key notes.")
