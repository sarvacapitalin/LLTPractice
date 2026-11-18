import json
import os

def fix_all():
    # ----------------------------------------------------
    # 1. FIX ROAD SIGNS
    # ----------------------------------------------------
    signs_path = "data/questions/telangana/road-signs.json"
    with open(signs_path) as f:
        signs = json.load(f)

    # Dictionary of clean corrections for road signs: (qNum -> {options: {en, te, hi}, answerIndex, explanation})
    clean_signs = {
        10: {
            "options": {
                "en": ["ONE WAY", "BOTH WAYS PROHIBITED", "RIGHT TURN PROHIBITED", "NONE OF THE ABOVE"],
                "te": ["వన్ వే (ఏకముఖ మార్గం)", "రెండు వైపులా ప్రవేశం నిషేధం", "కుడి వైపు మలుపు నిషేధం", "పైవేవీ కావు"],
                "hi": ["एकतरफा रास्ता (वन वे)", "दोनों ओर यातायात निषेध", "दाएं मुड़ना मना है", "इनमें से कोई नहीं"]
            },
            "answerIndex": 0,
            "explanation": {"en": "Arrow pointing forward indicates One Way traffic.", "te": "ముందుకు చూపే బాణం ఏకముఖ మార్గాన్ని (వన్ వే) సూచిస్తుంది.", "hi": "आगे तीर का निशान एकतरफा यातायात (वन वे) को दर्शाता है।"}
        },
        17: {
            "options": {
                "en": ["NO SMOKING", "RIGHT TURN PROHIBITED", "CYCLE PROHIBITED", "HORN PROHIBITED"],
                "te": ["ధూమపానం నిషేధం", "కుడి వైపు మలుపు నిషేధం", "సైకిల్ ప్రవేశం నిషేధం", "హారన్ మోగించడం నిషేధం"],
                "hi": ["धूम्रपान निषेध", "दाएं मुड़ना मना है", "साइकिल निषेध", "हॉर्न बजाना मना है"]
            },
            "answerIndex": 3,
            "explanation": {"en": "Horn symbol with a red cross slash means Horn Prohibited (Silence Zone).", "te": "హారన్ గుర్తుపై ఎరుపు అడ్డగీత హారన్ మోగించరాదని (సైలెన్స్ జోన్) సూచిస్తుంది.", "hi": "हॉर्न पर लाल कट का निशान हॉर्न बजाने की मनाही (साइलेंस जोन) दर्शाता है।"}
        },
        21: {
            "options": {
                "en": ["NO STOPPING", "RESTRICTION ENDS SIGN", "NO PARKING", "SPEED LIMIT"],
                "te": ["వాహనాన్ని ఆపరాదు (నో స్టాపింగ్)", "ఆంక్షల ముగింపు చిహ్నం", "నో పార్కింగ్ (పార్కింగ్ నిషేధం)", "వేగ పరిమితి"],
                "hi": ["रुकना मना है (नो स्टॉपिंग)", "प्रतिबंध समाप्ति चिन्ह", "नो पार्किंग (पार्किंग मना है)", "गति सीमा"]
            },
            "answerIndex": 2,
            "explanation": {"en": "Blue circle with a single diagonal red slash indicates No Parking.", "te": "ఒకే ఎరుపు అడ్డగీత గల నీలి వృత్తం నో పార్కింగ్ సూచిస్తుంది.", "hi": "नीले वृत्त पर एक तिरछी लाल रेखा नो पार्किंग को दर्शाती है।"}
        },
        24: {
            "options": {
                "en": ["LENGTH LIMIT", "SPEED LIMIT", "LOAD LIMIT", "HEIGHT LIMIT"],
                "te": ["పొడవు పరిమితి", "వేగ పరిమితి", "బరువు / లోడ్ పరిమితి", "ఎత్తు పరిమితి"],
                "hi": ["लंबाई सीमा", "गति सीमा", "भार सीमा", "ऊंचाई सीमा"]
            },
            "answerIndex": 0,
            "explanation": {"en": "Number followed by 'm' between horizontal arrows indicates Length Limit.", "te": "రెండు బాణాల మధ్య మీటర్లలో చూపిన సంఖ్య వాహనం పొడవు పరిమితిని సూచిస్తుంది.", "hi": "दो क्षैतिज तीरों के बीच मीटर में संख्या वाहन की लंबाई सीमा दर्शाती है।"}
        },
        31: {
            "options": {
                "en": ["COMPULSORY KEEP LEFT", "COMPULSORY AHEAD ONLY", "COMPULSORY TURN LEFT", "COMPULSORY TURN RIGHT"],
                "te": ["తప్పనిసరిగా ఎడమ వైపునే వెళ్లాలి", "తప్పనిసరిగా తిన్నగా ముందుకు వెళ్లాలి", "తప్పనిసరిగా ఎడమ వైపు మలగాలి", "తప్పనిసరిగా కుడి వైపు మలగాలి"],
                "hi": ["अनिवार्य रूप से बाएं चलें", "अनिवार्य रूप से केवल सीधे जाएं", "अनिवार्य रूप से बाएं मुड़ें", "अनिवार्य रूप से दाएं मुड़ें"]
            },
            "answerIndex": 1,
            "explanation": {"en": "Vertical white arrow on a blue circular disc means Compulsory Ahead Only.", "te": "నీలి వృత్తంలో పైకి చూపే తెల్లటి బాణం తప్పనిసరిగా తిన్నగా మాత్రమే వెళ్లాలని సూచిస్తుంది.", "hi": "नीले वृत्त में सीधा तीर अनिवार्य रूप से केवल आगे जाने का निर्देश देता है।"}
        },
        38: {
            "options": {
                "en": ["COMPULSORY SOUND HORN", "HORN PROHIBITED", "NO SMOKING", "NONE OF THE ABOVE"],
                "te": ["తప్పనిసరిగా హారన్ మోగించాలి", "హారన్ మోగించడం నిషేధం", "ధూమపానం నిషేధం", "పైవేవీ కావు"],
                "hi": ["अनिवार्य रूप से हॉर्न बजाएं", "हॉर्न बजाना मना है", "धूम्रपान निषेध", "इनमें से कोई नहीं"]
            },
            "answerIndex": 0,
            "explanation": {"en": "White horn on blue circular disc signifies Compulsory Sound Horn (e.g. sharp blind curves).", "te": "నీలి వృత్తంలో తెల్లటి హారన్ గుర్తు తప్పనిసరిగా హారన్ మోగించాలని సూచిస్తుంది.", "hi": "नीले वृत्त पर सफेद हॉर्न का चिन्ह अनिवार्य रूप से हॉर्न बजाने का संकेत देता है।"}
        },
        45: {
            "options": {
                "en": ["RIGHT HAND CURVE", "LEFT REVERSE BEND", "RIGHT REVERSE BEND", "HAIR PIN BEND RIGHT"],
                "te": ["కుడి వైపు మలుపు", "ఎడమ రివర్స్ బెండ్", "కుడి రివర్స్ బెండ్", "కుడి వైపు హెయిర్ పిన్ మలుపు"],
                "hi": ["दाहिना मोड़", "बायां रिवर्स मोड़", "दाहिना रिवर्स मोड़", "दाहिना हेयर पिन मोड़"]
            },
            "answerIndex": 2,
            "explanation": {"en": "Z-shaped arrow bending first to right then to left denotes Right Reverse Bend.", "te": "మొదట కుడికి తర్వాత ఎడమకు తిరిగే Z-ఆకారపు బాణం కుడి రివర్స్ బెండ్ సూచిస్తుంది.", "hi": "पहले दाएं फिर बाएं मुड़ने वाला Z-आकार का तीर दाहिना रिवर्स मोड़ दर्शाता है।"}
        },
        46: {
            "options": {
                "en": ["STEEP DESCENT", "STEEP ASCENT", "SLIPPERY ROAD", "HUMP OR ROUGH ROAD"],
                "te": ["తీవ్రమైన లోయ / క్రిందికి దిగుడు", "తీవ్రమైన ఎత్తు / ఎక్కుడు రోడ్డు", "జారే రోడ్డు (స్లిప్పరీ రోడ్డు)", "స్పీడ్ బ్రేకర్ లేదా గరుకు రోడ్డు"],
                "hi": ["तीव्र ढलान (नीचे की ओर)", "तीव्र चढ़ाई (ऊपर की ओर)", "फिसलन भरी सड़क", "गति अवरोधक या ऊबड़-खाबड़ सड़क"]
            },
            "answerIndex": 1,
            "explanation": {"en": "Vehicle ascending a triangular ramp denotes Steep Ascent ahead.", "te": "పైకి ఎక్కుతున్న వాహనం తీవ్రమైన ఎక్కుడు రోడ్డును సూచిస్తుంది.", "hi": "ऊपर चढ़ता हुआ वाहन आगे तीव्र चढ़ाई का संकेत देता है।"}
        },
        47: {
            "options": {
                "en": ["STEEP ASCENT", "STEEP DESCENT", "NARROW ROAD AHEAD", "NARROW BRIDGE"],
                "te": ["తీవ్రమైన ఎత్తు రోడ్డు", "తీవ్రమైన దిగుడు రోడ్డు", "ముందు ఇరుకైన రోడ్డు కలదు", "ముందు ఇరుకైన వంతెన కలదు"],
                "hi": ["तीव्र चढ़ाई", "तीव्र ढलान", "आगे संकरा रास्ता है", "आगे संकरा पुल है"]
            },
            "answerIndex": 1,
            "explanation": {"en": "Vehicle descending a triangular ramp denotes Steep Descent ahead.", "te": "క్రిందికి దిగుతున్న వాహనం తీవ్రమైన దిగుడు రోడ్డును సూచిస్తుంది.", "hi": "नीचे उतरता हुआ वाहन आगे तीव्र ढलान का संकेत देता है।"}
        },
        48: {
            "options": {
                "en": ["NARROW ROAD AHEAD", "ROAD WIDENS AHEAD", "NARROW BRIDGE", "SLIPPERY ROAD"],
                "te": ["ముందు ఇరుకైన రోడ్డు కలదు", "ముందు వెడల్పైన రోడ్డు కలదు", "ముందు ఇరుకైన వంతెన కలదు", "జారే రోడ్డు"],
                "hi": ["आगे संकरा रास्ता है", "आगे चौड़ा रास्ता है", "आगे संकरा पुल है", "फिसलन भरी सड़क"]
            },
            "answerIndex": 0,
            "explanation": {"en": "Roadway contour narrowing symmetrically indicates Narrow Road Ahead.", "te": "రోడ్డు మార్గం ఇరుకుగా మారడం ముందు ఇరుకైన రోడ్డు ఉందని సూచిస్తుంది.", "hi": "सड़क का संकरा होना आगे संकरे रास्ते का संकेत है।"}
        },
        49: {
            "options": {
                "en": ["NARROW ROAD AHEAD", "ROAD WIDENS AHEAD", "NARROW BRIDGE", "SLIPPERY ROAD"],
                "te": ["ముందు ఇరుకైన రోడ్డు కలదు", "ముందు వెడల్పైన రోడ్డు కలదు", "ముందు ఇరుకైన వంతెన కలదు", "జారే రోడ్డు"],
                "hi": ["आगे संकरा रास्ता है", "आगे चौड़ा रास्ता है", "आगे संकरा पुल है", "फिसलन भरी सड़क"]
            },
            "answerIndex": 1,
            "explanation": {"en": "Roadway lines spreading apart indicates Road Widens Ahead.", "te": "రోడ్డు మార్గం వెడల్పుగా మారడం ముందు వెడల్పైన రోడ్డు ఉందని సూచిస్తుంది.", "hi": "सड़क का चौड़ा होना आगे चौड़े रास्ते का संकेत है।"}
        },
        50: {
            "options": {
                "en": ["ROAD WIDENS AHEAD", "NARROW ROAD AHEAD", "NARROW BRIDGE", "SLIPPERY ROAD"],
                "te": ["ముందు వెడల్పైన రోడ్డు కలదు", "ముందు ఇరుకైన రోడ్డు కలదు", "ముందు ఇరుకైన వంతెన కలదు", "జారే రోడ్డు"],
                "hi": ["आगे चौड़ा रास्ता है", "आगे संकरा रास्ता है", "आगे संकरा पुल है", "फिसलन भरी सड़क"]
            },
            "answerIndex": 2,
            "explanation": {"en": "Road narrowing abruptly over parallel bridge barriers indicates Narrow Bridge.", "te": "వంతెన బారికేడ్ల వద్ద రోడ్డు ఇరుకుగా మారడం ఇరుకైన వంతెనను సూచిస్తుంది.", "hi": "पुल के पास सड़क का संकरा होना आगे संकरे पुल का संकेत है।"}
        },
        52: {
            "options": {
                "en": ["NARROW BRIDGE", "SLIPPERY ROAD", "LOOSE GRAVEL", "STEEP DESCENT"],
                "te": ["ముందు ఇరుకైన వంతెన కలదు", "జారే రోడ్డు (స్లిప్పరీ రోడ్డు)", "రోడ్డుపై చిన్న రాళ్లు / కంకర (లూజ్ గ్రావెల్)", "తీవ్రమైన దిగుడు రోడ్డు"],
                "hi": ["आगे संकरा पुल है", "फिसलन भरी सड़क", "बिखरी बजरी / कंकर (लूज बजरी)", "तीव्र ढलान"]
            },
            "answerIndex": 2,
            "explanation": {"en": "Car with gravel flinging from rear tire signifies Loose Gravel on road surface.", "te": "టైర్ల నుండి కంకర రాళ్లు ఎగిరే గుర్తు రోడ్డుపై వదులైన కంకర రాళ్లు ఉన్నాయని సూచిస్తుంది.", "hi": "टायर से बजरी उछलने का चिन्ह सड़क पर बिखरी बजरी का संकेत देता है।"}
        },
        53: {
            "options": {
                "en": ["SCHOOL AHEAD", "MEN AT WORK", "CYCLE CROSSING", "PEDESTRIAN CROSSING"],
                "te": ["ముందు పాఠశాల కలదు", "రోడ్డు పనులు జరుగుచున్నవి", "సైకిల్ క్రాసింగ్", "పాదచారుల క్రాసింగ్ (జీబ్రా క్రాసింగ్)"],
                "hi": ["आगे स्कूल है", "सड़क पर काम चल रहा है", "साइकिल क्रॉसिंग", "पैदल यात्री क्रॉसिंग (जेब्रा क्रॉसिंग)"]
            },
            "answerIndex": 3,
            "explanation": {"en": "Person walking on zebra crossing within triangle means Pedestrian Crossing ahead.", "te": "జీబ్రా గీతలపై నడిచే వ్యక్తి గుర్తు పాదచారుల క్రాసింగ్ కలదని సూచిస్తుంది.", "hi": "जेब्रा क्रॉसिंग पर चलता व्यक्ति पैदल यात्री क्रॉसिंग को दर्शाता है।"}
        },
        54: {
            "options": {
                "en": ["CYCLE CROSSING", "SCHOOL AHEAD", "LOOSE GRAVEL", "PEDESTRIAN CROSSING"],
                "te": ["సైకిల్ క్రాసింగ్", "ముందు పాఠశాల కలదు (పిల్లలు జాగ్రత్త)", "రోడ్డుపై వదులైన కంకర", "పాదచారుల క్రాసింగ్"],
                "hi": ["साइकिल क्रॉसिंग", "आगे स्कूल है (बच्चे सावधान)", "बिखरी बजरी", "पैदल यात्री क्रॉसिंग"]
            },
            "answerIndex": 1,
            "explanation": {"en": "School children running with bags denotes School Ahead.", "te": "బ్యాగులతో పరిగెత్తే పిల్లల గుర్తు ముందు పాఠశాల కలదని సూచిస్తుంది.", "hi": "बस्ता लेकर भागते बच्चों का चिन्ह आगे स्कूल होने का संकेत देता है।"}
        },
        55: {
            "options": {
                "en": ["BARRIER AHEAD", "DANGEROUS DIP", "MEN AT WORK", "MAJOR ROAD AHEAD"],
                "te": ["ముందు బారికేడ్ / చెక్\u200cపోస్ట్ కలదు", "ప్రమాదకరమైన గుంత", "రోడ్డు పనులు జరుగుచున్నవి (మెన్ ఎట్ వర్క్)", "ముందు ప్రధాన రహదారి కలదు"],
                "hi": ["आगे बैरियर / चेकपोस्ट है", "खतरनाक गड्ढा", "सड़क पर काम चल रहा है", "आगे मुख्य सड़क है"]
            },
            "answerIndex": 2,
            "explanation": {"en": "Worker digging road denotes Men At Work ahead.", "te": "రోడ్డు తవ్వుతున్న వ్యక్తి గుర్తు రోడ్డు పనులు జరుగుతున్నాయని సూచిస్తుంది.", "hi": "सड़क पर काम करता मजदूर आगे निर्माण कार्य का संकेत देता है।"}
        },
        56: {
            "options": {
                "en": ["FALLING ROCKS", "STEEP ASCENT", "HUMP OR ROUGH ROAD", "LOOSE GRAVEL"],
                "te": ["కొండ చరియలు / రాళ్లు విరిగిపడే ప్రమాదం", "తీవ్రమైన ఎక్కుడు రోడ్డు", "స్పీడ్ బ్రేకర్ లేదా గరుకు రోడ్డు", "రోడ్డుపై వదులైన కంకర"],
                "hi": ["चट्टानें गिरने का खतरा", "तीव्र चढ़ाई", "ऊबड़-खाबड़ सड़क", "बिखरी बजरी"]
            },
            "answerIndex": 0,
            "explanation": {"en": "Rocks sliding down hillside denotes Falling Rocks danger zone.", "te": "కొండ నుండి రాళ్లు జారే గుర్తు కొండ చరియలు విరిగిపడే ప్రమాదాన్ని సూచిస్తుంది.", "hi": "पहाड़ी से गिरती चट्टानों का चिन्ह चट्टानें गिरने के खतरे को दर्शाता है।"}
        },
        59: {
            "options": {
                "en": ["STAGGERED INTERSECTION", "ROUND ABOUT", "CROSS ROAD", "SIDE ROAD LEFT"],
                "te": ["స్టాగర్డ్ జంక్షన్", "రౌండ్‌ఎబౌట్ (వృత్తాకార కూడలి)", "క్రాస్ రోడ్స్ (నాలుగు రోడ్ల కూడలి)", "ఎడమ వైపు సైడ్ రోడ్డు"],
                "hi": ["विषम चौराहा (स्टैगर्ड जंक्शन)", "गोल चक्कर (राउंडअबाउट)", "चौराहा (चार सड़कें)", "बाएं पार्श्व सड़क"]
            },
            "answerIndex": 1,
            "explanation": {"en": "Circular arrows in clockwise/anti-clockwise formation indicates Roundabout ahead.", "te": "వృత్తాకార బాణాలు ముందు రౌండ్‌ఎబౌట్ (ట్రాఫిక్ ఐలాండ్) ఉందని సూచిస్తాయి.", "hi": "वृत्ताकार तीर आगे गोल चक्कर (चौराहा) होने का संकेत देते हैं।"}
        },
        66: {
            "options": {
                "en": ["ROUND ABOUT", "CROSS ROADS", "Y-INTERSECTION", "ROAD OPEN"],
                "te": ["రౌండ్‌ఎబౌట్", "క్రాస్ రోడ్స్", "వై-జంక్షన్ (Y-ఆకారపు కూడలి)", "రోడ్డు తెరిచి ఉంది"],
                "hi": ["गोल चक्कर", "चौराहा", "वाई-इंटरसेक्शन (Y-आकार का जंक्शन)", "सड़क खुली है"]
            },
            "answerIndex": 2,
            "explanation": {"en": "Y-shaped road bifurcation indicates Y-Intersection ahead.", "te": "Y-ఆకారపు రోడ్డు విభజన వై-జంక్షన్ ను సూచిస్తుంది.", "hi": "Y-आकार का सड़क विभाजन आगे वाई-जंक्शन का संकेत है।"}
        },
        75: {
            "options": {
                "en": ["EATING PLACE", "LIGHT REFRESHMENT", "RESTING PLACE", "ALL OF THE ABOVE"],
                "te": ["భోజన శాల (ఈటింగ్ ప్లేస్)", "అల్పాహార శాల (టీ/కాఫీ)", "విశ్రాంతి గది", "పైవన్నీ"],
                "hi": ["भोजन स्थल (रेस्टोरेंट)", "अल्पाहार (चाय/नाश्ता)", "विश्राम स्थल", "उपरोक्त सभी"]
            },
            "answerIndex": 0,
            "explanation": {"en": "Fork and spoon informational sign indicates Eating Place.", "te": "స్పూన్ మరియు ఫోర్క్ గుర్తు భోజన శాలను (హోటల్/రెస్టారెంట్) సూచిస్తుంది.", "hi": "कांटा और चम्मच का चिन्ह भोजन स्थल (रेस्टोरेंट) को दर्शाता है।"}
        },
        76: {
            "options": {
                "en": ["HOSPITAL", "RESTING PLACE", "LIGHT REFRESHMENT", "ALL OF THE ABOVE"],
                "te": ["ఆసుపత్రి", "విశ్రాంతి ప్రదేశం", "అల్పాహార శాల", "పైవన్నీ"],
                "hi": ["अस्पताल", "विश्राम स्थल", "अल्पाहार स्थल", "उपरोक्त सभी"]
            },
            "answerIndex": 1,
            "explanation": {"en": "Person lying on bed informational sign indicates Resting Place / Motel.", "te": "మంచంపై వ్యక్తి ఉన్న గుర్తు విశ్రాంతి ప్రదేశం లేదా మోటెల్ ను సూచిస్తుంది.", "hi": "बिस्तर पर लेटे व्यक्ति का चिन्ह विश्राम स्थल को दर्शाता है।"}
        },
        81: {
            "options": {
                "en": ["POST OFFICE", "NO PARKING", "PARK THIS SIDE", "NONE OF THE ABOVE"],
                "te": ["తపాలా కార్యాలయం (పోస్ట్ ఆఫీస్)", "నో పార్కింగ్", "ఈ వైపున పార్క్ చేయవచ్చు", "పైవేవీ కావు"],
                "hi": ["डाकघर", "नो पार्किंग", "इस तरफ पार्क करें", "इनमें से कोई नहीं"]
            },
            "answerIndex": 2,
            "explanation": {"en": "'P' with arrow pointing to one side indicates Park This Side.", "te": "P గుర్తుతో పాటు ఒక వైపు చూపే బాణం ఆ వైపున పార్కింగ్ చేయవచ్చని తెలుపుతుంది.", "hi": "P चिन्ह के साथ तीर इस तरफ वाहन पार्क करने की अनुमति दर्शाता है।"}
        },
        94: {
            "options": {
                "en": [
                    "YOU MUST NOT CROSS THESE LINES TO OVERTAKE OR MAKE A U-TURN",
                    "YOU CAN CHANGE LANE WITH CAUTION",
                    "ONE WAY ROAD",
                    "NONE OF THE ABOVE"
                ],
                "te": [
                    "ఓవర్‌టేక్ చేయడానికి లేదా యు-టర్న్ తీసుకోవడానికి ఈ గీతలను ఎట్టి పరిస్థితుల్లోనూ దాటరాదు",
                    "జాగ్రత్తగా లేన్ మార్చవచ్చు",
                    "ఏకముఖ రహదారి",
                    "పైవేవీ కావు"
                ],
                "hi": [
                    "ओवरटेक करने या यू-टर्न लेने के लिए इन रेखाओं को कतई पार न करें",
                    "सावधानी से लेन बदल सकते हैं",
                    "एकतरफा सड़क",
                    "इनमें से कोई नहीं"
                ]
            },
            "answerIndex": 0,
            "explanation": {"en": "Two solid yellow lines down the center mean strict prohibition of crossing to overtake or turn.", "te": "రోడ్డు మధ్యలో ఉన్న రెండు వరుస పసుపు గీతలను ఓవర్‌టేక్ లేదా మలుపు కోసం ఎట్టి పరిస్థితుల్లోనూ దాటరాదు.", "hi": "सड़क के बीच में दो ठोस पीली रेखाओं को ओवरटेक या मुड़ने के लिए पार करना सख्त मना है।"}
        }
    }

    # Apply fixes to road signs
    fixed_signs_count = 0
    for s in signs:
        qnum = s["questionNumber"]
        if qnum in clean_signs:
            corr = clean_signs[qnum]
            s["options"] = corr["options"]
            s["answerIndex"] = corr["answerIndex"]
            s["explanation"] = corr["explanation"]
            fixed_signs_count += 1

    with open(signs_path, "w") as f:
        json.dump(signs, f, indent=2, ensure_ascii=False)
    print(f"Updated {fixed_signs_count} road sign questions in {signs_path}")

    # ----------------------------------------------------
    # 2. FIX RULES OF THE ROAD
    # ----------------------------------------------------
    rules_path = "data/questions/telangana/rules-of-road.json"
    with open(rules_path) as f:
        rules = json.load(f)

    clean_rules = {
        55: {
            "options": {
                "en": [
                    "TURN AT THE NEXT LEFT",
                    "STOP ON THE LEFT",
                    "STOP IMMEDIATELY",
                    "MOVE OVER TO THE RIGHT"
                ],
                "te": [
                    "తరువాతి ఎడమ మలుపు వద్ద తిరగాలి",
                    "వాహనాన్ని ఎడమ వైపునకు తీసుకువచ్చి ఆపాలి",
                    "తక్షణమే అక్కడే ఆపాలి",
                    "కుడి వైపునకు తరలిపోవాలి"
                ],
                "hi": [
                    "अगले बाएं मोड़ पर मुड़ें",
                    "सड़क के बाईं ओर वाहन रोकें",
                    "तुरंत वहीं रुकें",
                    "दाईं ओर चले जाएं"
                ]
            },
            "answerIndex": 1,
            "explanation": {
                "en": "When a police officer flashes headlights and points left, pull over safely and stop on the left.",
                "te": "పోలీస్ హెడ్‌లైట్ వేసి ఎడమవైపు చూపిస్తే ఎడమ వైపునకు వచ్చి సురక్షితంగా ఆపాలి.",
                "hi": "जब पुलिस हेडलाइट जलाकर बाईं ओर इशारा करे, तो बाईं ओर सुरक्षित रुकें।"
            }
        }
    }

    fixed_rules_count = 0
    for r in rules:
        qnum = r["questionNumber"]
        if qnum in clean_rules:
            corr = clean_rules[qnum]
            r["options"] = corr["options"]
            r["answerIndex"] = corr["answerIndex"]
            r["explanation"] = corr["explanation"]
            fixed_rules_count += 1

    with open(rules_path, "w") as f:
        json.dump(rules, f, indent=2, ensure_ascii=False)
    print(f"Updated {fixed_rules_count} rules-of-road questions in {rules_path}")

    # ----------------------------------------------------
    # 3. FIX GENERAL PRINCIPLES
    # ----------------------------------------------------
    gp_path = "data/questions/telangana/general-principles.json"
    with open(gp_path) as f:
        gp = json.load(f)

    clean_gp = {
        108: {
            "text": {
                "en": "YOU HAVE THIRD PARTY INSURANCE. WHAT DOES THIS COVER?",
                "te": "మీ వద్ద థర్డ్ పార్టీ ఇన్సూరెన్స్ ఉంది. ఇది దేనికి రక్షణ కల్పిస్తుంది?",
                "hi": "आपके पास थर्ड पार्टी बीमा है। यह किस चीज को कवर करता है?"
            },
            "options": {
                "en": [
                    "INJURY TO ANOTHER PERSON.",
                    "DAMAGE TO SOMEONE'S PROPERTY.",
                    "DAMAGE TO OTHER VEHICLES.",
                    "ALL OF THE ABOVE."
                ],
                "te": [
                    "ఇతర వ్యక్తులకు గాయాలు / ప్రాణ నష్టం.",
                    "ఇతరుల ఆస్తి నష్టం.",
                    "ఇతర వాహనాలకు కలిగే నష్టం.",
                    "పైవన్నీ (ALL OF THE ABOVE)."
                ],
                "hi": [
                    "किसी अन्य व्यक्ति को चोट / शारीरिक हानि।",
                    "किसी अन्य की संपत्ति का नुकसान।",
                    "अन्य वाहनों को नुकसान।",
                    "उपरोक्त सभी।"
                ]
            },
            "answerIndex": 3,
            "explanation": {
                "en": "Third party insurance covers liability for death, injury, property, or vehicular damage caused to third parties.",
                "te": "థర్డ్ పార్టీ బీమా ఇతరుల ప్రాణాలు, గాయాలు, మరియు ఆస్తి లేదా వాహన నష్టానికి రక్షణ కల్పిస్తుంది.",
                "hi": "थर्ड पार्टी बीमा तीसरे पक्ष की चोट, मृत्यु और संपत्ति या वाहन के नुकसान को कवर करता है।"
            }
        },
        119: {
            "options": {
                "en": [
                    "THE OWNER OF THE VEHICLE.",
                    "THE PASSENGER IN THE VEHICLE.",
                    "THE MECHANIC OF THE VEHICLE.",
                    "THE DRIVER OF THE VEHICLE."
                ],
                "te": [
                    "వాహన యజమాని.",
                    "వాహనంలో ప్రయాణీకుడు.",
                    "వాహనం యొక్క మెకానిక్.",
                    "వాహనం నడుపుతున్న డ్రైవర్."
                ],
                "hi": [
                    "वाहन का मालिक।",
                    "वाहन में सवार यात्री।",
                    "वाहन का मैकेनिक।",
                    "वाहन का चालक।"
                ]
            },
            "answerIndex": 3,
            "explanation": {
                "en": "The driver of the vehicle is legally responsible for ensuring children are wearing seatbelts.",
                "te": "వాహనంలో పిల్లలు సీట్ బెల్ట్ ధరించేలా చూసే చట్టపరమైన బాధ్యత డ్రైవర్ దే.",
                "hi": "बच्चों द्वारा सीटबेल्ट पहनना सुनिश्चित करने की कानूनी जिम्मेदारी चालक की है।"
            }
        },
        159: {
            "text": {
                "en": "A PROPERLY SERVICED VEHICLE WILL GIVE:",
                "te": "క్రమం తప్పకుండా సర్వీస్ చేసిన వాహనం ఏమి ఇస్తుంది?",
                "hi": "उचित रूप से सर्विस किया गया वाहन क्या लाभ देता है?"
            },
            "options": {
                "en": [
                    "LOWER ROAD TAX",
                    "A REFUND ON YOUR INSURANCE",
                    "BETTER FUEL ECONOMY AND CLEANER EXHAUST",
                    "NONE OF THE ABOVE"
                ],
                "te": [
                    "తక్కువ రోడ్డు పన్ను",
                    "బీమా ప్రీమియం వాపసు",
                    "మెరుగైన ఇంధన సామర్థ్యం (మైలేజ్) మరియు తక్కువ కాలుష్యం",
                    "పైవేవీ కావు"
                ],
                "hi": [
                    "कम सड़क कर",
                    "बीमा रिफंड",
                    "बेहतर माइलेज (ईंधन बचत) और कम प्रदूषण",
                    "इनमें से कोई नहीं"
                ]
            },
            "answerIndex": 2,
            "explanation": {
                "en": "Regular vehicle maintenance ensures optimal engine combustion, improving fuel mileage and reducing emissions.",
                "te": "సమయానికి సర్వీస్ చేయడం వల్ల ఇంజిన్ సమర్థవంతంగా పనిచేసి మెరుగైన మైలేజీ మరియు తక్కువ పొగ విడుదల చేస్తుంది.",
                "hi": "नियमित सर्विसिंग से इंजन बेहतर माइलेज देता है और प्रदूषण कम होता है।"
            }
        }
    }

    fixed_gp_count = 0
    for q in gp:
        qnum = q["questionNumber"]
        if qnum in clean_gp:
            corr = clean_gp[qnum]
            if "text" in corr:
                q["text"] = corr["text"]
            q["options"] = corr["options"]
            q["answerIndex"] = corr["answerIndex"]
            q["explanation"] = corr["explanation"]
            fixed_gp_count += 1

    with open(gp_path, "w") as f:
        json.dump(gp, f, indent=2, ensure_ascii=False)
    print(f"Updated {fixed_gp_count} general-principles questions in {gp_path}")

if __name__ == "__main__":
    fix_all()
