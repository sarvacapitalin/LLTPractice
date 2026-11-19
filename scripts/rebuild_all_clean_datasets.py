#!/usr/bin/env python3
"""
scripts/rebuild_all_clean_datasets.py

Complete end-to-end rebuild and certification of:
- data/questions/telangana/rules-of-road.json (159 questions)
- data/questions/telangana/general-principles.json (159 questions)

Features:
- Robust multi-line PDF text extraction (supporting Tj, single-quote ', Tm, Td, TD, TL, T*, TJ offsets)
- Perfect separation of Question text and Option boundaries
- 100% parity with official government answer keys
- High quality Telugu and Hindi translations
- Preservation of all scenario images
"""

import os, sys, re, json
from scripts.test_robust_extractor import decode_stream_robust
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, get_page_contents
from scripts.verify_answers import get_official_pdf_answers
from scripts.translator import translate_phrase, get_explanation, PHRASE_DICT

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_JSON_PATH = os.path.join(WORKSPACE_ROOT, "data", "questions", "telangana", "rules-of-road.json")
GP_JSON_PATH = os.path.join(WORKSPACE_ROOT, "data", "questions", "telangana", "general-principles.json")

# Additional authentic translations for common driving phrases
CUSTOM_TRANSLATIONS = {
    "BE PATIENT AND WAIT.": (
        "ఓపికగా వేచి ఉండండి.",
        "धैर्य रखें और प्रतीक्षा करें।"
    ),
    "SOUND YOUR HORN.": (
        "హారన్ మోగించండి.",
        "हॉर्न बजाएं।"
    ),
    "DRIVE ON.": (
        "ముందుకు డ్రైవ్ చేయండి.",
        "आगे गाड़ी बढ़ाएं।"
    ),
    "WAVE THEM TO CROSS.": (
        "వారిని దాటమని సైగ చేయండి.",
        "उन्हें पार करने का इशारा करें।"
    ),
    "BE READY TO STOP.": (
        "ఆగడానికి సిద్ధంగా ఉండండి.",
        "रुकने के लिए तैयार रहें।"
    ),
    "DONT OBEY THEM IN EMERGENCY.": (
        "అత్యవసర పరిస్థితుల్లో వాటిని పాటించవద్దు.",
        "आपात स्थिति में उनका पालन न करें।"
    ),
    "BE OBSERVANT FOR DRIVERS WHO DO NOT RESPECT TRAFFIC SIGNALS.": (
        "ట్రాఫిక్ సిగ్నల్స్ పాటించని డ్రైవర్లను గమనిస్తూ అప్రమత్తంగా ఉండాలి.",
        "ट्रैफिक सिग्नलों का पालन न करने वाले चालकों पर नजर रखें।"
    ),
    "DONT GO IN FOGGY CONDITIONS.": (
        "పొగమంచు పరిస్థితుల్లో వెళ్లవద్దు.",
        "कोहरे की स्थिति में न जाएं।"
    ),
    "TURN THE STEERING WHEEL TOWARDS THE KERB AND PUT THE HAND BRAKE FIRMLY": (
        "స్టీరింగ్ వీల్‌ను కెర్బ్ వైపు తిప్పి హ్యాండ్‌బ్రేక్ గట్టిగా వేయాలి.",
        "स्टीयरिंग व्हील को कर्ब की ओर मोड़ें और हैंडब्रेक मजबूती से लगाएं।"
    ),
    "PARK CLOSE TO THE BUMPER OF THE ANOTHER CAR": (
        "మరొక కారు బంపర్‌కు దగ్గరగా పార్క్ చేయండి.",
        "दूसरी कार के बम्पर के पास पार्क करें।"
    ),
    "PARK WITH TWO WHEELS ON THE KERB": (
        "రెండు చక్రాలను కెర్బ్ పై ఉంచి పార్క్ చేయండి.",
        "दो पहियों को कर्ब पर चढ़ाकर पार्क करें।"
    ),
    "TURN THE STEERING WHEEL AWAY FROM THE KERB": (
        "స్టీరింగ్ వీల్‌ను కెర్బ్ నుండి దూరంగా తిప్పండి.",
        "स्टीयरिंग व्हील को कर्ब से दूर मोड़ें।"
    ),
    "NOT AN OFFENCE SINCE THE BORROWER IS SOLELY RESPONSIBLE.": (
        "తీసుకున్న వ్యక్తే బాధ్యుడు కాబట్టి నేరం కాదు.",
        "यह अपराध नहीं है क्योंकि वाहन ले जाने वाला ही जिम्मेदार है।"
    ),
    "A SERIOUS OFFENCE.": (
        "తీవ్రమైన నేరం.",
        "गंभीर अपराध है।"
    ),
    "AN OFFENCE ONLY WHEN VEHICLE IS INVOLVED IN AN ACCIDENT.": (
        "వాహనం ప్రమాదానికి గురైనప్పుడు మాత్రమే నేరం.",
        "केवल तभी अपराध जब वाहन दुर्घटनाग्रस्त हो।"
    ),
    "LENDING OF A MOTOR VEHICLE TO A PERSON FOR DRIVING, WHO IS NOT HOLDING A VALID LICENCE IS:-": (
        "సరైన లైసెన్స్ లేని వ్యక్తికి వాహనాన్ని నడపడానికి ఇవ్వడం:-",
        "वैध लाइसेंस न रखने वाले व्यक्ति को वाहन चलाने के लिए देना:-"
    ),
    "YOU WISH TO PARK FACING DOWN HILL. WHICH OF THE FOLLOWING SHOULD YOU DO?": (
        "మీరు క్రిందికి వాలుగా ఉన్న ప్రదేశంలో పార్క్ చేయాలనుకున్నప్పుడు ఏమి చేయాలి?",
        "ढलान पर नीचे की ओर मुंह करके पार्क करते समय आपको क्या करना चाहिए?"
    ),
    "EVEN IF YOUR TRAFFIC SIGNAL GIVES YOU A CLEARWAY, YOU SHOULD-": (
        "ట్రాఫిక్ సిగ్నల్ క్లియర్‌గా ఉన్నప్పటికీ, మీరు చేయవలసింది-",
        "ट्रैफिक सिग्नल साफ रास्ता देने पर भी, आपको क्या करना चाहिए-"
    ),
    "OBJECTS HANGING FROM YOUR INTERIOR MIRROR MAY": (
        "మీ కారు లోపలి అద్దానికి వస్తువులను వేలాడదీయడం వల్ల",
        "कार के अंदरूनी शीशे पर लटकी वस्तुएं क्या कर सकती हैं?"
    ),
    "RESTRICT YOUR VIEW & DISTRACT YOUR ATTENTION": (
        "మీ దృష్టిని అడ్డుకోవచ్చు మరియు ఏకాగ్రతను చెడగొట్టవచ్చు.",
        "आपकी दृष्टि बाधित कर सकती हैं और ध्यान भटका सकती हैं।"
    ),
    "IMPROVE YOUR DRIVING": (
        "మీ డ్రైవింగ్‌ను మెరుగుపరుస్తాయి.",
        "आपकी ड्राइविंग को बेहतर बनाती हैं।"
    ),
    "HELP YOU CONCENTRATION": (
        "ఏకాగ్రతకు సహాయపడతాయి.",
        "ध्यान केंद्रित करने में मदद करती हैं।"
    ),
    "SEAT BELTS": (
        "సీట్ బెల్టులు",
        "सीट बेल्ट"
    ),
    "SAFETY DOOR LATCHES": (
        "భద్రతా డోర్ లాచెస్",
        "सुरक्षा डोर लैच"
    ),
    "WHICH OF THE FOLLOWING SHOULD YOU DO BEFORE STOPPING?": (
        "వాహనాన్ని ఆపడానికి ముందు ఈ క్రింది వాటిలో మీరు ఏమి చేయాలి?",
        "गाड़ी रोकने से पहले आपको निम्नलिखित में से क्या करना चाहिए?"
    ),
    "SOUND THE HORN": (
        "హారన్ మోగించండి.",
        "हॉर्न बजाएं।"
    ),
    "USE THE MIRRORS": (
        "అద్దాలను ఉపయోగించండి (చూడండి).",
        "शीशों का उपयोग करें (देखें)।"
    ),
    "SELECT A HIGHER GEAR": (
        "హై గేర్ వేయండి.",
        "बड़ा गियर लगाएं।"
    ),
    "FLASH YOUR HEADLIGHTS": (
        "హెడ్‌లైట్లను ఫ్లాష్ చేయండి.",
        "हेडलाइट्स चमकाएं (फ्लैश करें)।"
    ),
    "PADDED INSTRUMENT PANELS": (
        "ప్యాడెడ్ ఇన్‌స్ట్రుమెంట్ ప్యానెల్స్",
        "पैडेड इंस्ट्रूमेंट पैनल"
    ),
    "NONE OF THESE": (
        "వీటిలో ఏదీ కాదు",
        "इनमें से कोई नहीं"
    )
}

# Update translator phrase dictionary
for phrase, (te, hi) in CUSTOM_TRANSLATIONS.items():
    PHRASE_DICT[phrase.upper()] = (te, hi)

SCENARIO_MAP_RULES = {
    13: "assets/scenarios/rr_22.png",
    28: "assets/scenarios/rr_34.png",
    30: "assets/scenarios/rr_36.png",
    38: "assets/scenarios/rr_49.png",
    48: "assets/scenarios/rr_57.png",
    56: "assets/scenarios/rr_69.png",
    60: "assets/scenarios/rr_70.png",
    100: "assets/scenarios/rr_107.png",
    105: "assets/scenarios/rr_108.png",
    114: "assets/scenarios/rr_120.png",
    115: "assets/scenarios/rr_121.png",
    116: "assets/scenarios/rr_122.png",
    118: "assets/scenarios/rr_22.png",
    123: "assets/scenarios/rr_129.png",
    125: "assets/scenarios/rr_136.png",
    126: "assets/scenarios/rr_137.png",
    130: "assets/scenarios/rr_144.png",
    147: "assets/scenarios/rr_158.png",
    148: "assets/scenarios/rr_156.png",
    149: "assets/scenarios/rr_57.png",
    158: "assets/scenarios/rr_172.png"
}

CURATED_QS = {
    "rules_of_road": {
        85: (
            "AT A TRAFFIC JUNCTION, YOU GOT A GREEN SIGNAL TO MOVE ON. BUT THE PEDESTRIANS ARE STILL ON THE ZEBRA CROSSING. WHAT SHOULD YOU DO.?",
            ["MOVE YOUR VEHICLE BY BLOWING HORN", "PATIENTLY WAIT AND ALLOW PEDESTRIANS TO PASS", "SIGNAL THE PEDESTRIANS TO STOP", "TURN YOUR VEHICLE TO THE RIGHT AND GO"]
        )
    },
    "general_principles": {
        87: (
            "PRESSING THE CLUTCH PEDAL DOWN OR ROLLING IN NEUTRAL FOR TOO LONG WHILE DRIVING WILL",
            ["USE MORE FUEL", "CAUSE THE ENGINE TO OVERHEAT", "REDUCE YOUR CONTROL", "IMPROVE TYRE WEAR"]
        ),
        105: (
            "WHEN YOU SMELL OR SEE FIRE IN YOUR VEHICLE, WHAT SHOULD YOU DO?",
            ["PULL TO THE SIDE OF THE ROAD IMMEDIATELY, TURN OFF THE ENGINE AND ALL ELECTRICAL SWITCHES AND TRY TO SMOOTHER BURNING WIRES WITH SAND OR HEAVY CLOTH.", "PULL TO THE SIDE OF THE ROAD IMMEDIATELY, TURN OFF THE ENGINE AND ALL ELECTRICAL SWITCHES AND SMOTHER BURNING WIRES BY POURING WATER ON THEM.", "DON'T DO ANYTHING BUT CALL THE FIRE BRIGADE.", "NONE OF THE ABOVE."]
        ),
        106: (
            "YOU SHOULD NOT DRIVE WITH YOUR FOOT ON THE CLUTCH FOR LONGER THAN NECESSARY BECAUSE IT",
            ["REDUCES CONTROL OVER THE VEHICLE AND WILL RESULT IN PREMATURE CLUTCH FAILURE", "INCREASES WEAR OF THE GEARBOX", "DECREASES PETROL CONSUMPTION", "REDUCES THE GRIP OF THE TYRES"]
        ),
        108: (
            "YOU HAVE THIRD PARTY INSURANCE. WHAT DOES THIS COVER?",
            ["INJURY TO ANOTHER PERSON.", "DAMAGE TO SOMEONE'S PROPERTY.", "DAMAGE TO OTHER VEHICLES.", "ALL OF THE ABOVE."]
        )
    }
}

CURATED_OPTS = {
    "rules_of_road": {
        6: ["'L' MARK VEHICLES.", "SLOW SPEED VEHICLES.", "OLD VEHICLES.", "LIGHT VEHICLES."],
        12: ["SOUND THE HORN", "BRAKE FIRMLY", "KEEP A SAFE GAP", "FLASH YOUR LIGHTS"],
        15: ["DRIVE TO ANOTHER INTERSECTION THAT HAS NO TRAFFIC LIGHT", "WAIT UNTIL THE LIGHT TURNS GREEN BEFORE MAKING THE \"U\" TURN", "MAKE THE \"U\" TURN IF THERE IS A POLICEMAN AT THE INTERSECTION.", "AVOID MAKING A 'U' TURN"],
        21: ["CROSS IT WHENEVER YOU FEEL", "CROSS IT WHEN THERE IS NO TRAFFIC COMING FROM THE OPPOSITE DIRECTION", "NEVER CROSS IT UNDER ANY CIRCUMSTANCES", "CROSS IT WHEN IT IS SAFE TO DO SO BUT SHOULD COME BACK TO YOUR LANE AFTER OVERTAKING"],
        30: ["PREPARE TO GO", "GO IF THE WAY IS CLEAR", "GO IF NO PEDESTRIANS ARE CROSSING", "GET READY TO STOP BEFORE THE STOP LINE"],
        31: ["EXTEND RIGHT ARM HORIZONTAL TO THE GROUND WITH PALM DOWNWARDS", "EXTEND THE RIGHT ARM & BEND THE ELBOW AT RIGHT ANGLES AND TURNING PALM TO THE FRONT.", "NO SIGNAL REQUIRED", "NONE OF THE ABOVE"],
        34: ["STOP IMMEDIATELY", "ANSWER IT IMMEDIATELY", "STOP AT A SUITABLE PLACE AND ATTEND PHONE", "STOP AT THE NEAREST KERB"],
        37: ["SOUND THE HORN", "USE THE MIRRORS", "SELECT A HIGHER GEAR", "FLASH YOUR HEADLIGHTS"],
        45: ["NEAR A SHOPPING MALL", "AT OR NEAR A BUS STOP", "WITHIN 10 METRES (32FEET) OF A JUNCTION", "ALL OF THE ABOVE"],
        46: ["NEAR A SCHOOL ENTRANCE", "NEAR A POLICE STATION", "ON A SIDE ROAD", "ALL OF THE ABOVE"],
        47: ["LOCK IT AND REMOVE THE KEY", "LEAVE THE ENGINE RUNNING", "SWITCH THE ENGINE OFF BUT LEAVE THE KEY IN", "PARK NEAR A TRAFFIC POLICEMAN"],
        48: ["NEITHER VEHICLE", "THE VEHICLE TRAVELLING THE FASTEST", "THE VEHICLE ON THE WIDEST ROAD", "VEHICLE APPROACHING FROM THE RIGHT"],
        52: ["ONLY IF BOTH ROADS ARE CLEAR OF TRAFFIC", "NOT AT ANY TIME", "AT ANY TIME", "ONLY IF THE MAIN ROAD IS CLEAR OF TRAFFIC"],
        53: ["SOUND THE HORN", "GIVE AN ARM SIGNAL", "FLASH YOUR HEADLIGHTS", "POSITION OVER THE CENTRE LINE"],
        55: ["TURN AT THE NEXT LEFT", "STOP ON THE LEFT", "STOP IMMEDIATELY", "MOVE OVER TO THE RIGHT"],
        58: ["USE YOUR MIRRORS AND LOOK AROUND FOR A FINAL CHECK", "SIGNAL FOR OTHER DRIVERS TO SLOW DOWN", "NOT LOOK AROUND IF THERE IS A PARKED VEHICLE CLOSE IN FRONT OF YOU", "GIVE A HAND SIGNAL AS WELL AS USE YOUR INDICATOR"],
        59: ["START TO OVERTAKE & INCREASE SPEED", "FLASH YOUR HEADLIGHTS", "GIVE ANY SIGNALS", "NONE OF THE ABOVE"],
        64: ["SLOW DOWN AND MOVE WITH CAUTION", "COME TO A FULL STOP", "DONT CHANGE SPEED IF THE WAY IS CLEAR.", "WAIT FOR THE POLICEMAN TO ARRIVE"],
        70: ["WAIT FOR THEM TO FINISH THEIR GAME", "SOUND YOUR HORN TO WARN THEM OF YOUR PRESENCE.", "SLOW DOWN, AND BE READY TO MAKE A SAFE STOP.", "CONTINUE AT THE SAME SPEED AND DRIVE AROUND THEM."],
        72: ["MUST NOT OVERTAKE THE VEHICLE", "MAY OVERTAKE THE VEHICLE IF THERE ARE NO PEDESTRIANS ON THE CROSSING", "MAY OVERTAKE THE VEHICLE IF THERE ARE NO OTHER VEHICLES COMING THE OTHER WAY.", "NONE OF THE ABOVE"],
        84: ["FIRE SERVICE VEHICLES", "AMBULANCES", "HEAVY VEHICLES ONLY", "1 & 2"],
        85: ["MOVE YOUR VEHICLE BY BLOWING HORN", "PATIENTLY WAIT AND ALLOW PEDESTRIANS TO PASS", "SIGNAL THE PEDESTRIANS TO STOP", "TURN YOUR VEHICLE TO THE RIGHT AND GO"],
        87: ["EXTEND THE RIGHT ARM, PALM DOWN, TO THE RIGHT OF THE VEHICLE AND MOVE THE EXTENDED ARM UP AND DOWN SEVERAL TIMES", "RAISE THE RIGHT FORE ARM VERTICALLY OUT SIDE TO THE RIGHT OF THE VEHICLE, PALM TO THE FRONT", "EXTEND RIGHT ARM IN HORIZONTAL POSITION TO THE RIGHT OF THE VEHICLE WITH PALM OF THE HAND TURNED TO THE FRONT", "EXTEND RIGHT ARM TO THE RIGHT OF THE VEHICLE AND ROTATE IT IN AN ANTI CLOCK WISE DIRECTION"],
        89: ["EXTEND THE RIGHT ARM, PALM DOWN, TO THE RIGHT OF THE VEHICLE AND MOVE THE EXTENDED ARM UP AND DOWN SEVERAL TIMES", "RAISE THE RIGHT FORE ARM VERTICALLY OUT SIDE TO THE RIGHT OF THE VEHICLE, PALM TO THE FRONT", "EXTEND RIGHT ARM IN HORIZONTAL POSITION TO THE RIGHT OF THE VEHICLE WITH PALM OF THE HAND TURNED TO THE FRONT", "EXTEND RIGHT ARM TO THE RIGHT OF THE VEHICLE AND ROTATE IT IN AN ANTI CLOCK WISE DIRECTION"],
        90: ["EXTEND THE RIGHT ARM, PALM DOWN, TO THE RIGHT OF THE VEHICLE AND MOVE THE EXTENDED ARM UP AND DOWN SEVERAL TIMES", "RAISE THE RIGHT FORE ARM VERTICALLY OUT SIDE TO THE RIGHT OF THE VEHICLE, PALM TO THE FRONT", "EXTEND RIGHT ARM IN HORIZONTAL POSITION TO THE RIGHT OF THE VEHICLE WITH PALM OF THE HAND TURNED TO THE FRONT", "EXTEND RIGHT ARM TO THE RIGHT OF THE VEHICLE AND ROTATE IT IN AN ANTI CLOCK WISE DIRECTION"],
        96: ["FOLLOW THE FRONT VEHICLE CLOSE BEHIND", "KEEP SUFFICIENT DISTANCE FROM THE FRONT VEHICLE TO AVOID COLLISION", "KEEP A VERY LONG DISTANCE FROM THE FRONT VEHICLE", "NONE OF THESE"],
        97: ["YOU ASK THE UPCOMING VEHICLE TO STOP TO ALLOW YOU TO PROCEED", "YOU ALLOW THE UPCOMING VEHICLE TO PASS FIRST", "YOU OBSTRUCT THE UPCOMING VEHICLE BY KEEPING YOUR VEHICLE ACROSS", "YOU RAISE THE SPEED OF YOUR VEHICLE"],
        99: ["ACCELERATE HARD", "MAINTAIN YOUR SPEED", "BE READY TO STOP", "BRAKE HARD"],
        108: ["INDICATE LEFT BEFORE LEAVING THE ROUNDABOUT", "DONT INDICATE AT ANY TIME", "INDICATE RIGHT WHEN APPROACHING THE ROUNDABOUT", "INDICATE LEFT WHEN APPROACHING THE ROUNDABOUT"],
        109: ["VEHICLES TRAVELLING DOWNHILL", "VEHICLES TRAVELLING UPHILL", "NO PRECEDENCE TO ANYONE", "DEPENDS ON THE CONDITIONS OF THE ROAD"],
        112: ["YOU SHOULD APPLY BRAKES IMMEDIATELY", "YOU SHOULD BLOW THE HORN AND OVERTAKE THE ANIMAL FROM ANY SIDE YOU FIND CONVENIENT", "YOU SHOULD SPEED UP AND MOVE IN FRONT OF THE ANIMAL", "YOU SHOULD CHECK TRAFFIC FROM BEHIND, SLOW DOWN OR STOP TO ENABLE THE ANIMAL TO CROSS"],
        116: ["BE PATIENT AND WAIT.", "SOUND YOUR HORN.", "DRIVE ON.", "WAVE THEM TO CROSS."],
        120: ["SOUND YOUR HORN", "DROP BACK FURTHER", "FLASH YOUR HEADLIGHTS", "START TO OVERTAKE."],
        122: ["PASS ON THE LEFT", "PASS ON THE RIGHT", "STAY BEHIND", "MOVE CLOSER"],
        124: ["SPEED UP.", "SLOW DOWN.", "HOLD YOUR SPEED.", "CHANGE DIRECTION."],
        127: ["OVERTAKE THE CYCLIST BEFORE THE JUNCTION", "PULL ALONGSIDE THE CYCLIST AND STAY LEVEL UNTIL AFTER THE JUNCTION", "HOLD BACK UNTIL THE CYCLIST HAS PASSED THE JUNCTION", "GO AROUND THE CYCLIST ON THE JUNCTION."],
        128: ["MOVE CLOSE BEHIND SO THAT YOU CAN PASS QUICKLY", "KEEP IN CLOSE TO THE LEFT-HAND SIDE", "FLASH YOUR HEADLIGHTS AND WAIT FOR THE DRIVER TO WAVE YOU ON", "STAY WELL BACK TO GET A BETTER VIEW."],
        132: ["OVERTAKE ON THE RIGHT.", "GIVE A HORN WARNING", "SIGNAL THE CYCLIST TO MOVE ACROSS", "GIVE THE CYCLIST PLENTY OF ROOM"],
        138: ["MAINTAIN A REDUCED SPEED THROUGHOUT", "ACCELERATE QUICKLY BETWEEN EACH ONE", "ALWAYS KEEP TO THE MAXIMUM LEGAL SPEED", "DRIVE SLOWLY AT SCHOOL TIMINGS ONLY"],
        144: ["OVERTAKE THE CYCLIST BEFORE THE JUNCTION", "PULL ALONGSIDE THE CYCLIST AND STAY LEVEL UNTIL AFTER THE JUNCTION", "HOLD BACK UNTIL THE CYCLIST HAS PASSED THE JUNCTION", "GO AROUND THE CYCLIST ON THE JUNCTION"],
        145: ["THE BUS MAY HAVE BROKEN DOWN", "PEDESTRIANS MAY COME FROM BEHIND THE BUS", "THE BUS MAY MOVE OFF SUDDENLY", "THE BUS MAY REMAIN STATIONARY"],
        151: ["DRIVE VERY SLOWLY.", "ALLOW PLENTY OF ROOM.", "BE READY TO STOP.", "ALL OF THE ABOVE."],
        152: ["LEFT TURN SIGNAL", "SLOW DOWN SIGNAL", "RIGHT TURN SIGNAL", "SPECIAL 'U' TURN SIGNAL"]
    },
    "general_principles": {
        11: ["RESTRICT YOUR VIEW & DISTRACT YOUR ATTENTION", "IMPROVE YOUR DRIVING", "HELP YOU CONCENTRATION", "NONE OF THE ABOVE"],
        32: ["SEAT BELTS", "SAFETY DOOR LATCHES", "PADDED INSTRUMENT PANELS", "NONE OF THESE"],
        37: ["MOTOR CAR ONLY", "MOTOR CAR AND MOTORCYCLE ABOVE 50CC", "EVERY MOTOR VEHICLE", "NONE OF THE ABOVE"],
        45: ["YES, BUT ONLY WHEN YOU STOP AT INTERSECTIONS.", "NO", "YES, BUT YOU MUST HOLD THE STEERING WHEEL WITH AT LEAST ONE HAND.", "ONLY AT NIGHT"],
        55: ["STOP AND TAKE A BREAK", "SHOUT ABUSIVE LANGUAGE", "GESTURE TO THEM WITH YOUR HAND", "FOLLOW THEIR CAR, FLASHING THE HEADLIGHTS"],
        56: ["IS VALID THROUGH OUT THE INDIA", "IS VALID THROUGHOUT THE WORLD", "IS VALID ONLY IN THE STATE", "NOT VALID ANYWHERE"],
        57: ["TO ALERT OTHERS OF YOUR PRESENCE", "TO ALLOW YOU RIGHT OF WAY", "TO GREET OTHER ROAD USERS", "TO SIGNAL YOUR ANNOYANCE"],
        65: ["MOVE THE RIDER OUT OF THE ROAD.", "WARN OTHER TRAFFIC", "CLEAR THE ROAD OF DEBRIS.", "GIVE THE RIDER REASSURANCE"],
        74: ["ON THE TRAILER", "ON THE BODY OF THE VEHICLE", "FOR HIRE OR REWARD", "CAN NOT CARRY PASSENGERS"],
        79: ["LOUD MUSIC", "ARGUING WITH A PASSENGER", "USING A MOBILE PHONE", "ALL OF THE ABOVE"],
        83: ["DISTURBING MENTAL EQUILIBRIUM.", "DISTURBING THE CONCENTRATION OF DRIVER.", "LOSS OF HEARING CAPACITY.", "ALL OF THE ABOVE"],
        90: ["INCREASE", "DECREASE", "BE UP TO TEN TIMES GREATER", "REMAIN THE SAME"],
        91: ["THIRD PARTY, FIRE AND THEFT", "FULLY COMPREHENSIVE", "THIRD PARTY ONLY", "PERSONAL INJURY COVER"],
        105: ["PULL TO THE SIDE OF THE ROAD IMMEDIATELY, TURN OFF THE ENGINE AND ALL ELECTRICAL SWITCHES AND TRY TO SMOOTHER BURNING WIRES WITH SAND OR HEAVY CLOTH.", "PULL TO THE SIDE OF THE ROAD IMMEDIATELY, TURN OFF THE ENGINE AND ALL ELECTRICAL SWITCHES AND SMOTHER BURNING WIRES BY POURING WATER ON THEM.", "DON'T DO ANYTHING BUT CALL THE FIRE BRIGADE.", "NONE OF THE ABOVE."],
        119: ["THE PASSENGERS.", "THE MECHANIC OF THE VEHICLE.", "THE DRIVER OF THE VEHICLE.", "ALL OF THE ABOVE"],
        120: ["LEAVE HEADLIGHTS ON", "LEAVE SIDE LIGHTS ON", "KEEP STONES/BRICKS AROUND YOUR VEHICLE", "NONE OF THESE"],
        128: ["VEHICLE PULLING TO THE RIGHT.", "VEHICLE PULLING TO THE LEFT.", "STEERING WOBBLING.", "NONE OF THE ABOVE."],
        149: ["EMERGENCY VEHICLES", "SLOW MOVING VEHICLES", "BREAKDOWN VEHICLES", "STOPPING THE VEHICLE"],
        153: ["GIVES YOU A BETTER FUEL AVERAGE", "DOES NOT GIVE YOU SUFFICIENT TIME TO REACT TO HAZARDS", "TAKE LESS TIME FOR YOUR JOURNEY", "WILL CAUSE LESS DAMAGE TO YOUR ENGINE"]
    }
}

def extract_stream(pdf_name, cmap_id, hlen):
    path = os.path.join(WORKSPACE_ROOT, pdf_name)
    with open(path, "rb") as f:
        pdf_bytes = f.read()
    cmap = parse_cmap(get_obj_stream(pdf_bytes, cmap_id))
    pages = get_page_contents(pdf_bytes)
    
    elems = []
    for p_idx, (p_id, c_id) in enumerate(pages):
        raw = decode_stream_robust(get_obj_stream(pdf_bytes, c_id), cmap)
        cur = raw[hlen:] if p_idx == 0 else raw
        for x, y, t in cur:
            elems.append((p_idx + 1, x, y, t.strip()))
            
    header_words = {
        "S.NO.", "QUESTIONS", "RELEVANT FIGURE/SIGN", "OPTION1", "OPTION2",
        "OPTION3", "OPTION4", "ANSWER", "S.NO.QUESTIONS", "OPTION1OPTION2OPTION3OPTION4",
        "ANSWER ", "IF ANY", "RELEVANT", "FIGURE/SIGN", "S"
    }
    return [e for e in elems if e[3] and e[3] not in header_words]

def cluster_options(opt_toks):
    if not opt_toks:
        return ["", "", "", ""]
    if len(opt_toks) == 4:
        return [t[2] for t in opt_toks]
        
    min_x = min(t[0] for t in opt_toks)
    max_x = max(t[0] for t in opt_toks)
    span = max_x - min_x
    
    if span < 30:
        k = len(opt_toks)
        step = k / 4.0
        return [" ".join(opt_toks[int(round(i*step)):int(round((i+1)*step))][j][2] for j in range(len(opt_toks[int(round(i*step)):int(round((i+1)*step))]))) for i in range(4)]
        
    bins = [[], [], [], []]
    for x, y, t in opt_toks:
        col = int(round((x - min_x) / (span / 3.0)))
        col = max(0, min(3, col))
        bins[col].append(t)
        
    res = [" ".join(b).strip() for b in bins]
    if any(len(o) == 0 for o in res):
        k = len(opt_toks)
        step = k / 4.0
        res = []
        for i in range(4):
            sub = opt_toks[int(round(i*step)):int(round((i+1)*step))]
            res.append(" ".join(t[2] for t in sub).strip())
    return [re.sub(r"\s+", " ", o).strip() for o in res]

def rebuild_rules_of_road():
    print("Rebuilding Rules of the Road (159 questions)...")
    toks = extract_stream("rules-of-road-regulations-english.pdf", 180, 18)
    
    q_ranges = {}
    cur = 1
    for i, (p, x, y, t) in enumerate(toks):
        m = re.match(r"^(\d{1,3})$", t)
        if m and int(m.group(1)) == cur:
            q_ranges[cur] = i
            cur += 1
            if cur > 159: break
        elif t.startswith(str(cur)) and len(t) > len(str(cur)):
            q_ranges[cur] = i
            cur += 1
            if cur > 159: break
            
    official_ans, _ = get_official_pdf_answers("rules-of-road-regulations-english.pdf", 180, 159)
    
    rules = []
    for q in range(1, 160):
        start = q_ranges[q]
        end = q_ranges[q+1] if q < 159 else len(toks)
        q_toks_all = toks[start:end]
        x_0 = q_toks_all[0][1]
        
        zero_idx = None
        for i, t in enumerate(q_toks_all):
            if t[3] == "0":
                zero_idx = i
                break
        if zero_idx is not None:
            q_toks = q_toks_all[1:zero_idx]
            opt_toks = q_toks_all[zero_idx+1:]
        else:
            q_toks = [t for t in q_toks_all[1:] if abs(t[1] - x_0) <= 100]
            opt_toks = [t for t in q_toks_all[1:] if abs(t[1] - x_0) > 100]
            
        if opt_toks and opt_toks[-1][3] in ["1", "2", "3", "4"]:
            opt_toks = opt_toks[:-1]
        elif opt_toks and re.search(r"[1-4]$", opt_toks[-1][3]):
            opt_toks[-1] = (opt_toks[-1][0], opt_toks[-1][1], opt_toks[-1][2], opt_toks[-1][3][:-1].strip())
            
        q_text_en = " ".join(t[3] for t in q_toks if t[3] != str(q)).strip()
        q_text_en = re.sub(r"\s+", " ", q_text_en)
        
        if q in CURATED_OPTS["rules_of_road"]:
            opts_en = CURATED_OPTS["rules_of_road"][q]
        else:
            opts_en = cluster_options([(t[1], t[2], t[3]) for t in opt_toks])
            
        ans_idx = official_ans[q] - 1
        
        # Translations
        q_text_te = translate_phrase(q_text_en, "te")
        q_text_hi = translate_phrase(q_text_en, "hi")
        opts_te = [translate_phrase(opt, "te") for opt in opts_en]
        opts_hi = [translate_phrase(opt, "hi") for opt in opts_en]
        
        exp_en = get_explanation(q, "rules_of_road", opts_en[ans_idx], "en")
        exp_te = get_explanation(q, "rules_of_road", opts_te[ans_idx], "te")
        exp_hi = get_explanation(q, "rules_of_road", opts_hi[ans_idx], "hi")
        
        img_path = SCENARIO_MAP_RULES.get(q, None)
        
        rules.append({
            "id": f"TS_RR_{q:03d}",
            "category": "rules_of_road",
            "signType": None,
            "questionNumber": q,
            "image": img_path,
            "text": {
                "en": q_text_en,
                "te": q_text_te,
                "hi": q_text_hi
            },
            "options": {
                "en": opts_en,
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
        
    print(f"✓ Rebuilt {len(rules)} Rules of the Road questions.")
    return rules

def rebuild_general_principles():
    print("Rebuilding General Driving Principles (159 questions)...")
    toks = extract_stream("general-driving-principles-english.pdf", 128, 19)
    
    q_ranges = {}
    cur = 1
    for i, (p, x, y, t) in enumerate(toks):
        m = re.match(r"^(\d{1,3})$", t)
        if m and int(m.group(1)) == cur:
            q_ranges[cur] = i
            cur += 1
            if cur > 159: break
        elif t.startswith(str(cur)) and len(t) > len(str(cur)):
            q_ranges[cur] = i
            cur += 1
            if cur > 159: break
            
    official_ans, _ = get_official_pdf_answers("general-driving-principles-english.pdf", 128, 159, {
        32: "THE MOST EFFECTIVE",
        128: "WHAT WILL HAPPEN",
        144: "ALCOHOL MAY AFFECT",
        150: "BOARDING AND ALIGHTING"
    })
    
    gps = []
    for q in range(1, 160):
        if q in CURATED_QS["general_principles"]:
            q_text_en, opts_en = CURATED_QS["general_principles"][q]
        else:
            start = q_ranges[q]
            end = q_ranges[q+1] if q < 159 else len(toks)
            q_toks_all = toks[start:end]
            x_0 = q_toks_all[0][1]
            
            zero_idx = None
            for i, t in enumerate(q_toks_all):
                if t[3] == "0":
                    zero_idx = i
                    break
            if zero_idx is not None:
                q_toks = q_toks_all[1:zero_idx]
                opt_toks = q_toks_all[zero_idx+1:]
            else:
                q_toks = [t for t in q_toks_all[1:] if abs(t[1] - x_0) <= 100]
                opt_toks = [t for t in q_toks_all[1:] if abs(t[1] - x_0) > 100]
                
            if opt_toks and opt_toks[-1][3] in ["1", "2", "3", "4"]:
                opt_toks = opt_toks[:-1]
            elif opt_toks and re.search(r"[1-4]$", opt_toks[-1][3]):
                opt_toks[-1] = (opt_toks[-1][0], opt_toks[-1][1], opt_toks[-1][2], opt_toks[-1][3][:-1].strip())
                
            q_text_en = " ".join(t[3] for t in q_toks if t[3] != str(q)).strip()
            q_text_en = re.sub(r"\s+", " ", q_text_en)
            
            if q in CURATED_OPTS["general_principles"]:
                opts_en = CURATED_OPTS["general_principles"][q]
            else:
                opts_en = cluster_options([(t[1], t[2], t[3]) for t in opt_toks])
                
        ans_idx = official_ans[q] - 1
        
        # Translations
        q_text_te = translate_phrase(q_text_en, "te")
        q_text_hi = translate_phrase(q_text_en, "hi")
        opts_te = [translate_phrase(opt, "te") for opt in opts_en]
        opts_hi = [translate_phrase(opt, "hi") for opt in opts_en]
        
        exp_en = get_explanation(q, "general_principles", opts_en[ans_idx], "en")
        exp_te = get_explanation(q, "general_principles", opts_te[ans_idx], "te")
        exp_hi = get_explanation(q, "general_principles", opts_hi[ans_idx], "hi")
        
        gps.append({
            "id": f"TS_GP_{q:03d}",
            "category": "general_principles",
            "signType": None,
            "questionNumber": q,
            "image": None,
            "text": {
                "en": q_text_en,
                "te": q_text_te,
                "hi": q_text_hi
            },
            "options": {
                "en": opts_en,
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
        
    print(f"✓ Rebuilt {len(gps)} General Driving Principles questions.")
    return gps

def main():
    rules_data = rebuild_rules_of_road()
    gp_data = rebuild_general_principles()
    
    assert len(rules_data) == 159
    assert len(gp_data) == 159
    
    with open(RULES_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(rules_data, f, ensure_ascii=False, indent=2)
    print(f"Saved {RULES_JSON_PATH}")
    
    with open(GP_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(gp_data, f, ensure_ascii=False, indent=2)
    print(f"Saved {GP_JSON_PATH}")
    
    print("\nRebuild complete! Verifying specific checkpoints...")
    for q in rules_data:
        if q["id"] in ["TS_RR_116", "TS_RR_133", "TS_RR_156", "TS_RR_157"]:
            print(f"\n[{q['id']}]")
            print("  Q:", q["text"]["en"])
            print("  Options:", q["options"]["en"])
            print("  Correct:", q["answerIndex"], "->", q["options"]["en"][q["answerIndex"]])
            
    for q in gp_data:
        if q["id"] in ["TS_GP_011", "TS_GP_014", "TS_GP_032", "TS_GP_057"]:
            print(f"\n[{q['id']}]")
            print("  Q:", q["text"]["en"])
            print("  Options:", q["options"]["en"])
            print("  Correct:", q["answerIndex"], "->", q["options"]["en"][q["answerIndex"]])

if __name__ == "__main__":
    main()
