# Script to build data/questions/telangana/road-signs.json (94 questions)
import json, os

def get_road_signs():
    return [
        {
            "id": "TS_RS_001",
            "category": "road_signs",
            "signType": "mandatory",
            "questionNumber": 1,
            "image": "assets/signs/sign_001.png",
            "text": {
                "en": "A RED TRAFFIC LIGHT MEANS",
                "te": "ఎరుపు రంగు (రెడ్) సిగ్నల్ పడినప్పుడు ఏమిటి అర్ధం ?",
                "hi": "यातायात की लालबत्ती का मतलब"
            },
            "options": {
                "en": [
                    "MUST STOP BEHIND WHITE STOP LINE",
                    "YOU MAY GO STRAIGHT IF THERE IS NO OTHER TRAFFIC",
                    "YOU MAY TURN LEFT IF IT IS SAFE TO DO SO",
                    "YOU MUST SLOW DOWN AND PREPARE TO STOP IF TRAFFIC HAS STARTED TO CROSS"
                ],
                "te": [
                    "తెల్లటి స్టాప్లైన్ దాటకుండా ఆగాలని అర్ధం",
                    "ఇతర వాహనాలు ఏవీ లేనప్పుడు ముందుకు వెళ్లమని అర్ధం",
                    "ఏ ప్రమాదమూ ఎదురవ్వదనిపిస్తే ఎడమ పక్కకు తిరగమని అర్ధం",
                    "మీ వ్యతిరేక దిశలో ట్రాఫిక్ మొదలైతే వెంటనే ఆగందుకు వీలుగా మీరు వేగాన్ని తగ్గించాలని అర్ధం"
                ],
                "hi": [
                    "सफेद लाइन के पीछे रुकें",
                    "ट्रेफिक न हो, तो सीधे चले जाएं",
                    "सुरक्षित महसूस करने पर बांये हाथ की ओर मुडे",
                    "यदि यातायात आरंभ हो गया है, तो वाहन की गति धीमी करें"
                ]
            },
            "answerIndex": 0,
            "explanation": {
                "en": "A red traffic light is a mandatory stop instruction. You must bring the vehicle to a complete halt behind the white stop line.",
                "te": "ఎరుపు సిగ్నల్ తప్పనిసరి స్టాప్ ఆర్డర్. స్టాప్ లైన్ దాటకుండా వాహనాన్ని పూర్తిగా ఆపాలి.",
                "hi": "लाल बत्ती अनिवार्य रूप से रुकने का संकेत है। सफेद स्टॉप लाइन के पीछे पूरी तरह रुकना आवश्यक है।"
            }
        },
        {
            "id": "TS_RS_002",
            "category": "road_signs",
            "signType": "cautionary",
            "questionNumber": 2,
            "image": "assets/signs/sign_002.png",
            "text": {
                "en": "A FLASHING YELLOW LIGHT INDICATES",
                "te": "పసుపు రంగు లైటు ఫ్లాష్ అవుతున్న ఒక జంక్షన్ ఎదురైనప్పుడు ఏమిచేయాలి ?",
                "hi": "पीली बत्ती का मतलब"
            },
            "options": {
                "en": [
                    "SLOW DOWN AND PROCEED WITH CAUTION",
                    "NO ENTRY",
                    "STOP HERE",
                    "NONE OF THE ABOVE"
                ],
                "te": [
                    "వేగాన్ని తగ్గించి జాగ్రత్తగా ముందుకువెళ్లాలి",
                    "ప్రవేశం లేదు",
                    "ఆగిపోవాలి",
                    "పైవేవీ కావు"
                ],
                "hi": [
                    "गति धीमी कर सावधानी से बढ़ें",
                    "प्रवेश निषेध",
                    "यहां रुकें",
                    "इनमें से कोई भी नहीं"
                ]
            },
            "answerIndex": 0,
            "explanation": {
                "en": "A flashing amber/yellow signal warns drivers of an intersection or hazard ahead; slow down and proceed carefully.",
                "te": "మెరిసే పసుపు సిగ్నల్ ప్రమాద సంకేతం. వేగం తగ్గించి జాగ్రత్తగా గమనిస్తూ ముందుకు వెళ్లాలి.",
                "hi": "चमकती पीली बत्ती चौराहे या खतरे का संकेत देती है; गति धीमी करें और सावधानी से आगे बढ़ें।"
            }
        },
        {
            "id": "TS_RS_003",
            "category": "road_signs",
            "signType": "mandatory",
            "questionNumber": 3,
            "image": "assets/signs/sign_003.png",
            "text": {
                "en": "A FLASHING RED LIGHT INDICATES",
                "te": "ఎరుపు రంగు లైట్ ఫ్లాష్ అవుతున్న ఒక జంక్షన్ ఎదురైనప్పుడు ఏం చేయాలి?",
                "hi": "चमकती लालबत्ती का मतलब"
            },
            "options": {
                "en": [
                    "STOP",
                    "BRIGHT SUN",
                    "STOP, OBSERVE AND PROCEED WITH CAUTION",
                    "NONE OF THE ABOVE"
                ],
                "te": [
                    "ఆగడానికి",
                    "ఎర్రటి సూర్యుడు",
                    "ఆగి చుట్టుప్రక్కల చూసి జాగ్రత్తగా వెళ్ళాలి",
                    "పైవి ఏవి కాదు"
                ],
                "hi": [
                    "रुकें",
                    "चमकता सूर्य",
                    "रुकें, देखें और सावधानी से आगे बढ़ें",
                    "इनमें से कोई भी नहीं"
                ]
            },
            "answerIndex": 2,
            "explanation": {
                "en": "A flashing red light requires coming to a complete stop, looking for traffic in all directions, and proceeding only when clear.",
                "te": "మెరిసే ఎరుపు లైట్ వద్ద వాహనాన్ని పూర్తిగా ఆపి, రోడ్డు క్లియర్ గా ఉందని నిర్ధారించుకున్నాకే వెళ్లాలి.",
                "hi": "चमकती लाल बत्ती पर पूरी तरह रुकें, सभी दिशाओं में देखें और सुरक्षित होने पर ही आगे बढ़ें।"
            }
        },
        {
            "id": "TS_RS_004",
            "category": "road_signs",
            "signType": "mandatory",
            "questionNumber": 4,
            "image": "assets/signs/sign_004.png",
            "text": {
                "en": "THE SIGNS MARKED IN THIS CIRCLE ARE..",
                "te": "ఈ ఆకారంలో ఉండే గుర్తు దేనిని సూచిస్తుంది",
                "hi": "वृत्ताकार चिन्ह का मतलब"
            },
            "options": {
                "en": [
                    "MANDATORY",
                    "CAUTIONARY",
                    "INFORMATORY",
                    "ALL OF THE ABOVE"
                ],
                "te": [
                    "తప్పనిసరి ఆదేశాలను",
                    "జాగ్రత్త పరిచేవి",
                    "సమాచారం కోసం",
                    "పైవి అన్నీ"
                ],
                "hi": [
                    "आवश्यक (अनिवार्य)",
                    "सावधान (चेतावनी)",
                    "सूचक (सूचनात्मक)",
                    "ये सभी"
                ]
            },
            "answerIndex": 0,
            "explanation": {
                "en": "Circular signs with red borders signify mandatory orders and prohibitions that drivers must legally obey.",
                "te": "ఎరుపు రంగు అంచుగల వృత్తాకార సంకేతాలు చట్టబద్ధంగా తప్పనిసరిగా పాటించాల్సిన ఆదేశాలు.",
                "hi": "लाल बॉर्डर वाले गोलाकार चिन्ह अनिवार्य आदेशों और निषेधों को दर्शाते हैं जिनका पालन कानूनन जरूरी है।"
            }
        },
        {
            "id": "TS_RS_005",
            "category": "road_signs",
            "signType": "cautionary",
            "questionNumber": 5,
            "image": "assets/signs/sign_005.png",
            "text": {
                "en": "THE SIGNS MARKED IN THIS TRIANGLE ARE..",
                "te": "త్రికోణంలో ఇచ్చిన గుర్తులు దేనికి సంకేతం",
                "hi": "त्रिकोण चिन्ह का मतलब"
            },
            "options": {
                "en": [
                    "MANDATORY",
                    "CAUTIONARY",
                    "INFORMATORY",
                    "ALL OF THE ABOVE"
                ],
                "te": [
                    "ఖచ్చితంగా పాటించాలి",
                    "జాగ్రత్త పరిచేవి",
                    "సమాచారం కోసం",
                    "పైవి అన్నీ"
                ],
                "hi": [
                    "आवश्यक",
                    "सावधान (चेतावनी)",
                    "सूचक",
                    "ये सभी"
                ]
            },
            "answerIndex": 1,
            "explanation": {
                "en": "Triangular signs with red borders are cautionary/warning signs indicating impending road hazards ahead.",
                "te": "ఎరుపు అంచుగల త్రిభుజాకార సంకేతాలు ముందున్న ప్రమాదాలు మరియు జాగ్రత్తలను హెచ్చరిస్తాయి.",
                "hi": "त्रिकोणीय चिन्ह चेतावनी या सावधानी के संकेत होते हैं जो आगे सड़क पर खतरों के प्रति सचेत करते हैं।"
            }
        },
        {
            "id": "TS_RS_006",
            "category": "road_signs",
            "signType": "informatory",
            "questionNumber": 6,
            "image": "assets/signs/sign_006.png",
            "text": {
                "en": "THE SIGNS MARKED IN THIS RECTANGLE ARE..",
                "te": "ఈ ఆకారంలో ఉండే గుర్తు దేనిని సూచిస్తుంది (చతురస్రం/దీర్ఘచతురస్రం)",
                "hi": "वर्गाकार/आयताकार चिन्ह का मतलब"
            },
            "options": {
                "en": [
                    "MANDATORY",
                    "CAUTIONARY",
                    "INFORMATORY",
                    "ALL OF THE ABOVE"
                ],
                "te": [
                    "తప్పనిసరి ఆదేశాలను",
                    "హెచ్చరికలు",
                    "సమాచారం కోసం",
                    "పైవి అన్నీ"
                ],
                "hi": [
                    "आवश्यक",
                    "सावधान",
                    "सूचक (जानकारी)",
                    "ये सभी"
                ]
            },
            "answerIndex": 2,
            "explanation": {
                "en": "Blue rectangular or square signs provide informatory guidance (directions, petrol pumps, hospitals, parking).",
                "te": "దీర్ఘచతురస్రాకార/చతురస్రాకార నీలం సంకేతాలు సమాచారం మరియు సౌకర్యాలను (ఆసుపత్రి, పెట్రోల్ పంప్) సూచిస్తాయి.",
                "hi": "नीले आयताकार या वर्गाकार चिन्ह सूचनात्मक मार्गदर्शन (अस्पताल, पेट्रोल पंप, दिशा) प्रदान करते हैं।"
            }
        }
    ]

if __name__ == '__main__':
    qs = get_road_signs()
    print("Road signs initial count:", len(qs))
