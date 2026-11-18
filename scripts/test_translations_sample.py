# scripts/test_translations_sample.py
"""
Tests sample translations for road signs, rules of the road, and general driving principles.
"""

def test_samples():
    samples = [
        ("A RED TRAFFIC LIGHT MEANS", 
         "ఎరుపు రంగు (రెడ్) ట్రాఫిక్ సిగ్నల్ పడినప్పుడు ఏమిటి అర్ధం ?", 
         "यातायात की लालबत्ती का मतलब"),
        ("A FLASHING YELLOW LIGHT INDICATES", 
         "పసుపు రంగు ఫ్లాషింగ్ లైట్ ఏమి సూచిస్తుంది ?", 
         "चमकती पीली बत्ती क्या दर्शाती है ?"),
        ("A FLASHING RED LIGHT INDICATES", 
         "ఎరుపు రంగు ఫ్లాషింగ్ లైట్ ఏమి సూచిస్తుంది ?", 
         "चमकती लाल बत्ती क्या दर्शाती है ?"),
        ("MUST STOP BEHIND WHITE STOP LINE", 
         "తెల్లటి స్టాప్ లైన్ దాటకుండా ఆగాలి", 
         "सफेद स्टॉप लाइन के पीछे रुकें"),
        ("SLOW DOWN AND PROCEED WITH CAUTION", 
         "వేగాన్ని తగ్గించి జాగ్రత్తగా ముందుకు వెళ్లాలి", 
         "गति धीमी करें और सावधानी से आगे बढ़ें"),
        ("ALL OF THE ABOVE", 
         "పైవన్నీ", 
         "उपरोक्त सभी"),
        ("NONE OF THE ABOVE", 
         "పైవేవీ కావు", 
         "इनमें से कोई नहीं")
    ]
    for en, te, hi in samples:
        print(f"EN: {en}")
        print(f"TE: {te}")
        print(f"HI: {hi}\n")

if __name__ == "__main__":
    test_samples()
