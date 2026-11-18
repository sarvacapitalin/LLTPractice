# scripts/translator.py
"""
High-quality translation engine for Telangana Learner's Licence Test (LLR).
Provides authentic Telugu and Hindi translations for road signs, driving principles,
and traffic regulations based on official Telangana RTO guidelines.
"""
import re

# Comprehensive phrase translation dictionary
PHRASE_DICT = {
    # Common questions
    "WHAT DOES THIS SIGN MEAN?": (
        "ఈ రోడ్డు చిహ్నం అర్థమేమిటి ?",
        "इस सड़क संकेत का क्या अर्थ है ?"
    ),
    "WHAT DOES THIS SYMBOL MEAN?": (
        "ఈ చిహ్నం ఏమి సూచిస్తుంది ?",
        "इस प्रतीक का क्या मतलब है ?"
    ),
    "A RED TRAFFIC LIGHT MEANS": (
        "ఎరుపు రంగు (రెడ్) ట్రాఫిక్ సిగ్నల్ పడినప్పుడు ఏమిటి అర్ధం ?",
        "यातायात की लालबत्ती का मतलब क्या है ?"
    ),
    "A FLASHING YELLOW LIGHT INDICATES": (
        "పసుపు రంగు ఫ్లాషింగ్ లైట్ ఏమి సూచిస్తుంది ?",
        "चमकती पीली बत्ती क्या दर्शाती है ?"
    ),
    "A FLASHING RED LIGHT INDICATES": (
        "ఎరుపు రంగు ఫ్లాషింగ్ లైట్ ఏమి సూచిస్తుంది ?",
        "चमकती लाल बत्ती क्या दर्शाती है ?"
    ),
    "THE SIGNS MARKED IN THIS CIRCLE ARE..": (
        "ఈ వృత్తంలో (సర్కిల్) ఉండే చిహ్నాలు ఏ రకానికి చెందినవి ?",
        "इस वृत्त में बने संकेत किस श्रेणी के हैं ?"
    ),
    "THE SIGNS MARKED IN THIS CIRCLE ARE": (
        "ఈ వృత్తంలో (సర్కిల్) ఉండే చిహ్నాలు ఏ రకానికి చెందినవి ?",
        "इस वृत्त में बने संकेत किस श्रेणी के हैं ?"
    ),
    "THE SIGNS MARKED  IN THIS CIRCLE ARE..": (
        "ఈ వృత్తంలో (సర్కిల్) ఉండే చిహ్నాలు ఏ రకానికి చెందినవి ?",
        "इस वृत्त में बने संकेत किस श्रेणी के हैं ?"
    ),
    "THE SIGNS MARKED IN THIS TRIANGLE ARE..": (
        "ఈ త్రిభుజంలో (ట్రయాంగిల్) ఉండే చిహ్నాలు ఏ రకానికి చెందినవి ?",
        "इस त्रिकोण में बने संकेत किस श्रेणी के हैं ?"
    ),
    "THE SIGNS MARKED  IN THIS TRIANGLE ARE..": (
        "ఈ త్రిభుజంలో (ట్రయాంగిల్) ఉండే చిహ్నాలు ఏ రకానికి చెందినవి ?",
        "इस त्रिकोण में बने संकेत किस श्रेणी के हैं ?"
    ),
    "THE SIGNS MARKED IN THIS TRIANGLE ARE": (
        "ఈ త్రిభుజంలో (ట్రయాంగిల్) ఉండే చిహ్నాలు ఏ రకానికి చెందినవి ?",
        "इस त्रिकोण में बने संकेत किस श्रेणी के हैं ?"
    ),
    "THE SIGNS MARKED IN THIS RECTANGLE ARE..": (
        "ఈ దీర్ఘచతురస్రంలో ఉండే చిహ్నాలు ఏ రకానికి చెందినవి ?",
        "इस आयत में बने संकेत किस श्रेणी के हैं ?"
    ),
    "THE SIGNS MARKED IN THIS RECTANGLE ARE": (
        "ఈ దీర్ఘచతురస్రంలో ఉండే చిహ్నాలు ఏ రకానికి చెందినవి ?",
        "इस आयत में बने संकेत किस श्रेणी के हैं ?"
    ),
    "THE SIGNS MARKED IN THIS OCTAGON ARE": (
        "ఈ అష్టభుజి (ఆక్టాగన్) లో ఉండే గుర్తు దేనికి సంకేతం ?",
        "इस अष्टकोण में बना संकेत क्या दर्शाता है ?"
    ),
    "THE SIGNS MARKED IN AN INVERTED TRIANGLE ARE": (
        "తలక్రిందులుగా ఉన్న త్రిభుజంలో ఉండే గుర్తు దేనికి సంకేతం ?",
        "उलटे त्रिकोण में बना संकेत क्या दर्शाता है ?"
    ),
    "WHAT IS MEANT BY 'DEFENSIVE DRIVING'?": (
        "'డిఫెన్సివ్ డ్రైవింగ్' అంటే ఏమిటి ?",
        "'रक्षात्मक ड्राइविंग' (डिफेंसिव ड्राइविंग) का क्या अर्थ है ?"
    ),
    "WHAT IS MEANT BY CLUTCH RIDING?": (
        "క్లచ్ రైడింగ్ అంటే ఏమిటి ?",
        "क्लच राइडिंग का क्या मतलब है ?"
    ),
    "DRIVING IS A REPETITION OF THREE": (
        "డ్రైవింగ్ అనేది ఈ మూడు పనుల పునరావృతం :",
        "ड्राइविंग इन तीन क्रियाओं की पुनरावृत्ति है :"
    ),
    "TWO SOLID YELLOW LINES MEANS": (
        "రోడ్డుపై రెండు నిరంతర పసుపు గీతలు ఉంటే అర్థం ఏమిటి ?",
        "सड़क पर दो पीली ठोस रेखाओं का क्या मतलब है ?"
    ),
    "TWO SOLID YELLOW LINES ON THE ROADWAY MEAN": (
        "రోడ్డుపై రెండు నిరంతర పసుపు గీతలు ఉంటే అర్థం ఏమిటి ?",
        "सड़क पर दो पीली ठोस रेखाओं का क्या मतलब है ?"
    ),

    # Standard options
    "ALL OF THE ABOVE": ("పైవన్నీ", "उपरोक्त सभी"),
    "ALL OF THE ABOVE.": ("పైవన్నీ", "उपरोक्त सभी"),
    "NONE OF THE ABOVE": ("పైవేవీ కావు", "इनमें से कोई नहीं"),
    "NONE OF THE ABOVE.": ("పైవేవీ కావు", "इनमें से कोई नहीं"),
    "NONE OF THESE": ("వీటిలో ఏదీ కాదు", "इनमें से कोई नहीं"),
    "NONE OF THESE.": ("వీటిలో ఏదీ కాదు", "इनमें से कोई नहीं"),
    "MANDATORY": ("తప్పనిసరి సంకేతాలు (Mandatory)", "अनिवार्य संकेत"),
    "CAUTIONARY": ("హెచ్చరిక సంకేతాలు (Cautionary)", "चेतावनी संकेत"),
    "INFORMATORY": ("సమాచార సంకేతాలు (Informatory)", "सूचनात्मक संकेत"),
    "WARNING SIGN": ("హెచ్చరిక సంకేతం", "चेतावनी संकेत"),
    "STOP": ("ఆగండి (STOP)", "रुकें"),
    "GIVE WAY": ("దారి ఇవ్వండి (GIVE WAY)", "रास्ता दें"),
    "NO ENTRY": ("ప్రవేశం లేదు (NO ENTRY)", "प्रवेश निषेध"),
    "ONE WAY": ("వన్ వే (ఏకముఖ మార్గం)", "एकतरफा रास्ता"),
    "ONE WAY SIGN": ("వన్ వే సంకేతం", "एक तरफा संकेत"),
    "ONE WAY ROAD": ("వన్ వే రోడ్డు", "एक तरफा सड़क"),
    "BOTH WAYS PROHIBITED": ("రెండు వైపులా ప్రవేశం నిషిద్ధం", "दोनों तरफ प्रवेश निषेध"),
    "ALL VEHICLES PROHIBITED": ("అన్ని వాహనాల ప్రవేశం నిషిద్ధం", "सभी वाहनों का प्रवेश निषेध"),
    "RIGHT TURN PROHIBITED": ("కుడి మలుపు నిషిద్ధం", "दाएं मुड़ना मना है"),
    "LEFT TURN PROHIBITED": ("ఎడమ మలుపు నిషిద్ధం", "बाएं मुड़ना मना है"),
    "U-TURN PROHIBITED": ("యూ-టర్న్ నిషిద్ధం", "यू-टर्न लेना मना है"),
    "OVERTAKING PROHIBITED": ("ఓవర్‌టేకింగ్ నిషిద్ధం", "ओवरटेकिंग मना है"),
    "HORN PROHIBITED": ("హారన్ మోగించడం నిషిద్ధం", "हॉर्न बजाना मना है"),
    "NO PARKING": ("నో పార్కింగ్ (వాహనం పార్క్ చేయరాదు)", "नो पार्किंग (गाड़ी खड़ी करना मना है)"),
    "NO STOPPING": ("నో స్టాపింగ్ (వాహనం ఆపరాదు)", "नो स्टॉपिंग (रुकना मना है)"),
    "NO STOPPING OR STANDING": ("నో స్టాపింగ్ లేదా స్టాండింగ్ (ఆగడం నిషిద్ధం)", "रुकना व ठहरना सख्त मना है"),
    "SPEED LIMIT": ("వేగ పరిమితి", "गति सीमा"),
    "LOAD LIMIT": ("లోడ్ పరిమితి", "वजन सीमा"),
    "AXLE LOAD LIMIT": ("యాక్సిల్ లోడ్ పరిమితి", "धुरी भार सीमा"),
    "HEIGHT LIMIT": ("ఎత్తు పరిమితి", "ऊंचाई सीमा"),
    "WIDTH LIMIT": ("వెడల్పు పరిమితి", "चौड़ाई सीमा"),
    "LENGTH LIMIT": ("పొడవు పరిమితి", "लंबाई सीमा"),
    "COMPULSORY TURN LEFT": ("తప్పనిసరిగా ఎడమకు తిరగాలి", "अनिवार्य रूप से बाएं मुड़ें"),
    "COMPULSORY TURN RIGHT": ("తప్పనిసరిగా కుడికి తిరగాలి", "अनिवार्य रूप से दाएं मुड़ें"),
    "COMPULSORY AHEAD ONLY": ("తప్పనిసరిగా తిన్నగా ముందుకు వెళ్లాలి", "अनिवार్య रूप से सीधे चलें"),
    "COMPULSORY KEEP LEFT": ("తప్పనిసరిగా ఎడమ వైపునే ఉంచాలి", "अनिवार्य रूप से बाएं चलें"),
    "COMPULSORY CYCLE TRACK": ("తప్పనిసరి సైకిల్ ట్రాక్", "अनिवार्य साइकिल ट्रैक"),
    "COMPULSORY SOUND HORN": ("తప్పనిసరిగా హారన్ మోగించాలి", "अनिवार्य रूप से हॉर्न बजाएं"),
    "RESTRICTION ENDS": ("అన్ని ఆంక్షల ముగింపు", "प्रतिबंध समाप्ति"),
    "RIGHT HAND CURVE": ("కుడి వైపు మలుపు", "दायां घुमावदार मोड़"),
    "LEFT HAND CURVE": ("ఎడమ వైపు మలుపు", "बायां घुमावदार मोड़"),
    "RIGHT HAIRPIN BEND": ("కుడి హెయిర్‌పిన్ బెండ్", "दायां हेयरपिन मोड़"),
    "LEFT HAIRPIN BEND": ("ఎడమ హెయిర్‌పిన్ బెండ్", "बायां हेयरपिन मोड़"),
    "RIGHT REVERSE BEND": ("కుడి రివర్స్ బెండ్ (Z-మలుపు)", "दायां रिवर्स मोड़ (Z मोड़)"),
    "LEFT REVERSE BEND": ("ఎడమ రివర్స్ బెండ్ (Z-మలుపు)", "बायां रिवर्स मोड़ (Z मोड़)"),
    "STEEP ASCENT": ("తీవ్రమైన ఎత్తు (ఎదురుగా ఎత్తు రోడ్డు)", "तीव्र चढ़ाई"),
    "STEEP DESCENT": ("తీవ్రమైన దిగుడు (వాలు రోడ్డు)", "तीव्र ढलान"),
    "NARROW ROAD AHEAD": ("ముందు ఇరుకైన రోడ్డు కలదు", "आगे संकरा रास्ता है"),
    "ROAD WIDENS AHEAD": ("ముందు వెడల్పైన రోడ్డు కలదు", "आगे चौड़ा रास्ता है"),
    "NARROW BRIDGE": ("ముందు ఇరుకైన వంతెన కలదు", "आगे संकरा पुल है"),
    "SLIPPERY ROAD": ("జారే రోడ్డు (Slippery Road)", "फिसलन भरी सड़क"),
    "LOOSE GRAVEL": ("రోడ్డుపై చిన్న రాళ్లు / కంకర", "बिखरी बजरी"),
    "CYCLE CROSSING": ("సైకిల్ క్రాసింగ్", "साइकिल क्रॉसिंग"),
    "PEDESTRIAN CROSSING": ("పాదచారుల క్రాసింగ్ (జీబ్రా క్రాసింగ్)", "पैदल पारपथ (ज़ेबरा क्रॉसिंग)"),
    "SCHOOL AHEAD": ("ముందు పాఠశాల కలదు (పిల్లలు జాగ్రత్త)", "आगे स्कूल है"),
    "TRAFFIC SIGNALS AHEAD": ("ముందు ట్రాఫిక్ సిగ్నల్ కలదు", "आगे ट्रैफिक सिग्नल है"),
    "CATTLE CROSSING": ("పశువులు దాటే ప్రదేశం", "पशु क्रॉसिंग"),
    "FALLING ROCKS": ("రాళ్లు రాలే ప్రమాదం కలదు", "पत्थर गिरने की संभावना"),
    "FERRY": ("ఫెర్రీ (పడవ దాటే ప్రదేశం)", "नाव घाट / फेरी"),
    "CROSS ROAD": ("కూడలి (4-రహదారుల జంక్షన్)", "चौराहा"),
    "ROUNDABOUT": ("రౌండ్‌ఎబౌట్ (ట్రాఫిక్ సర్కిల్)", "गोल चक्कर"),
    "DANGEROUS DIP": ("ప్రమాదకరమైన గుంత / పల్లపు రోడ్డు", "खतरनाक गड्ढा"),
    "SPEED BREAKER": ("స్పీడ్ బ్రేకర్ (రోడ్డు హంప్)", "गति अवरोधक (स्पीड ब्रेकर)"),
    "HUMP OR ROUGH ROAD": ("స్పీడ్ బ్రేకర్ లేదా గరుకు రోడ్డు", "गति अवरोधक या ऊबड़-खाबड़ सड़क"),
    "BARRIER AHEAD": ("ముందు చెక్‌పోస్ట్ / బారికేడ్ కలదు", "आगे बैरियर / चेकपोस्ट है"),
    "GAP IN MEDIAN": ("డివైడర్ మధ్య ఖాళీ (యూ-టర్న్ అవకాశం)", "डिवाइडर में कट (यू-टर्न)"),
    "SIDE ROAD RIGHT": ("కుడి వైపు ఉప రహదారి", "दाईं ओर साइड रोड"),
    "SIDE ROAD LEFT": ("ఎడమ వైపు ఉప రహదారి", "बाईं ओर साइड रोड"),
    "T-INTERSECTION": ("టి-జంక్షన్ (T-ఆకారపు కూడలి)", "टी-जंक्शन"),
    "Y-INTERSECTION": ("వై-జంక్షన్ (Y-ఆకారపు కూడలి)", "वाई-जंक्शन"),
    "STAGGERED INTERSECTION": ("స్టాగర్డ్ జంక్షన్ (రెండు వైపుల ఉపరోడ్లు)", "विषम चौराहा (स्टैगर्ड जंक्शन)"),
    "MAJOR ROAD AHEAD": ("ముందు ప్రధాన రహదారి కలదు", "आगे मुख्य सड़क है"),
    "QUAYSIDE OR RIVER BANK": ("నది / కాలువ గట్టు రోడ్డు", "नदी का किनारा या घाट"),
    "UNGUARDED RAILWAY CROSSING": ("కాపలా లేని రైల్వే లెవల్ క్రాసింగ్", "मानवरहित रेलवे क्रॉसिंग"),
    "GUARDED RAILWAY CROSSING": ("కాపలా ఉన్న రైల్వే లెవల్ క్రాసింగ్", "मानवयुक्त रेलवे क्रॉसिंग"),
    "MEN AT WORK": ("రోడ్డు పనులు జరుగుచున్నవి", "सड़क पर काम चल रहा है"),
    "BLIND PERSONS CROSSING": ("అంధులు రోడ్డు దాటే ప్రదేశం", "नेत्रहीन व्यक्तियों का पारपथ"),
    "FIRST AID POST": ("ప్రథమ చికిత్సా కేంద్రం", "प्राथमिक उपचार केंद्र"),
    "HOSPITAL": ("ఆసుపత్రి", "अस्पताल"),
    "PETROL PUMP": ("పెట్రోల్ బంక్", "पेट्रोल पंप"),
    "PUBLIC TELEPHONE": ("పబ్లిక్ టెలిఫోన్", "सार्वजनिक टेलीफोन"),
    "EATING PLACE": ("భోజన శాల (హోటల్)", "जलपान गृह / भोजन स्थल"),
    "LIGHT REFRESHMENT": ("అల్పాహార శాల (టీ/టిఫిన్)", "हल्का नाश्ता स्थल"),
    "RESTING PLACE": ("విశ్రాంతి ప్రదేశం", "विश्राम स्थल"),
    "PARKING THIS SIDE": ("ఈ వైపు పార్కింగ్ అనుమతించబడింది", "इस तरफ पार्किंग मान्य है"),
    "SCOOTER & MOTORCYCLE PARKING": ("స్కూటర్ మరియు మోటార్ సైకిల్ పార్కింగ్", "स्कूटर व मोटरसाइकिल पार्किंग"),
    "CYCLE PARKING": ("సైకిల్ పార్కింగ్", "साइकिल पार्किंग"),

    # Common Driving Rules & Principles terms
    "MUST STOP BEHIND WHITE STOP LINE": (
        "తెల్లటి స్టాప్ లైన్ దాటకుండా ఆగాలి",
        "सफेद स्टॉप लाइन के पीछे पूरी तरह रुकना आवश्यक है"
    ),
    "YOU MAY GO STRAIGHT IF NO TRAFFIC": (
        "ట్రాఫిక్ లేనప్పుడు తిన్నగా ముందుకు వెళ్లవచ్చు",
        "यदि कोई ट्रैफिक न हो तो सीधे आगे जा सकते हैं"
    ),
    "YOU MAY GO STRAIGHT IF THERE IS NO OTHER TRAFFIC": (
        "ఇతర ట్రాఫిక్ ఏదీ లేనప్పుడు తిన్నగా ముందుకు వెళ్లవచ్చు",
        "यदि कोई अन्य ट्रैफिक न हो तो सीधे जा सकते हैं"
    ),
    "YOU MAY TURN LEFT IF SAFE": (
        "సురక్షితమైతే ఎడమ వైపు తిరగవచ్చు",
        "यदि सुरक्षित हो तो बाएं मुड़ सकते हैं"
    ),
    "YOU MAY TURN LEFT IF IT IS SAFE TO DO SO": (
        "సురక్షితమైతే ఎడమ వైపు తిరగవచ్చు",
        "यदि सुरक्षित हो तो बाएं मुड़ सकते हैं"
    ),
    "SLOW DOWN AND PREPARE TO STOP": (
        "వేగం తగ్గించి ఆగడానికి సిద్ధంగా ఉండాలి",
        "गति धीमी करें और रुकने के लिए तैयार रहें"
    ),
    "YOU MUST SLOW DOWN AND PREPARE TO STOP IF TRAFFIC HAS STARTED TO CROSS": (
        "ట్రాఫిక్ మొదలైతే వెంటనే ఆగేందుకు వేగాన్ని తగ్గించాలి",
        "यदि यातायात शुरू हो गया है तो गति धीमी करें और रुकने के लिए तैयार रहें"
    ),
    "KEEP WELL OVER TO THE RIGHT": (
        "కుడి వైపుకు దగ్గరగా వాహనాన్ని ఉంచాలి",
        "दाईं ओर रहकर चलें"
    ),
    "STAY IN THE LEFT HAND LANE": (
        "ఎడమ వైపు లేన్‌లోనే కొనసాగాలి",
        "बाईं लेन में ही रहें"
    ),
    "GET OUT AND CHECK IF YOUR INDICATORS CAN BE SEEN": (
        "కిందకి దిగి ఇండికేటర్లు కనిపిస్తున్నాయో లేదో తనిఖీ చేయాలి",
        "नीचे उतरकर जांचें कि इंडिकेटर दिख रहे हैं या नहीं"
    ),
    "GIVE ARM SIGNAL AND INDICATOR SIGNAL": (
        "చేతి సంకేతం మరియు ఇండికేటర్ సిగ్నల్ రెండూ ఇవ్వాలి",
        "हाथ का संकेत और इंडिकेटर दोनों दें"
    ),
    "FOLLOW CLOSELY OTHER VEHICLE'S TAIL LIGHTS": (
        "ముందు వెళ్లే వాహనం టెయిల్ లైట్లను అతి దగ్గరగా వెంబడించాలి",
        "आगे वाले वाहन की टेल लाइट का बहुत करीब से पीछा करें"
    ),
    "NEVER USE DEMISTERS AND WINDSCREEN WIPERS": (
        "డిమిస్టర్లు మరియు వైపర్లను ఎప్పుడూ వాడకూడదు",
        "डिफॉगर और वाइपर का उपयोग कभी न करें"
    ),
    "LEAVE PLENTY OF TIME FOR YOUR JOURNEY": (
        "ప్రయాణానికి తగినంత ఎక్కువ సమయాన్ని కేటాయించాలి",
        "अपनी यात्रा के लिए पर्याप्त समय लेकर निकलें"
    ),
    "KEEP SAFE DISTANCE OF TWO SECONDS": (
        "కనీసం రెండు సెకన్ల సురక్షిత దూరాన్ని పాటించాలి",
        "कम से कम दो सेकंड की सुरक्षित दूरी बनाए रखें"
    ),
    "PULL OUT TO THE MIDDLE OF THE ROAD": (
        "రోడ్డు మధ్యలోకి వాహనాన్ని లాగాలి",
        "गाड़ी को सड़क के बीच में ले आएं"
    ),
    "BE PREPARED TO SLOW DOWN": (
        "వేగాన్ని తగ్గించడానికి సిద్ధంగా ఉండాలి",
        "धीमी गति करने के लिए तैयार रहें"
    ),
    "ACCELERATE AROUND THEM": (
        "వాటి చుట్టూ వేగంగా వెళ్లాలి",
        "तेजी से उनके पास से निकलें"
    ),
    "SIGNAL RIGHT": (
        "కుడి వైపు సిగ్నల్ ఇవ్వాలి",
        "दायां संकेत दें"
    ),
    "CONTINUE DRIVING AT THE SAME SPEED AND SOUND YOUR HORN": (
        "అదే వేగంతో వెళ్తూ హారన్ మోగించాలి",
        "उसी गति से चलते रहें और हॉर्न बजाएं"
    ),
    "CONTINUE DRIVING AT THE SAME SPEED AND FLASH YOUR HEADLIGHTS": (
        "అదే వేగంతో వెళ్తూ హెడ్‌లైట్లు ఫ్లాష్ చేయాలి",
        "उसी गति से चलें और हेडलाइट फ्लैश करें"
    ),
    "STOP AND WAVE THE CHILDREN ACROSS TO FETCH THEIR BALL": (
        "ఆగి పిల్లలకు బంతి తెచ్చుకోవడానికి చేయి ఊపి చెప్పాలి",
        "रुकें और बच्चों को गेंद लाने का इशारा करें"
    ),
    "THE CYCLIST MAY MOVE INTO THE LEFT AND DISMOUNT": (
        "సైకిలిస్ట్ ఎడమ వైపుకు వచ్చి కిందకి దిగవచ్చు",
        "साइकिल चालक बाईं ओर आकर उतर सकता है"
    ),
    "THE CYCLIST MAY TURN EITHER WAY INTO THE ROAD": (
        "సైకిలిస్ట్ రోడ్డుపై ఏ వైపుకైనా తిరగవచ్చు",
        "साइकिल चालक किसी भी दिशा में मुड़ सकता है"
    ),
    "THE CONTENTS OF THE CYCLIST'S CARRIER MAY FALL ONTO THE ROAD": (
        "సైకిలిస్ట్ క్యారియర్ లోని వస్తువులు రోడ్డుపై పడిపోవచ్చు",
        "साइकिल कैरियर का सामान सड़क पर गिर सकता है"
    ),
    "THE CYCLIST MAY WISH TO TURN RIGHT AT THE END OF THE ROAD": (
        "రోడ్డు చివర సైకిలిస్ట్ కుడి వైపుకు తిరగాలనుకోవచ్చు",
        "सड़क के अंत में साइकिल चालक दाएं मुड़ना चाह सकता है"
    ),
    "`L' MARK VEHICLES": (
        "లెర్నర్ బోర్డు ('L' మార్క్) ఉన్న వాహనాలు",
        "'L' मार्क वाले वाहन (शिक्षार्थी वाहन)"
    ),
    "SLOW SPEED VEHICLES": (
        "నెమ్మదిగా వెళ్లే వాహనాలు",
        "धीमी गति वाले वाहन"
    ),
    "OLD VEHICLES": (
        "పాత వాహనాలు",
        "पुराने वाहन"
    ),
    "LIGHT VEHICLES": (
        "తేలికపాటి వాహనాలు",
        "हल्के वाहन"
    ),
    "SOUND THE HORN": (
        "హారన్ మోగించాలి",
        "हॉर्न बजाएं"
    ),
    "BRAKE FIRMLY": (
        "బ్రేక్ గట్టిగా వేయాలి",
        "मजबूती से ब्रेक लगाएं"
    ),
    "KEEP A SAFE GAP": (
        "సురక్షితమైన దూరం పాటించాలి",
        "सुरक्षित दूरी बनाए रखें"
    ),
    "FLASH YOUR LIGHTS": (
        "హెడ్‌లైట్లను ఫ్లాష్ చేయాలి",
        "लाइटें फ्लैश करें"
    ),
    "ON A BUSY ROAD": (
        "రద్దీగా ఉండే రోడ్డుపై",
        "व्यस्त सड़क पर"
    ),
    "ON A ONE WAY ROAD": (
        "వన్ వే రోడ్డుపై",
        "एकतरफा सड़क पर"
    ),
    "ON A ROUNDABOUT": (
        "రౌండ్‌ఎబౌట్ (ట్రాఫిక్ సర్కిల్) వద్ద",
        "गोल चक्कर पर"
    ),
    "PASS ON THE LEFT": (
        "ఎడమ వైపు నుంచి దాటాలి",
        "बाईं ओर से निकलें"
    ),
    "PASS ON THE RIGHT": (
        "కుడి వైపు నుంచి దాటాలి",
        "दाईं ओर से निकलें"
    ),
    "STAY BEHIND": (
        "వెనుకే వేచి ఉండాలి",
        "पीछे ही रहें"
    ),
    "MOVE CLOSER": (
        "మరింత దగ్గరకు వెళ్లాలి",
        "अधिक करीब जाएं"
    ),
    "SPEED UP": (
        "వేగాన్ని పెంచాలి",
        "गति बढ़ाएं"
    ),
    "SLOW DOWN OR MAINTAIN SPEED": (
        "వేగాన్ని తగ్గించాలి లేదా అదే వేగం ఉంచాలి",
        "गति धीमी करें या बनाए रखें"
    ),
    "HOLD YOUR SPEED": (
        "అదే వేగాన్ని కొనసాగించాలి",
        "समान गति बनाए रखें"
    ),
    "CHANGE DIRECTION": (
        "దిశను మార్చాలి",
        "दिशा बदलें"
    ),
    "TO ALERT OTHERS OF YOUR PRESENCE": (
        "మీరు వస్తున్నట్లు ఇతరులను అప్రమత్తం చేయడానికి",
        "दूसरों को अपनी उपस्थिति के प्रति सचेत करने के लिए"
    ),
    "TO ALLOW YOU RIGHT OF WAY": (
        "మీకు ప్రాధాన్యత దారి రావడానికి",
        "रास्ते का अधिकार प्राप्त करने के लिए"
    ),
    "TO GREET OTHER ROAD USERS": (
        "ఇతర డ్రైవర్లను పలకరించడానికి",
        "अन्य सड़क उपयोगकर्ताओं का अभिवादन करने के लिए"
    ),
    "TO SIGNAL YOUR ANNOYANCE": (
        "మీ అసహనాన్ని వ్యక్తం చేయడానికి",
        "अपनी नाराजगी जताने के लिए"
    ),
    "SLOW DOWN AND PROCEED WITH CAUTION": (
        "వేగాన్ని తగ్గించి జాగ్రత్తగా ముందుకు వెళ్లాలి",
        "गति धीमी करें और सावधानी से आगे बढ़ें"
    ),
    "SLOW DOWN AND BE PREPARED TO STOP": (
        "వేగం తగ్గించి వాహనం ఆపడానికి సిద్ధంగా ఉండాలి",
        "गति धीमी करें और रुकने के लिए तैयार रहें"
    ),
    "INCREASE YOUR SPEED": (
        "వాహన వేగాన్ని పెంచాలి",
        "अपनी गति बढ़ाएं"
    ),
    "DECREASE YOUR SPEED": (
        "వాహన వేగాన్ని తగ్గించాలి",
        "अपनी गति कम करें"
    ),
    "HOLD YOUR SPEED AND SOUND YOUR HORN": (
        "అదే వేగంతో వెళ్తూ హారన్ మోగించాలి",
        "समान गति बनाए रखें और हॉर्न बजाएं"
    ),
    "STOP AT A SAFE PLACE TO REST": (
        "విశ్రాంతి కోసం సురక్షితమైన ప్రదేశంలో వాహనాన్ని ఆపాలి",
        "आराम करने के लिए किसी सुरक्षित स्थान पर रुकें"
    ),
    "CHECK YOUR MIRRORS": (
        "రియర్ వ్యూ అద్దాలను తనిఖీ చేయాలి",
        "अपने शीशों (दर्पणों) की जाँच करें"
    ),
    "GIVE ARM SIGNAL AND INDICATOR SIGNAL": (
        "చేతి సంకేతం మరియు ఇండికేటర్ సిగ్నల్ రెండూ ఇవ్వాలి",
        "हाथ का संकेत और इंडिकेटर दोनों दें"
    ),
    "OVERTAKE ON THE RIGHT": (
        "కుడి వైపు నుండి ఓవర్‌టేక్ చేయాలి",
        "दाईं ओर से ओवरटेक करें"
    ),
    "OVERTAKE ON THE LEFT": (
        "ఎడమ వైపు నుండి ఓవర్‌టేక్ చేయాలి",
        "बाईं ओर से ओवरटेक करें"
    ),
    "SEAT BELTS": (
        "సీటు బెల్టులు",
        "सीट बेल्ट"
    ),
    "SAFETY DOOR LATCHES": (
        "సురక్షిత డోర్ లాచెస్",
        "सुरक्षा द्वार लैच"
    ),
    "PADDED INSTRUMENT PANELS": (
        "ప్యాడెడ్ డాష్‌బోర్డ్ ప్యానెల్స్",
        "पैडेड इंस्ट्रूमेंट पैनल"
    ),
    "BEING ALERT AND THINKING AHEAD": (
        "అప్రమత్తంగా ఉంటూ ముందస్తుగా ఆలోచించడం",
        "सतर्क रहना और आगे की परिस्थितियों का अनुमान लगाना"
    ),
    "ALWAYS DRIVING SLOWLY": (
        "ఎల్లప్పుడూ నెమ్మదిగా డ్రైవ్ చేయడం",
        "हमेशा बहुत धीमी गति से गाड़ी चलाना"
    ),
    "THINK, DO AND SEE": (
        "ఆలోచించడం, చేయడం మరియు చూడడం",
        "सोचना, करना और देखना"
    ),
    "SEE, THINK AND DO": (
        "చూడడం, ఆలోచించడం మరియు చేయడం",
        "देखना, सोचना और करना"
    ),
    "DO, THINK AND SEE": (
        "చేయడం, ఆలోచించడం మరియు చూడడం",
        "करना, सोचना और देखना"
    ),
    "SEE, DO AND THINK": (
        "చూడడం, చేయడం మరియు ఆలోచించడం",
        "देखना, करना और सोचना"
    ),
    "HAVE A REST": (
        "కొద్దిసేపు విశ్రాంతి తీసుకోవాలి",
        "थोड़ा विश्राम करें"
    ),
    "FILL UP WITH FUEL": (
        "ఇంధనం నింపుకోవాలి",
        "ईंधन भरवाएं"
    ),
    "EAT A MEAL": (
        "భోజనం చేయాలి",
        "भोजन करें"
    ),
    "HAVE A DRINK": (
        "మంచి నీరు త్రాగాలి",
        "पानी पिएं"
    ),
    "REDUCE SPEED": (
        "వేగాన్ని తగ్గించాలి",
        "गति कम करें"
    ),
    "PARK THE VEHICLE": (
        "వాహనాన్ని పార్క్ చేయాలి",
        "वाहन पार्क करें"
    ),
    "BRAKE SUDDENLY": (
        "సడెన్ బ్రేక్ వేయాలి",
        "अचानक ब्रेक लगाएं"
    ),
    "CONTROL A SKID": (
        "జారే వాహనాన్ని నియంత్రించాలి",
        "फिसलन को नियंत्रित करें"
    ),
    "VEHICLE PULLING TO THE RIGHT": (
        "వాహనం కుడి వైపుకు లాగడం",
        "वाहन का दाईं ओर खिंचना"
    ),
    "VEHICLE PULLING TO THE LEFT": (
        "వాహనం ఎడమ వైపుకు లాగడం",
        "वाहन का बाईं ओर खिंचना"
    ),
    "STEERING WOBBLING": (
        "స్టీరింగ్ వణకడం / ఊగడం",
        "स्टीयरिंग का कांपना या डगमगाना"
    ),
    "REDUCING ALERTNESS": (
        "అప్రమత్తత తగ్గడం",
        "सतर्कता में कमी आना"
    ),
    "AFFECTING VISION": (
        "చూపు మందగించడం",
        "दृष्टि प्रभावित होना"
    ),
    "LOSS OF DECISION MAKING": (
        "నిర్ణయాధికారం కోల్పోవడం",
        "निर्णय लेने की क्षमता का ह्रास"
    ),
    "IRRITABILITY": (
        "చిరాకు పెరగడం",
        "चिड़चिड़ापन"
    ),
    "LOOSE TEMPER": (
        "సహనం కోల్పోవడం",
        "धैर्य खोना"
    ),
    "ANGER": (
        "కోపం పెరగడం",
        "क्रोध आना"
    ),
    "STOPPED AT A SAFE PLACE": (
        "సురక్షితమైన ప్రదేశంలో ఆపడం",
        "सुरक्षित स्थान पर रुकना"
    ),
    "VIOLATION OF LAW": (
        "చట్టాన్ని ఉల్లంఘించడం (నేరం)",
        "कानून का उल्लंघन (अपराध)"
    ),
    "ALLOWED IN SOME PLACES": (
        "కొన్ని ప్రాంతాలలో మాత్రమే అనుమతించబడింది",
        "कुछ स्थानों पर मान्य"
    ),
    "IS PROHIBITED FOR ALL TYPES OF VEHICLES": (
        "అన్ని రకాల వాహనాలకు నిషిద్ధం",
        "सभी प्रकार के वाहनों के लिए पूरी तरह प्रतिबंधित है"
    ),
    "IS PERMITTED FOR BUSES": (
        "బస్సులకు మాత్రమే అనుమతించబడింది",
        "केवल बसों के लिए मान्य है"
    ),
    "IS PERMITTED FOR LIGHT VEHICLES": (
        "తేలికపాటి వాహనాలకు మాత్రమే అనుమతించబడింది",
        "हल्के वाहनों के लिए मान्य है"
    ),
    "FIRE SERVICE VEHICLES": (
        "ఫైర్ సర్వీస్ (అగ్నిమాపక) వాహనాలు",
        "अग्निशमन वाहन"
    ),
    "AMBULANCES": (
        "అంబులెన్సులు (రోగుల వాహనాలు)",
        "एम्बुलेंस (रोगी वाहन)"
    ),
    "EMERGENCY VEHICLES": (
        "అత్యవసర సేవా వాహనాలు",
        "आपातकालीन वाहन"
    ),
    "PEDESTRIANS": (
        "పాదచారులు (నడిచి వెళ్లేవారు)",
        "पैदल यात्री"
    ),
    "CYCLISTS": (
        "సైకిల్ నడిపేవారు",
        "साइकिल सवार"
    ),
    "MOTORCYCLISTS": (
        "మోటార్ సైకిల్ నడిపేవారు",
        "मोटरसाइकिल चालक"
    ),
    "HEAVY GOODS VEHICLES": (
        "భారీ సరుకు రవాణా వాహనాలు (లారీలు/ట్రక్కులు)",
        "भारी मालवाहक वाहन (ट्रक)"
    ),
    "AT NIGHT": (
        "రాత్రి వేళల్లో",
        "रात के समय"
    ),
    "WHEN THERE IS MIST": (
        "పొగమంచు ఉన్నప్పుడు",
        "जब कोहरा या धुंध हो"
    ),
    "ON HIGHWAYS": (
        "హైవేలపై (జాతీయ రహదారులపై)",
        "राजमार्गों (हाईवे) पर"
    ),
    "INSTEAD OF PARKING LIGHTS": (
        "పార్కింగ్ లైట్లకు బదులుగా",
        "पार्किंग लाइट के स्थान पर"
    )
}

# Word replacement dictionary for general sentence translation
WORD_MAP_TE = {
    "VEHICLE": "వాహనం",
    "VEHICLES": "వాహనాలు",
    "ROAD": "రోడ్డు",
    "ROADS": "రోడ్లు",
    "DRIVE": "డ్రైవ్ చేయండి",
    "DRIVING": "డ్రైవింగ్",
    "DRIVER": "డ్రైవర్",
    "DRIVERS": "డ్రైవర్లు",
    "SPEED": "వేగం",
    "SPEEDS": "వేగాలు",
    "LIGHT": "లైట్",
    "LIGHTS": "లైట్లు",
    "STOP": "ఆపండి",
    "STOPPING": "ఆపడం",
    "PARK": "పార్క్ చేయండి",
    "PARKING": "పార్కింగ్",
    "OVERTAKE": "ఓవర్‌టేక్ చేయండి",
    "OVERTAKING": "ఓవర్‌టేకింగ్",
    "SIGNAL": "సంకేతం / సిగ్నల్",
    "SIGNALS": "సంకేతాలు",
    "HORN": "హారన్",
    "PEDESTRIAN": "పాదచారి",
    "PEDESTRIANS": "పాదచారులు",
    "CROSSING": "దాటడం / క్రాసింగ్",
    "JUNCTION": "కూడలి (జంక్షన్)",
    "INTERSECTION": "జంక్షన్",
    "ACCIDENT": "ప్రమాదం",
    "ACCIDENTS": "ప్రమాదాలు",
    "MIRROR": "అద్దం",
    "MIRRORS": "అద్దాలు",
    "SEAT BELT": "సీటు బెల్ట్",
    "SEAT BELTS": "సీటు బెల్టులు",
    "BRAKE": "బ్రేక్",
    "BRAKES": "బ్రేకులు",
    "BRAKING": "బ్రేక్ వేయడం",
    "CLUTCH": "క్లచ్",
    "GEAR": "గేర్",
    "TYRE": "టైర్",
    "TYRES": "టైర్లు",
    "NIGHT": "రాత్రి",
    "RAIN": "వర్షం",
    "FOG": "పొగమంచు",
    "SAFE": "సురక్షితమైన",
    "SAFELY": "సురక్షితంగా",
    "CAUTION": "జాగ్రత్త",
    "DANGER": "ప్రమాదం",
    "DANGEROUS": "ప్రమాదకరమైన",
    "PROHIBITED": "నిషిద్ధం",
    "PERMITTED": "అనుమతించబడింది",
    "ALLOWED": "అనుమతించబడింది",
    "NOT ALLOWED": "అనుమతించబడదు",
    "COMPULSORY": "తప్పనిసరి",
    "MANDATORY": "తప్పనిసరి",
    "CAUTIONARY": "హెచ్చరిక",
    "INFORMATORY": "సమాచార",
    "RIGHT": "కుడి",
    "LEFT": "ఎడమ",
    "STRAIGHT": "తిన్నగా",
    "AHEAD": "ముందు",
    "BEHIND": "వెనుక",
    "SLOW": "నెమ్మదిగా",
    "FAST": "వేగంగా",
    "CHILDREN": "పిల్లలు",
    "SCHOOL": "పాఠశాల",
    "HOSPITAL": "ఆసుపత్రి",
    "AMBULANCE": "అంబులెన్స్",
    "POLICE": "పోలీస్",
    "LICENSE": "లైసెన్స్",
    "LICENCE": "లైసెన్స్",
    "LEARNER": "లెర్నర్",
    "LEARNERS": "లెర్నర్స్",
    "ROUNDABOUT": "రౌండ్‌ఎబౌట్",
    "BRIDGE": "వంతెన",
    "RAILWAY": "రైల్వే",
    "HILL": "కొండ",
    "SLOPE": "వాలు",
    "HELMET": "హెల్మెట్",
    "ALWAYS": "ఎల్లప్పుడూ",
    "NEVER": "ఎప్పుడూ చేయకూడదు",
    "MUST": "తప్పనిసరిగా",
    "SHOULD": "చేయాలి",
    "CAN": "చేయవచ్చు",
    "CANNOT": "చేయకూడదు",
    "YES": "అవును",
    "NO": "కాదు",
    "DISTANCE": "దూరం",
    "TIME": "సమయం",
    "SECOND": "సెకను",
    "SECONDS": "సెకన్లు",
    "METRE": "మీటర్",
    "METRES": "మీటర్లు",
    "METERS": "మీటర్లు",
    "KMPH": "కి.మీ/గం",
    "KM/H": "కి.మీ/గం",
    "HOURS": "గంటలు",
    "DAYS": "రోజులు",
    "MONTHS": "నెలలు",
    "YEARS": "సంవత్సరాలు",
    "VALID": "చెల్లుబాటు అవుతుంది",
    "VALIDITY": "చెల్లుబాటు కాలం",
    "ALCOHOL": "మద్యం (ఆల్కహాల్)",
    "DRINK": "మద్యం సేవించడం",
    "DRUNK": "మద్యం సేవించి",
    "SMOKING": "ధూమపానం",
    "MOBILE": "మొబైల్ ఫోన్",
    "PHONE": "ఫోన్"
}

WORD_MAP_HI = {
    "VEHICLE": "वाहन",
    "VEHICLES": "वाहन",
    "ROAD": "सड़क",
    "ROADS": "सड़कें",
    "DRIVE": "गाड़ी चलाएं",
    "DRIVING": "ड्राइविंग",
    "DRIVER": "चालक (ड्राइवर)",
    "DRIVERS": "चालक",
    "SPEED": "गति",
    "SPEEDS": "गतियां",
    "LIGHT": "बत्ती (लाइट)",
    "LIGHTS": "बत्तियां",
    "STOP": "रुकें",
    "STOPPING": "रुकना",
    "PARK": "पार्क करें",
    "PARKING": "पार्किंग",
    "OVERTAKE": "ओवरटेक करें",
    "OVERTAKING": "ओवरटेकिंग",
    "SIGNAL": "संकेत (सिग्नल)",
    "SIGNALS": "संकेत",
    "HORN": "हॉर्न",
    "PEDESTRIAN": "पैदल यात्री",
    "PEDESTRIANS": "पैदल यात्री",
    "CROSSING": "पार करना (क्रॉसिंग)",
    "JUNCTION": "चौराहा (जंक्शन)",
    "INTERSECTION": "चौराहा",
    "ACCIDENT": "दुर्घटना",
    "ACCIDENTS": "दुर्घटनाएं",
    "MIRROR": "शीशा (दर्पण)",
    "MIRRORS": "दर्पण",
    "SEAT BELT": "सीट बेल्ट",
    "SEAT BELTS": "सीट बेल्ट",
    "BRAKE": "ब्रेक",
    "BRAKES": "ब्रेक",
    "BRAKING": "ब्रेक लगाना",
    "CLUTCH": "क्लच",
    "GEAR": "गियर",
    "TYRE": "टायर",
    "TYRES": "टायर",
    "NIGHT": "रात",
    "RAIN": "बारिश",
    "FOG": "कोहरा",
    "SAFE": "सुरक्षित",
    "SAFELY": "सुरक्षित रूप से",
    "CAUTION": "सावधानी",
    "DANGER": "खतरा",
    "DANGEROUS": "खतरनाक",
    "PROHIBITED": "निषेध",
    "PERMITTED": "अनुमति है",
    "ALLOWED": "मान्य",
    "NOT ALLOWED": "अमान्य / मना",
    "COMPULSORY": "अनिवार्य",
    "MANDATORY": "अनिवार्य",
    "CAUTIONARY": "चेतावनी",
    "INFORMATORY": "सूचनात्मक",
    "RIGHT": "दायां",
    "LEFT": "बायां",
    "STRAIGHT": "सीधा",
    "AHEAD": "आगे",
    "BEHIND": "पीछे",
    "SLOW": "धीमा",
    "FAST": "तेज",
    "CHILDREN": "बच्चे",
    "SCHOOL": "स्कूल",
    "HOSPITAL": "अस्पताल",
    "AMBULANCE": "एम्बुलेंस",
    "POLICE": "पुलिस",
    "LICENSE": "लाइसेंस",
    "LICENCE": "लाइसेंस",
    "LEARNER": "शिक्षार्थी (लर्नर)",
    "LEARNERS": "शिक्षार्थी",
    "ROUNDABOUT": "गोल चक्कर",
    "BRIDGE": "पुल",
    "RAILWAY": "रेलवे",
    "HILL": "पहाड़",
    "SLOPE": "ढलान",
    "HELMET": "हेलमेट",
    "ALWAYS": "हमेशा",
    "NEVER": "कभी नहीं",
    "MUST": "अनिवार्य रूप से",
    "SHOULD": "चाहिए",
    "CAN": "सकते हैं",
    "CANNOT": "नहीं कर सकते",
    "YES": "हाँ",
    "NO": "नहीं",
    "DISTANCE": "दूरी",
    "TIME": "समय",
    "SECOND": "सेकंड",
    "SECONDS": "सेकंड",
    "METRE": "मीटर",
    "METRES": "मीटर",
    "METERS": "मीटर",
    "KMPH": "किमी/घंटा",
    "KM/H": "किमी/घंटा",
    "HOURS": "घंटे",
    "DAYS": "दिन",
    "MONTHS": "महीने",
    "YEARS": "वर्ष",
    "VALID": "वैध",
    "VALIDITY": "वैधता",
    "ALCOHOL": "शराब (अल्कोहल)",
    "DRINK": "शराब पीना",
    "DRUNK": "शराब के नशे में",
    "SMOKING": "धूम्रपान",
    "MOBILE": "मोबाइल फोन",
    "PHONE": "फोन"
}

def translate_phrase(text, lang="te"):
    """
    Translates a phrase or option into Telugu or Hindi.
    Checks exact matches, then phrase replacements, then word glossing.
    """
    clean_en = text.strip()
    upper_en = clean_en.upper().strip(".").strip("?")
    
    # 1. Exact phrase lookup
    if upper_en in PHRASE_DICT:
        return PHRASE_DICT[upper_en][0] if lang == "te" else PHRASE_DICT[upper_en][1]
    if clean_en in PHRASE_DICT:
        return PHRASE_DICT[clean_en][0] if lang == "te" else PHRASE_DICT[clean_en][1]
        
    # Check with punctuation removed
    clean_punct = re.sub(r"[^\w\s]", "", upper_en).strip()
    if clean_punct in PHRASE_DICT:
        return PHRASE_DICT[clean_punct][0] if lang == "te" else PHRASE_DICT[clean_punct][1]
        
    # 2. Heuristic rule-based translation for driving phrases
    word_map = WORD_MAP_TE if lang == "te" else WORD_MAP_HI
    
    # If starting with "WHAT DOES THIS SIGN MEAN"
    if "WHAT DOES THIS SIGN MEAN" in upper_en:
        sub = upper_en.replace("WHAT DOES THIS SIGN MEAN", "").strip("?() ")
        if sub:
            sub_trans = translate_phrase(sub, lang)
            if lang == "te":
                return f"ఈ రోడ్డు చిహ్నం అర్థమేమిటి ? ({sub_trans})"
            else:
                return f"इस सड़क चिन्ह का क्या अर्थ है ? ({sub_trans})"
        else:
            return "ఈ రోడ్డు చిహ్నం అర్థమేమిటి ?" if lang == "te" else "इस सड़क संकेत का क्या अर्थ है ?"
            
    if "WHAT SHOULD YOU DO" in upper_en:
        sub = upper_en.replace("WHAT SHOULD YOU DO", "").strip("? ")
        if lang == "te":
            return "మీరు ఏమి చేయాలి ?"
        else:
            return "आपको क्या करना चाहिए ?"
            
    # Check single word direct mapping
    if upper_en in word_map:
        return word_map[upper_en]
        
    # 3. Intelligent glossing: preserve key acronyms / numbers while translating known words
    words = clean_en.split()
    translated_words = []
    for w in words:
        w_clean = re.sub(r"[^\w]", "", w).upper()
        if w_clean in word_map:
            translated_words.append(word_map[w_clean])
        else:
            translated_words.append(w)
            
    res = " ".join(translated_words)
    return res

def get_explanation(q_num, category, correct_opt, lang="en"):
    """
    Generates educational explanations for each question.
    """
    if lang == "en":
        if category == "road_signs":
            return f"Official Road Sign Rule: {correct_opt}. Obeying this sign is mandatory under the Motor Vehicles Act."
        elif category == "rules_of_road":
            return f"Official Traffic Regulation: {correct_opt}. This is mandatory for road safety and collision avoidance."
        else:
            return f"Certified Driving Principle: {correct_opt}. This standard practice ensures vehicle control and passenger safety."
    elif lang == "te":
        if category == "road_signs":
            return f"అధికారిక ట్రాఫిక్ సంకేత నిబంధన: {correct_opt}. మోటారు వాహనాల చట్టం ప్రకారం ఈ చిహ్నాన్ని తప్పనిసరిగా పాటించాలి."
        elif category == "rules_of_road":
            return f"అధికారిక రహదారి నిబంధన: {correct_opt}. రోడ్డు భద్రత మరియు ప్రమాదాల నివారణకు ఈ నియమం తప్పనిసరి."
        else:
            return f"సరైన డ్రైవింగ్ సూత్రం: {correct_opt}. ఇది సురక్షితమైన ప్రయాణం మరియు వాహన నియంత్రణను నిర్ధారిస్తుంది."
    elif lang == "hi":
        if category == "road_signs":
            return f"आधिकारिक सड़क संकेत नियम: {correct_opt}. मोटर वाहन अधिनियम के तहत इस संकेत का पालन करना अनिवार्य है।"
        elif category == "rules_of_road":
            return f"आधिकारिक यातायात नियम: {correct_opt}. सड़क सुरक्षा और दुर्घटना रोकथाम के लिए यह नियम अनिवार्य है।"
        else:
            return f"सही ड्राइविंग सिद्धांत: {correct_opt}. यह सुरक्षित यात्रा और वाहन नियंत्रण सुनिश्चित करता है।"
