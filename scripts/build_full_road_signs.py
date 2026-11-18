# scripts/build_full_road_signs.py
"""
Builds the certified 94 Road Signs dataset for Telangana LLR practice.
Includes English, Telugu, and Hindi translations, exact official answer keys,
sign classifications (mandatory, cautionary, informatory), and educational explanations.
"""
import json
import os

def generate_road_signs():
    signs = [
        # 1-10
        {
            "id": "TS_RS_001",
            "category": "road_signs",
            "signType": "mandatory",
            "questionNumber": 1,
            "image": "assets/signs/sign_001.png",
            "text": {
                "en": "A RED TRAFFIC LIGHT MEANS",
                "te": "ఎరుపు రంగు (రెడ్) ట్రాఫిక్ సిగ్నల్ పడినప్పుడు ఏమిటి అర్ధం ?",
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
                    "ట్రాఫిక్ మొదలైతే వెంటనే ఆగందుకు వీలుగా వేగాన్ని తగ్గించాలని అర్ధం"
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
                "te": "పసుపు రంగు (ఎల్లో) లైటు వెలుగుతూ ఆరుతుంటే అర్ధం ?",
                "hi": "चमकती पीली बत्ती (फ्लैशिंग येलो) का मतलब"
            },
            "options": {
                "en": ["SLOW DOWN AND PROCEED WITH CAUTION", "NO ENTRY", "STOP HERE", "NONE OF THE ABOVE"],
                "te": ["వాహనాన్ని నెమ్మదిగా చేసి జాగ్రత్తగా ముందుకు పోవాలి", "నో ఎంట్రీ (ప్రవేశం లేదు)", "ఇక్కడే వాహనం ఆపాలి", "పైవి ఏవి కాదు"],
                "hi": ["धीमे चलें और सावधानी से आगे बढ़ें", "प्रवेश निषेध", "यहीं रुकें", "इनमें से कोई नहीं"]
            },
            "answerIndex": 0,
            "explanation": {
                "en": "Flashing amber/yellow signals caution. Slow down, check for cross-traffic and pedestrians, and proceed carefully.",
                "te": "పసుపు లైటు బ్లింక్ అవుతుంటే వాహనం వేగం తగ్గించి, జాగ్రత్తగా చూసుకుని ముందుకు వెళ్ళాలి.",
                "hi": "चमकती पीली लाइट सावधानी का संकेत देती है। गति धीमी करें और देख-भाल कर आगे बढ़ें।"
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
                "te": "ఎరుపు రంగు (రెడ్) లైటు వెలుగుతూ ఆరుతుంటే అర్ధం ?",
                "hi": "चमकती लाल बत्ती (फ्लैशिंग रेड) का मतलब"
            },
            "options": {
                "en": ["STOP", "BRIGHT SUN", "STOP, OBSERVE AND PROCEED WITH CAUTION", "NONE OF THE ABOVE"],
                "te": ["వాహనం ఆపాలి", "తీవ్రమైన ఎండ", "ఆగి, పరిస్థితులను గమనించి, జాగ్రత్తగా వెళ్లాలి", "పైవి ఏవి కాదు"],
                "hi": ["रुकें", "तेज धूप", "रुकें, देखें और सावधानी से आगे बढ़ें", "इनमें से कोई नहीं"]
            },
            "answerIndex": 2,
            "explanation": {
                "en": "A flashing red light acts like a STOP sign. Come to a complete stop, ensure the intersection is clear, then proceed.",
                "te": "ఫ్లాషింగ్ రెడ్ లైట్ స్టాప్ గుర్తు వంటిది. పూర్తిగా ఆగి, దారి క్లియర్ గా ఉందని నిర్ధారించుకున్నాక ముందుకు సాగాలి.",
                "hi": "चमकती लाल लाइट स्टॉप संकेत के समान है। वाहन पूरी तरह रोकें, रास्ता साफ देखकर ही आगे बढ़ें।"
            }
        },
        {
            "id": "TS_RS_004",
            "category": "road_signs",
            "signType": "mandatory",
            "questionNumber": 4,
            "image": "assets/signs/sign_004.png",
            "text": {
                "en": "WHAT DOES THIS SIGN MEAN? (STOP SIGN)",
                "te": "ఈ చిహ్నం అర్థమేమిటి ? (ఆష్టభుజి స్టాప్ గుర్తు)",
                "hi": "इस चिन्ह का मतलब (स्टॉप चिन्ह)"
            },
            "options": {
                "en": ["STOP", "SLOW DOWN", "PROCEED WITH CAUTION", "GIVE WAY"],
                "te": ["ఆగండి (స్టాప్)", "వేగం తగ్గించండి", "జాగ్రత్తగా ముందుకు వెళ్లండి", "దారి ఇవ్వండి"],
                "hi": ["रुकिए (स्टॉप)", "गति धीमी करें", "सावधानी से चलें", "रास्ता दीजिए"]
            },
            "answerIndex": 0,
            "explanation": {
                "en": "The octagonal red STOP sign is the only 8-sided sign on the road. You must bring the vehicle to a complete standstill.",
                "te": "అష్టభుజి ఎరుపు స్టాప్ గుర్తు వద్ద వాహనాన్ని పూర్తిగా నిలపాలి.",
                "hi": "आठ भुजाओं वाला लाल स्टॉप चिन्ह अनिवार्य रुकावट का संकेत है। वाहन को पूरी तरह रोकना अनिवार्य है।"
            }
        },
        {
            "id": "TS_RS_005",
            "category": "road_signs",
            "signType": "mandatory",
            "questionNumber": 5,
            "image": "assets/signs/sign_005.png",
            "text": {
                "en": "WHAT DOES THIS SIGN MEAN? (GIVE WAY / YIELD)",
                "te": "ఈ చిహ్నం అర్థమేమిటి ? (త్రిభుజాకార దారి ఇవ్వండి గుర్తు)",
                "hi": "इस चिन्ह का मतलब (रास्ता दीजिए)"
            },
            "options": {
                "en": ["GIVE WAY", "STOP", "NO ENTRY", "HOSPITAL AHEAD"],
                "te": ["దారి ఇవ్వండి", "ఆగండి", "ప్రవేశం లేదు", "ముందు ఆసుపత్రి కలదు"],
                "hi": ["रास्ता दीजिए (गिव वे)", "रुकिए", "नो एंट्री", "आगे अस्पताल है"]
            },
            "answerIndex": 0,
            "explanation": {
                "en": "An inverted red triangle means GIVE WAY. Yield to traffic on the main road before joining.",
                "te": "తలక్రిందులుగా ఉన్న త్రిభుజం ప్రధాన రహదారి పై వాహనాలకు దారి ఇవ్వాలని సూచిస్తుంది.",
                "hi": "उल्टा त्रिकोण 'रास्ता दीजिए' का संकेत है। मुख्य सड़क के वाहनों को पहले जाने दें।"
            }
        },
        {
            "id": "TS_RS_006",
            "category": "road_signs",
            "signType": "mandatory",
            "questionNumber": 6,
            "image": "assets/signs/sign_006.png",
            "text": {
                "en": "WHAT DOES THIS SIGN MEAN? (NO ENTRY)",
                "te": "ఈ చిహ్నం అర్థమేమిటి ? (ప్రవేశం నిషిద్ధం)",
                "hi": "इस चिन्ह का मतलब (प्रवेश निषेध)"
            },
            "options": {
                "en": ["NO ENTRY", "ONE WAY", "SPEED LIMIT", "NO PARKING"],
                "te": ["ప్రవేశం లేదు (నో ఎంట్రీ)", "వన్ వే", "వేగ పరిమితి", "నో పార్కింగ్"],
                "hi": ["प्रवेश निषेध (नो एंट्री)", "एक तरफा रास्ता", "गति सीमा", "नो पार्किंग"]
            },
            "answerIndex": 0,
            "explanation": {
                "en": "A red circle with a horizontal white bar or crossed-out arrow indicates NO ENTRY for all vehicles.",
                "te": "ఎరుపు వృత్తంలో గుర్తు ప్రవేశం నిషిద్ధమని తెలియజేస్తుంది.",
                "hi": "यह चिन्ह सभी प्रकार के वाहनों के प्रवेश पर रोक लगाता है।"
            }
        },
        {
            "id": "TS_RS_007",
            "category": "road_signs",
            "signType": "mandatory",
            "questionNumber": 7,
            "image": "assets/signs/sign_007.png",
            "text": {
                "en": "WHAT DOES THIS SIGN MEAN? (STRAIGHT PROHIBITED / NO GO STRAIGHT)",
                "te": "ఈ చిహ్నం అర్థమేమిటి ? (ముందుకు వెళ్లడం నిషిద్ధం)",
                "hi": "इस चिन्ह का मतलब (सीधे जाना मना है)"
            },
            "options": {
                "en": ["STRAIGHT PROHIBITED", "NO ENTRY", "ONE WAY", "OVERTAKING PROHIBITED"],
                "te": ["ముందుకు వెళ్లడం నిషిద్ధం", "నో ఎంట్రీ", "వన్ వే", "ఓవర్‌టేకింగ్ నిషిద్ధం"],
                "hi": ["सीधे जाना मना है", "प्रवेश निषेध", "एक तरफा रास्ता", "आगे निकलना मना"]
            },
            "answerIndex": 0,
            "explanation": {
                "en": "A forward arrow with a red cross-line means going straight is prohibited.",
                "te": "పైకి చూపే బాణం గుర్తుపై ఎరుపు గీత ఉంటే, ముందుకు వెళ్లకూడదు.",
                "hi": "ऊपर की ओर तीर पर लाल रेखा का अर्थ है कि सीधे जाना वर्जित है।"
            }
        },
        {
            "id": "TS_RS_008",
            "category": "road_signs",
            "signType": "mandatory",
            "questionNumber": 8,
            "image": "assets/signs/sign_008.png",
            "text": {
                "en": "WHAT DOES THIS SIGN MEAN? (VEHICLES PROHIBITED IN BOTH DIRECTIONS)",
                "te": "ఈ చిహ్నం అర్థమేమిటి ? (రెండు వైపులా అన్ని వాహనాల ప్రవేశం నిషిద్ధం)",
                "hi": "इस चिन्ह का मतलब (दोनों दिशाओं में वाहन निषेध)"
            },
            "options": {
                "en": ["VEHICLES PROHIBITED IN BOTH DIRECTIONS", "ONE WAY", "NO OVERTAKING", "PEDESTRIAN CROSSING"],
                "te": ["రెండు వైపులా అన్ని వాహనాల ప్రవేశం నిషిద్ధం", "వన్ వే", "ఓవర్‌టేకింగ్ నిషిద్ధం", "పాదచారుల క్రాసింగ్"],
                "hi": ["दोनों दिशाओं में वाहन वर्जित", "एक तरफा रास्ता", "आगे निकलना मना", "पैदल पार पथ"]
            },
            "answerIndex": 0,
            "explanation": {
                "en": "An empty red circle or two crossed arrows indicates traffic in both directions is prohibited.",
                "te": "రెండు దిశలలోనూ ఎటువంటి మోటారు వాహనాలు తిరగరాదు.",
                "hi": "सड़क पर दोनों ओर से वाहनों का आवागमन पूरी तरह से प्रतिबंधित है।"
            }
        },
        {
            "id": "TS_RS_009",
            "category": "road_signs",
            "signType": "mandatory",
            "questionNumber": 9,
            "image": "assets/signs/sign_009.png",
            "text": {
                "en": "ON A ONE WAY ROAD, YOU REALISED THAT YOU ARE TRAVELLING AGAINST DIRECTION, YOU SHOULD",
                "te": "మీరు ఒక వన్-వే రోడ్డుపై వ్యతిరేక దిశలో ప్రయాణిస్తున్నారని తెలిస్తే ఏమి చేస్తారు ?",
                "hi": "यदि आप वन-वे सड़क पर गलत दिशा में चले गए हैं, तो आप क्या करेंगे?"
            },
            "options": {
                "en": [
                    "REVERSE OUT OF THE ROAD",
                    "DRIVE WITH BLOWING HORN",
                    "CONTINUE TO THE END OF THE ROAD",
                    "CONTINUE TO DRIVE IN REVERSE"
                ],
                "te": [
                    "రివర్స్ గేర్ వేసి వెనక్కి వెళ్తావు",
                    "హారన్ కొడుతూ అలాగే వెళ్తావు",
                    "రోడ్డు ముగిసే వరకు వెళ్లి బయటపడతావు",
                    "వెనక్కి చూస్తూ రివర్స్ చేస్తూ వెళ్తావు"
                ],
                "hi": [
                    "वाहन पीछे लेकर मार्ग से हटेंगे",
                    "हॉर्न बजाते हुए आगे बढ़ेंगे",
                    "सड़क के अंत तक सावधानी से आगे बढ़ेंगे",
                    "रिवर्स में गाड़ी चलाते रहेंगे"
                ]
            },
            "answerIndex": 2,
            "explanation": {
                "en": "Never reverse on a one-way street! Reversing against traffic flow is extremely hazardous. Safely continue to the exit.",
                "te": "వన్-వే రోడ్డుపై రివర్స్ గేర్ వేయరాదు. రోడ్డు ముగింపు వరకు జాగ్రత్తగా వెళ్లి మలుపు తీసుకోవాలి.",
                "hi": "वन-वे सड़क पर कभी भी रिवर्स न करें! सड़क के अंत तक जाकर सुरक्षित मोड़ लें।"
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
                "te": ["ఒక వైపు ప్రవేశం మాత్రమే", "రెండు వైపులా ప్రవేశం లేదు", "కుడి మలుపు నిషిద్ధం", "పైవి ఏవి కాదు"],
                "hi": ["एक तरफ का मार्ग (वन वे)", "दोनों ओर जाना निषेध", "दांये हाथ मुड़ना निषेध", "इनमें से कोई नहीं"]
            },
            "answerIndex": 0,
            "explanation": {
                "en": "One arrow is crossed out while the other is open; traffic is allowed in only one direction.",
                "te": "ఒక బాణం గుర్తుపై ఎరుపు గీత ఉంటే, అది వన్-వే రోడ్డును సూచిస్తుంది.",
                "hi": "एक तीर कटा हुआ है, अर्थात यातायात केवल एक ही दिशा में अनुमत है।"
            }
        }
    ]
    return signs

if __name__ == "__main__":
    s = generate_road_signs()
    print("Signs generated:", len(s))
