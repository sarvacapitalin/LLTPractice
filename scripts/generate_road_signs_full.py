# scripts/generate_road_signs_full.py
import json, os

def get_signs_batch_1():
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
                "en": "A red traffic light is a mandatory stop signal. You must come to a complete stop behind the stop line.",
                "te": "ఎరుపు సిగ్నల్ తప్పనిసరి స్టాప్ సంకేతం. స్టాప్ లైన్ వెనుక వాహనాన్ని ఆపాలి.",
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
                "en": "A flashing yellow light warns drivers to slow down and enter the junction with extreme care.",
                "te": "మెరిసే పసుపు లైట్ వేగం తగ్గించి, జాగ్రత్తగా గమనిస్తూ ముందుకు వెళ్లాలని సూచిస్తుంది.",
                "hi": "चमकती पीली बत्ती गति धीमी करके सावधानी से आगे बढ़ने का निर्देश देती है।"
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
                "en": "Flashing red requires a complete stop like a stop sign. Yield right of way, then go when safe.",
                "te": "ఫ్లాషింగ్ రెడ్ వద్ద తప్పక ఆగి, ట్రాఫిక్ గమనించి సురక్షితంగా వెళ్లాలి.",
                "hi": "चमकती लाल बत्ती पर पहले रुकें, सभी तरफ देखें और रास्ता साफ होने पर ही बढ़ें।"
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
                "te": "ఈ ఆకారంలో ఉండే గుర్తు దేనిని సూచిస్తుంది (వృత్తాకారం)",
                "hi": "वृत्ताकार चिन्ह का मतलब"
            },
            "options": {
                "en": ["MANDATORY", "CAUTIONARY", "INFORMATORY", "ALL OF THE ABOVE"],
                "te": ["తప్పనిసరి ఆదేశాలను", "జాగ్రత్త పరిచేవి", "సమాచారం కోసం", "పైవి అన్నీ"],
                "hi": ["आवश्यक (अनिवार्य)", "सावधान", "सूचक", "ये सभी"]
            },
            "answerIndex": 0,
            "explanation": {
                "en": "Circular signs indicate mandatory traffic laws and prohibitions.",
                "te": "వృత్తాకార సంకేతాలు చట్టపరంగా తప్పనిసరి నిబంధనలు.",
                "hi": "गोलाकार चिन्ह अनिवार्य यातायात नियमों को दर्शाते हैं।"
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
                "en": ["MANDATORY", "CAUTIONARY", "INFORMATORY", "ALL OF THE ABOVE"],
                "te": ["ఖచ్చితంగా పాటించాలి", "జాగ్రత్త పరిచేవి", "సమాచారం కోసం", "పైవి అన్నీ"],
                "hi": ["आवश्यक", "सावधान (चेतावनी)", "सूचक", "ये सभी"]
            },
            "answerIndex": 1,
            "explanation": {
                "en": "Triangular signs warn motorists of upcoming hazards or changes in road conditions.",
                "te": "త్రిభుజాకార సంకేతాలు రోడ్డుపై ప్రమాదాలు మరియు హెచ్చరికలను తెలుపుతాయి.",
                "hi": "त्रिकोणीय चिन्ह आगे आने वाले खतरों या सड़क की स्थिति के प्रति आगाह करते हैं।"
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
                "hi": "वर्गाकार चिन्ह का मतलब"
            },
            "options": {
                "en": ["MANDATORY", "CAUTIONARY", "INFORMATORY", "ALL OF THE ABOVE"],
                "te": ["తప్పనిసరి ఆదేశాలను", "హెచ్చరికలు", "సమాచారం కోసం", "పైవి అన్నీ"],
                "hi": ["आवश्यक", "सावधान", "सूचक (जानकारी)", "ये सभी"]
            },
            "answerIndex": 2,
            "explanation": {
                "en": "Rectangular signs provide informatory guidance and public facility locations.",
                "te": "దీర్ఘచతురస్రాకార సంకేతాలు సమాచారం మరియు సౌకర్యాలను సూచిస్తాయి.",
                "hi": "आयताकार चिन्ह सूचना और सुविधाओं की जानकारी देते हैं।"
            }
        },
        {
            "id": "TS_RS_007",
            "category": "road_signs",
            "signType": "mandatory",
            "questionNumber": 7,
            "image": "assets/signs/sign_007.png",
            "text": {
                "en": "WHAT DOES THIS SIGN MEAN? (STOP)",
                "te": "ఈ చిహ్నం అర్థమేమిటి ? (ఆగండి - అష్టభుజి)",
                "hi": "इस चिन्ह का मतलब (रुकें)"
            },
            "options": {
                "en": ["STOP", "ONE WAY SIGN", "NO PARKING", "NO STOPPING"],
                "te": ["ఆగండి", "ఒక ప్రక్కమాత్రమే వెళ్ళాలి", "వాహనాలు నిలుపరాదు", "ఇక్కడ ఆగరాదు"],
                "hi": ["रुकें", "एक दिशा में जाने का चिन्ह", "पार्किंग नहीं", "रुकें नहीं"]
            },
            "answerIndex": 0,
            "explanation": {
                "en": "The octagonal red STOP sign requires a complete halt before proceeding.",
                "te": "ఎనిమిది కోణాల ఎరుపు గుర్తు 'ఆగండి' (STOP) ని సూచిస్తుంది.",
                "hi": "अष्टकोणीय लाल चिन्ह 'रुकें' (STOP) का अनिवार्य संकेत है।"
            }
        },
        {
            "id": "TS_RS_008",
            "category": "road_signs",
            "signType": "mandatory",
            "questionNumber": 8,
            "image": "assets/signs/sign_008.png",
            "text": {
                "en": "WHAT DOES THIS SIGN MEAN? (GIVE WAY)",
                "te": "ఈ చిహ్నం అర్థమేమిటి ? (దారి ఇవ్వండి - తలక్రిందుల త్రిభుజం)",
                "hi": "इस चिन्ह का मतलब (रास्ता दें)"
            },
            "options": {
                "en": ["LEFT HAND CURVE", "INFORMATORY", "WARNING SIGN", "GIVE WAY"],
                "te": ["ఎడమ చేతి మలుపు", "సమాచారం కోసం", "హెచ్చరిక గుర్తు", "దారి ఇవ్వాలి"],
                "hi": ["बायें हाथ की ओर मोड़ है", "सूचक", "सावधान का चिन्ह", "जाने के लिए मार्ग दें (रास्ता दें)"]
            },
            "answerIndex": 3,
            "explanation": {
                "en": "An inverted triangle is the GIVE WAY sign. Yield right of way to traffic on the main road.",
                "te": "తలక్రిందులుగా ఉన్న త్రిభుజం 'దారి ఇవ్వండి' (GIVE WAY) సంకేతం.",
                "hi": "उलटा त्रिकोण 'रास्ता दें' (GIVE WAY) का अनिवार्य संकेत है।"
            }
        },
        {
            "id": "TS_RS_009",
            "category": "road_signs",
            "signType": "mandatory",
            "questionNumber": 9,
            "image": "assets/signs/sign_009.png",
            "text": {
                "en": "YOU MISSED YOUR WAY AND FIND YOU ARE ON A ONE-WAY STREET. YOU SHOULD",
                "te": "నువ్వు రోడ్డు మధ్యలోకి వెళ్ళాక నువ్వు ఒక వైపు మాత్రమే ప్రవేశం ఉన్న రోడ్డులో ఉన్నావని తెలుసుకున్నావు. అప్పుడు నువ్వు ఏమిచేస్తావు",
                "hi": "रास्ता भटक गये हैं और आप एक सड़क के किनारे पर है, तो आप ये करेंगे"
            },
            "options": {
                "en": [
                    "REVERSE OUT OF THE ROAD",
                    "BLOW YOUR HORN AND DRIVE",
                    "CONTINUE TO THE END OF THE ROAD",
                    "REVERSE INTO A DRIVEWAY"
                ],
                "te": [
                    "ఆ రోడ్డు నుండి వెనుకకు తిరిగి వస్తావు",
                    "హారన్ కొట్టుకుంటూ ముందుకు వెళ్తావు",
                    "రోడ్డు చివరకు వెళ్తావు",
                    "అనుమతించిన రోడ్డులోకి మారతావు"
                ],
                "hi": [
                    "वाहन पीछे लेकर मार्ग से हटेंगे",
                    "हॉर्न बजाते हुए चलायेंगे",
                    "सड़क के खत्म होने तक जारी रखेंगे (सड़क के अंत तक चलेंगे)",
                    "पीछे लेकर चलते रहेंगे"
                ]
            },
            "answerIndex": 2,
            "explanation": {
                "en": "Never reverse on a one-way street! Safely continue to the end of the road and turn properly.",
                "te": "వన్-వే రోడ్డుపై ఎప్పుడూ రివర్స్ చేయకూడదు. రోడ్డు చివరి వరకు ముందుకు వెళ్లి మలుపు తీసుకోవాలి.",
                "hi": "वन-वे सड़क पर कभी रिवर्स न करें! सड़क के अंत तक आगे बढ़कर ही मुड़ें।"
            }
        },
        {
            "id": "TS_RS_010",
            "category": "road_signs",
            "signType": "mandatory",
            "questionNumber": 10,
            "image": "assets/signs/sign_010.png",
            "text": {
                "en": "WHAT DOES THIS SIGN MEAN? (ONE WAY)",
                "te": "ఈ చిహ్నం అర్థమేమిటి ? (వన్ వే - ఒక వైపు మాత్రమే ప్రవేశం)",
                "hi": "इस चिन्ह का मतलब (एक तरफा रास्ता)"
            },
            "options": {
                "en": ["ONE WAY", "BOTH WAYS PROHIBITED", "RIGHT TURN PROHIBITED", "NONE OF THE ABOVE"],
                "te": ["ఒక వైపు ప్రవేశం మాత్రమే", "రెండు వైపులా ఎటువంటి వాహనాలకు ప్రవేశం లేదు", "కుడి మలుపు నిషిద్ధం", "పైవి ఏవి కాదు"],
                "hi": ["एक तरफ का मार्ग (वन वे)", "दोनों ओर जाना निषेध", "दांये हाथ मुड़ना निषेध", "इनमें से कोई नहीं"]
            },
            "answerIndex": 0,
            "explanation": {
                "en": "One arrow is crossed out; movement is allowed only in the direction of the open arrow.",
                "te": "ఒక బాణం గుర్తుపై ఎరుపు గీత ఉంటే, అది వన్-వే రోడ్డును సూచిస్తుంది.",
                "hi": "एक तीर कटा हुआ है, अर्थात यातायात केवल एक ही दिशा में अनुमत है।"
            }
        }
    ]
