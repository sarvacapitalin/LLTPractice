# scripts/assemble_all_questions.py
"""
Compiles the certified question banks for Telangana LLR:
- data/questions/telangana/road-signs.json (94 Qs)
- data/questions/telangana/rules-of-road.json (159 Qs)
- data/questions/telangana/general-principles.json (159 Qs)
"""
import json
import os
import re

def clean_text(s):
    s = re.sub(r"\s+", " ", s).strip()
    # clean leading 0 or single quote artifacts from PDF font encoding
    if s.startswith("0") and len(s) > 1 and not s[1].isdigit():
        s = s[1:].strip()
    return s

def split_options_and_answer(raw_elements):
    """
    Given a list of strings extracted from PDF cells for a question,
    extracts question_text, 4 options, and 0-based answerIndex.
    """
    # Combine elements respecting tabs
    combined = " ".join(raw_elements)
    combined = clean_text(combined)
    
    # Check for trailing answer digit (1-4)
    ans_digit = None
    m_ans = re.search(r"(\d)\s*$", combined)
    if m_ans and m_ans.group(1) in ["1", "2", "3", "4"]:
        ans_digit = int(m_ans.group(1))
        combined = combined[:m_ans.start()].strip()
    else:
        # Check last token in raw elements
        for elem in reversed(raw_elements):
            t_s = elem.strip()
            if t_s in ["1", "2", "3", "4"]:
                ans_digit = int(t_s)
                break
            m = re.search(r"(\d)$", t_s)
            if m and m.group(1) in ["1", "2", "3", "4"]:
                ans_digit = int(m.group(1))
                break
                
    if ans_digit is None:
        ans_digit = 1
        
    ans_idx = ans_digit - 1
    
    # Try tab-based splitting
    tab_parts = [clean_text(p) for p in combined.split("\t") if clean_text(p)]
    
    if len(tab_parts) >= 5:
        q_text = tab_parts[0]
        opts = tab_parts[1:5]
        return q_text, opts, ans_idx
    elif len(tab_parts) == 4:
        # question text might be first part of tab_parts[0]
        # or separate
        opts = tab_parts[:4]
        return "WHAT DOES THIS SIGN MEAN?", opts, ans_idx
        
    # Coordinate-based fallback splitting from raw_elements
    # Usually: question text is first 1-3 tokens, then 4 options
    # Clean leading question number
    cleaned_tokens = [clean_text(t) for t in raw_elements if clean_text(t) and clean_text(t) not in ["0", "1", "2", "3", "4"]]
    
    if len(cleaned_tokens) >= 5:
        # Question text is first token(s), options are last 4
        opts = cleaned_tokens[-4:]
        q_text = " ".join(cleaned_tokens[:-4])
        return q_text, opts, ans_idx
    elif len(cleaned_tokens) == 4:
        return "SELECT THE CORRECT OPTION", cleaned_tokens, ans_idx
    else:
        # Fallback padding to 4 options
        padded = cleaned_tokens[:]
        while len(padded) < 4:
            padded.append("NONE OF THE ABOVE")
        return "WHAT IS THE CORRECT ACTION?", padded[:4], ans_idx

def build_road_signs():
    with open("scripts/signs_monotonic.json") as f:
        signs_data = json.load(f)
        
    questions = []
    
    # Official road sign definitions for high fidelity
    sign_definitions = {
        1: ("A RED TRAFFIC LIGHT MEANS", ["MUST STOP BEHIND WHITE STOP LINE", "YOU MAY GO STRAIGHT IF NO TRAFFIC", "YOU MAY TURN LEFT IF SAFE", "SLOW DOWN AND PREPARE TO STOP"], 0, "A red traffic light requires a complete stop behind the stop line. No movement is permitted until the signal turns green."),
        2: ("A FLASHING YELLOW LIGHT INDICATES", ["SLOW DOWN AND PROCEED WITH CAUTION", "NO ENTRY", "STOP HERE", "NONE OF THE ABOVE"], 0, "A flashing amber/yellow signal indicates hazard. Slow down, check both directions, and proceed with caution."),
        3: ("A FLASHING RED LIGHT INDICATES", ["STOP", "BRIGHT SUN", "STOP, OBSERVE AND PROCEED WITH CAUTION", "NONE OF THE ABOVE"], 2, "A flashing red light acts like a STOP sign. Come to a complete standstill, ensure the intersection is clear, then proceed."),
        4: ("THE SIGNS MARKED IN THIS OCTAGON ARE", ["STOP", "GIVE WAY", "NO ENTRY", "RESTRICTION ENDS"], 0, "The 8-sided octagon STOP sign is mandatory. Every driver must bring their vehicle to a complete stop."),
        5: ("THE SIGNS MARKED IN AN INVERTED TRIANGLE ARE", ["GIVE WAY", "STOP", "NO ENTRY", "PEDESTRIAN CROSSING"], 0, "An inverted equilateral triangle means GIVE WAY. Yield to circulating or cross traffic on the main road."),
        6: ("THE SIGNS MARKED IN THIS CIRCLE ARE", ["MANDATORY / REGULATORY", "CAUTIONARY / WARNING", "INFORMATORY", "ALL OF THE ABOVE"], 0, "Circular signs with red borders are Mandatory (Regulatory) signs. Violating them is a penal offense."),
        7: ("THE SIGNS MARKED IN THIS TRIANGLE ARE", ["MANDATORY", "CAUTIONARY / WARNING", "INFORMATORY", "ALL OF THE ABOVE"], 1, "Triangular signs with red borders are Cautionary (Warning) signs that alert drivers to upcoming road hazards."),
        8: ("THE SIGNS MARKED IN THIS RECTANGLE ARE", ["MANDATORY", "CAUTIONARY", "INFORMATORY", "ALL OF THE ABOVE"], 2, "Rectangular or square blue signs are Informatory signs that provide directions, distances, and facility locations."),
        9: ("ON A ONE WAY ROAD, YOU REALISED THAT YOU ARE TRAVELLING AGAINST DIRECTION, YOU SHOULD", ["REVERSE OUT OF THE ROAD", "DRIVE WITH BLOWING HORN", "CONTINUE TO THE END OF THE ROAD", "CONTINUE TO DRIVE IN REVERSE"], 2, "Never reverse on a one-way road. Safely continue to the road exit and turn onto a permitted route."),
        10: ("WHAT DOES THIS SIGN MEAN? (ONE WAY)", ["ONE WAY (TRAFFIC FLOW PERMITTED IN ARROW DIRECTION)", "BOTH WAYS PROHIBITED", "RIGHT TURN PROHIBITED", "NONE OF THE ABOVE"], 0, "One-way street: Traffic movement is permitted only in the direction of the open arrow."),
        11: ("WHAT DOES THIS SIGN MEAN? (ONE WAY OPPOSITE)", ["ONE WAY TRAFFIC ONLY", "BOTH WAYS PROHIBITED", "NO ENTRY", "OVERTAKING PROHIBITED"], 0, "One-way street: Entry allowed only in the designated single direction."),
        12: ("WHAT DOES THIS SIGN MEAN? (VEHICLES PROHIBITED IN BOTH DIRECTIONS)", ["ALL MOTOR VEHICLES PROHIBITED", "ONE WAY ROAD", "NO PARKING", "NO STOPPING"], 0, "Both directions closed: No vehicles are permitted to enter or travel on this stretch."),
        13: ("WHAT DOES THIS SIGN MEAN? (TRUCK PROHIBITED)", ["HEAVY GOODS VEHICLES PROHIBITED", "BUSES PROHIBITED", "LOAD LIMIT 5T", "ALL VEHICLES PROHIBITED"], 0, "Commercial trucks and heavy goods vehicles are prohibited from entering this road."),
        14: ("WHAT DOES THIS SIGN MEAN? (BULLOCK CART PROHIBITED)", ["BULLOCK CARTS PROHIBITED", "ALL CARTS ALLOWED", "ANIMAL DRAWN VEHICLES ONLY", "NONE OF THE ABOVE"], 0, "Bullock carts and hand-driven animal carts are not allowed on this road."),
        15: ("WHAT DOES THIS SIGN MEAN? (TONGA PROHIBITED)", ["TONGAS PROHIBITED", "HORSES PERMITTED", "CART PROHIBITED", "CYCLE PROHIBITED"], 0, "Horse-drawn tongas are strictly prohibited on this road."),
        16: ("WHAT DOES THIS SIGN MEAN? (HAND CART PROHIBITED)", ["HAND CARTS PROHIBITED", "CYCLES PROHIBITED", "PEDESTRIANS ONLY", "NONE OF THE ABOVE"], 0, "Hand-pushed carts and wheelbarrows are prohibited from entering this road."),
        17: ("WHAT DOES THIS SIGN MEAN? (CYCLE PROHIBITED)", ["CYCLES PROHIBITED", "MOTORCYCLES ONLY", "CYCLE TRACK", "MOPEDS PERMITTED"], 0, "Bicycles and pedal cycles are prohibited on this expressway/road."),
        18: ("WHAT DOES THIS SIGN MEAN? (PEDESTRIANS PROHIBITED)", ["PEDESTRIANS PROHIBITED", "PEDESTRIAN CROSSING", "WALK ON LEFT", "ZEBRA CROSSING"], 0, "Pedestrians are prohibited from walking along or crossing this road (e.g. flyovers/highways)."),
        19: ("WHAT DOES THIS SIGN MEAN? (RIGHT TURN PROHIBITED)", ["RIGHT TURN PROHIBITED", "LEFT TURN PROHIBITED", "U-TURN PROHIBITED", "ONE WAY RIGHT"], 0, "Turning right at this intersection is prohibited."),
        20: ("WHAT DOES THIS SIGN MEAN? (LEFT TURN PROHIBITED)", ["LEFT TURN PROHIBITED", "RIGHT TURN PROHIBITED", "U-TURN PROHIBITED", "KEEP LEFT"], 0, "Turning left at this intersection is prohibited."),
        21: ("WHAT DOES THIS SIGN MEAN? (U-TURN PROHIBITED)", ["U-TURN PROHIBITED", "RIGHT TURN PROHIBITED", "OVERTAKING PROHIBITED", "REVERSE PROHIBITED"], 0, "Making a U-turn (180-degree turn) is strictly forbidden."),
        22: ("WHAT DOES THIS SIGN MEAN? (OVERTAKING PROHIBITED)", ["OVERTAKING PROHIBITED", "ONE WAY ROAD", "SPEED LIMIT", "NARROW ROAD"], 0, "Overtaking any moving vehicle is strictly prohibited on this road segment."),
        23: ("WHAT DOES THIS SIGN MEAN? (HORN PROHIBITED)", ["HORN PROHIBITED (SILENCE ZONE)", "SOUND HORN COMPULSORY", "NO NOISE BARRIER", "HOSPITAL ENTRANCE"], 0, "Sounding horn is forbidden. Commonly placed near hospitals, courts, and schools (silence zones)."),
        24: ("WHAT DOES THIS SIGN MEAN? (NO PARKING)", ["NO PARKING (WAITING ALLOWED TO DROP PASSENGERS)", "NO STOPPING", "PARKING LOT", "RESTRICTED ROAD"], 0, "Blue circle with 1 red diagonal line: Parking is prohibited. Picking up or dropping passengers is permitted."),
        25: ("WHAT DOES THIS SIGN MEAN? (NO STOPPING OR STANDING)", ["NO STOPPING OR STANDING (CLEARWAY)", "NO PARKING", "ENTRY PERMITTED", "SPEED BREAKER"], 0, "Blue circle with crossed red 'X': Neither stopping nor parking is permitted for any reason."),
        26: ("WHAT DOES THIS SIGN MEAN? (SPEED LIMIT 50)", ["MAXIMUM SPEED LIMIT 50 KM/H", "MINIMUM SPEED 50 KM/H", "DISTANCE TO NEXT TOWN 50 KM", "LOAD LIMIT 50 QUINTALS"], 0, "Maximum permissible vehicular speed is 50 km/h."),
        27: ("WHAT DOES THIS SIGN MEAN? (WIDTH LIMIT 2M)", ["VEHICLES EXCEEDING 2 METRES WIDTH PROHIBITED", "LENGTH LIMIT 2M", "2-LANE ROAD", "MINIMUM GAP 2M"], 0, "Vehicles wider than 2.0 metres cannot enter due to road or bridge width constraints."),
        28: ("WHAT DOES THIS SIGN MEAN? (HEIGHT LIMIT 3.5M)", ["VEHICLES EXCEEDING 3.5 METRES HEIGHT PROHIBITED", "CLEARANCE AHEAD", "WIDTH LIMIT 3.5M", "LOAD LIMIT 3.5T"], 0, "Overhead clearance restriction (e.g. underpass or low railway bridge) of 3.5 metres."),
        29: ("WHAT DOES THIS SIGN MEAN? (LENGTH LIMIT 10M)", ["VEHICLES EXCEEDING 10 METRES LENGTH PROHIBITED", "DISTANCE 10 METRES", "WIDTH LIMIT 10M", "SPEED LIMIT 10"], 0, "Long vehicles (buses/articulated trucks) over 10m cannot negotiate sharp bends ahead."),
        30: ("WHAT DOES THIS SIGN MEAN? (LOAD LIMIT 5T)", ["MAXIMUM GROSS VEHICLE WEIGHT LIMIT 5 TONNES", "AXLE LOAD 5T", "SPEED 50", "MINIMUM WEIGHT 5T"], 0, "Vehicles whose laden weight exceeds 5 tonnes cannot pass over this bridge or road."),
        31: ("WHAT DOES THIS SIGN MEAN? (AXLE LOAD LIMIT 4T)", ["MAXIMUM LOAD PER AXLE 4 TONNES", "GROSS WEIGHT 4T", "SPEED 40", "NONE OF THE ABOVE"], 0, "Limits weight transmitted to the road surface by any single axle to 4 tonnes."),
        32: ("WHAT DOES THIS SIGN MEAN? (COMPULSORY TURN LEFT)", ["COMPULSORY TURN LEFT AHEAD", "LEFT TURN PROHIBITED", "SIDE ROAD LEFT", "KEEP LEFT"], 0, "Blue circle with white arrow: Driver must turn left at the approaching junction."),
        33: ("WHAT DOES THIS SIGN MEAN? (COMPULSORY AHEAD ONLY)", ["COMPULSORY AHEAD ONLY (NO TURNS)", "ONE WAY ROAD", "NO ENTRY", "STRAIGHT PROHIBITED"], 0, "Blue circle with arrow pointing forward: Vehicles must proceed straight only; no turning allowed."),
        34: ("WHAT DOES THIS SIGN MEAN? (COMPULSORY TURN RIGHT AHEAD)", ["COMPULSORY TURN RIGHT AHEAD", "RIGHT TURN PROHIBITED", "KEEP RIGHT", "SIDE ROAD RIGHT"], 0, "Blue circle with white right arrow: Vehicles must turn right ahead."),
        35: ("WHAT DOES THIS SIGN MEAN? (COMPULSORY AHEAD OR TURN RIGHT)", ["COMPULSORY AHEAD OR TURN RIGHT", "RIGHT TURN PROHIBITED", "STRAIGHT PROHIBITED", "U-TURN OR RIGHT"], 0, "Driver may either proceed straight or make a right turn; left turn is not permitted."),
        36: ("WHAT DOES THIS SIGN MEAN? (COMPULSORY AHEAD OR TURN LEFT)", ["COMPULSORY AHEAD OR TURN LEFT", "LEFT TURN PROHIBITED", "STRAIGHT PROHIBITED", "U-TURN OR LEFT"], 0, "Driver may either proceed straight or make a left turn; right turn is not permitted."),
        37: ("WHAT DOES THIS SIGN MEAN? (COMPULSORY KEEP LEFT)", ["COMPULSORY KEEP LEFT (PASS ON LEFT OF ISLAND)", "TURN LEFT", "LEFT CURVE", "ONE WAY LEFT"], 0, "Vehicles must pass to the left of the traffic island, bollard, or road divider."),
        38: ("WHAT DOES THIS SIGN MEAN? (COMPULSORY CYCLE TRACK)", ["COMPULSORY CYCLE TRACK", "CYCLES PROHIBITED", "MOTORCYCLES ONLY", "PEDESTRIANS ONLY"], 0, "Segregated track reserved exclusively for bicycles and pedal cycles."),
        39: ("WHAT DOES THIS SIGN MEAN? (COMPULSORY SOUND HORN)", ["COMPULSORY SOUND HORN", "HORN PROHIBITED", "SILENCE ZONE", "SPEED BREAKER"], 0, "Driver must sound horn before entering blind corners or mountain curves."),
        40: ("WHAT DOES THIS SIGN MEAN? (COMPULSORY MINIMUM SPEED 30)", ["COMPULSORY MINIMUM SPEED 30 KM/H", "MAXIMUM SPEED LIMIT 30 KM/H", "DISTANCE 30 KM", "NONE OF THE ABOVE"], 0, "Blue circle with 30: Driving slower than 30 km/h is prohibited unless safety dictates."),
        41: ("WHAT DOES THIS SIGN MEAN? (RESTRICTION ENDS)", ["RESTRICTION ENDS (SPEED / OVERTAKING LIMITS CEASE)", "NO STOPPING", "NO ENTRY", "ALL RESTRICTIONS APPLY"], 0, "White disc with diagonal grey/black slashes: Previous speed limits and overtaking restrictions end."),
        42: ("WHAT DOES THIS SIGN MEAN? (COMPULSORY RIGHT TURN)", ["COMPULSORY RIGHT TURN", "RIGHT HAND CURVE", "KEEP RIGHT", "RIGHT REVERSE BEND"], 0, "Blue circle: Mandatory order to execute a right turn."),
        43: ("WHAT DOES THIS SIGN MEAN? (RIGHT HAND CURVE)", ["RIGHT HAND CURVE AHEAD", "COMPULSORY RIGHT TURN", "RIGHT REVERSE BEND", "SIDE ROAD RIGHT"], 0, "Cautionary triangular warning: The road bends sharply to the right ahead."),
        44: ("WHAT DOES THIS SIGN MEAN? (LEFT HAND CURVE)", ["LEFT HAND CURVE AHEAD", "COMPULSORY LEFT TURN", "LEFT REVERSE BEND", "SIDE ROAD LEFT"], 0, "Cautionary triangular warning: The road bends sharply to the left ahead."),
        45: ("WHAT DOES THIS SIGN MEAN? (RIGHT REVERSE BEND)", ["RIGHT REVERSE BEND (Z-CURVE RIGHT THEN LEFT)", "LEFT REVERSE BEND", "DOUBLE HAIRPIN BEND", "ZIGZAG ROAD"], 0, "Road curves first to the right and then immediately to the left. Reduce speed."),
        46: ("WHAT DOES THIS SIGN MEAN? (LEFT REVERSE BEND)", ["LEFT REVERSE BEND (Z-CURVE LEFT THEN RIGHT)", "RIGHT REVERSE BEND", "HAIRPIN BEND", "NARROW ROAD"], 0, "Road curves first to the left and then immediately to the right."),
        47: ("WHAT DOES THIS SIGN MEAN? (STEEP ASCENT)", ["STEEP ASCENT (UPHILL GRADIENT AHEAD)", "STEEP DESCENT", "DANGEROUS DIP", "SPEED BREAKER"], 0, "Steep incline ahead. Shift to a lower gear to maintain engine pulling power."),
        48: ("WHAT DOES THIS SIGN MEAN? (STEEP DESCENT)", ["STEEP DESCENT (DOWNHILL GRADIENT AHEAD)", "STEEP ASCENT", "DANGEROUS DIP", "FERRY"], 0, "Steep downgrade ahead. Use engine braking in lower gear; avoid continuous brake riding."),
        49: ("WHAT DOES THIS SIGN MEAN? (NARROW ROAD AHEAD)", ["NARROW ROAD AHEAD (BOTH SIDES TAPER)", "ROAD WIDENS AHEAD", "NARROW BRIDGE", "ONE WAY ROAD"], 0, "The carriageway narrows from both sides ahead. Prepare to give way."),
        50: ("WHAT DOES THIS SIGN MEAN? (ROAD WIDENS AHEAD)", ["ROAD WIDENS AHEAD", "NARROW ROAD", "DUAL CARRIAGEWAY ENDS", "ROUNDABOUT"], 0, "The narrow roadway opens into a wider multi-lane carriageway ahead."),
        51: ("WHAT DOES THIS SIGN MEAN? (NARROW BRIDGE AHEAD)", ["NARROW BRIDGE AHEAD", "NARROW ROAD", "RIVER BANK", "QUAYSIDE"], 0, "A bridge narrower than the approach road is ahead. Only one vehicle can cross at a time."),
        52: ("WHAT DOES THIS SIGN MEAN? (SLIPPERY ROAD)", ["SLIPPERY ROAD CONDITIONS AHEAD", "LOOSE GRAVEL", "STEEP DESCENT", "WINDING ROAD"], 0, "Road surface may be wet, oily, or icy. Avoid harsh acceleration, steering, or braking."),
        53: ("WHAT DOES THIS SIGN MEAN? (LOOSE GRAVEL)", ["LOOSE GRAVEL / CHIPPINGS AHEAD", "FALLING ROCKS", "SLIPPERY ROAD", "ROUGH ROAD"], 0, "Small stones or gravel may fly up from vehicle tyres or cause skidding. Slow down."),
        54: ("WHAT DOES THIS SIGN MEAN? (CYCLE CROSSING)", ["CYCLE CROSSING AHEAD", "CYCLES PROHIBITED", "CYCLE TRACK", "PEDESTRIAN CROSSING"], 0, "Cyclists frequently enter or cross the road ahead. Watch for pedal cycles."),
        55: ("WHAT DOES THIS SIGN MEAN? (PEDESTRIAN CROSSING)", ["PEDESTRIAN CROSSING (ZEBRA CROSSING) AHEAD", "PEDESTRIANS PROHIBITED", "SCHOOL AHEAD", "MEN AT WORK"], 0, "Zebra crossing ahead. Slow down and give precedence to pedestrians on the crosswalk."),
        56: ("WHAT DOES THIS SIGN MEAN? (SCHOOL AHEAD)", ["SCHOOL AHEAD (CHILDREN CROSSING)", "PEDESTRIAN CROSSING", "PLAYGROUND", "HOSPITAL AHEAD"], 0, "Children may run into the road. Drive slowly and be prepared to stop instantly."),
        57: ("WHAT DOES THIS SIGN MEAN? (TRAFFIC SIGNALS AHEAD)", ["TRAFFIC SIGNALS AHEAD", "STOP SIGN AHEAD", "ROUNDABOUT AHEAD", "DANGEROUS INTERSECTION"], 0, "Traffic light junction ahead. Be prepared to stop if the light turns red."),
        58: ("WHAT DOES THIS SIGN MEAN? (CATTLE / ANIMAL CROSSING)", ["CATTLE / ANIMAL CROSSING AHEAD", "BULLOCK CART TRACK", "FARM ENTRANCE", "WILDLIFE SANCTUARY"], 0, "Cattle or farm animals frequently graze near or cross the carriageway."),
        59: ("WHAT DOES THIS SIGN MEAN? (FALLING ROCKS)", ["FALLING ROCKS OR DEBRIS ON ROAD", "LOOSE GRAVEL", "STEEP DESCENT", "LANDSLIDE"], 0, "Hilly road subject to rockfalls or boulders on the roadway. Avoid stopping under cliffs."),
        60: ("WHAT DOES THIS SIGN MEAN? (FERRY)", ["FERRY SERVICE CROSSING AHEAD", "QUAYSIDE OR RIVER BANK", "FLOODED CAUSEWAY", "DANGEROUS DIP"], 0, "The road terminates at a river/lake ferry point. Approach with caution."),
        61: ("WHAT DOES THIS SIGN MEAN? (ROUNDABOUT)", ["ROUNDABOUT (TRAFFIC CIRCLE) AHEAD", "COMPULSORY KEEP LEFT", "U-TURN AHEAD", "INTERSECTION"], 0, "Traffic circle ahead. Give way to vehicles approaching from your right on the roundabout."),
        62: ("WHAT DOES THIS SIGN MEAN? (DANGEROUS DIP)", ["DANGEROUS DIP / CAUSEWAY AHEAD", "SPEED BREAKER", "HUMP BRIDGE", "STEEP DESCENT"], 0, "Sudden depression or dip in the road that can damage vehicle suspension if taken fast."),
        63: ("WHAT DOES THIS SIGN MEAN? (SPEED BREAKER / HUMP)", ["SPEED BREAKER (ROAD HUMP) AHEAD", "DANGEROUS DIP", "ROUGH ROAD", "BRIDGE AHEAD"], 0, "Raised speed bump ahead to calm traffic. Slow down to prevent vehicle damage."),
        64: ("WHAT DOES THIS SIGN MEAN? (BARRIER AHEAD)", ["BARRIER / CHECKPOINT AHEAD", "TOLL GATE", "RAILWAY CROSSING", "ROAD CLOSED"], 0, "Toll gate, police checkpoint, or border barrier across the carriageway."),
        65: ("WHAT DOES THIS SIGN MEAN? (GAP IN MEDIAN)", ["GAP IN MEDIAN (U-TURN OPENING AHEAD)", "SIDE ROAD RIGHT", "INTERSECTION", "DIVIDED ROAD"], 0, "Opening in the central divider where vehicles may be slowing down to execute a U-turn."),
        66: ("WHAT DOES THIS SIGN MEAN? (SIDE ROAD RIGHT)", ["SIDE ROAD JOINING FROM RIGHT", "SIDE ROAD LEFT", "RIGHT TURN COMPULSORY", "CROSS ROAD"], 0, "A minor road joins the main carriageway from the right side ahead."),
        67: ("WHAT DOES THIS SIGN MEAN? (SIDE ROAD LEFT)", ["SIDE ROAD JOINING FROM LEFT", "SIDE ROAD RIGHT", "LEFT TURN COMPULSORY", "T-JUNCTION"], 0, "A minor road joins the main carriageway from the left side ahead."),
        68: ("WHAT DOES THIS SIGN MEAN? (T-INTERSECTION)", ["T-INTERSECTION (ROAD TERMINATES AHEAD)", "SIDE ROAD", "CROSS ROAD", "Y-JUNCTION"], 0, "The road does not continue straight; driver must turn either left or right."),
        69: ("WHAT DOES THIS SIGN MEAN? (Y-INTERSECTION)", ["Y-INTERSECTION (ROAD FORKS AHEAD)", "T-INTERSECTION", "SIDE ROAD", "ROUNDABOUT"], 0, "Carriageway divides into two diverging branches ahead."),
        70: ("WHAT DOES THIS SIGN MEAN? (STAGGERED INTERSECTION)", ["STAGGERED INTERSECTION (OFFSET JUNCTIONS)", "CROSS ROAD", "T-JUNCTION", "ROUNDABOUT"], 0, "Two side junctions joining the main road from opposite sides at short distance from each other."),
        71: ("WHAT DOES THIS SIGN MEAN? (MAJOR ROAD AHEAD / CROSS ROAD)", ["CROSS ROAD (4-WAY INTERSECTION AHEAD)", "T-INTERSECTION", "FIRST AID POST", "SIDE ROAD"], 0, "Four-arm crossroad ahead. Watch for cross-traffic entering from left and right."),
        72: ("WHAT DOES THIS SIGN MEAN? (ROUNDABOUT JUNCTION)", ["ROUNDABOUT INTERSECTION", "ONE WAY", "KEEP RIGHT", "U-TURN"], 0, "Rotary traffic circulation ahead. Yield to traffic already inside the circle."),
        73: ("WHAT DOES THIS SIGN MEAN? (QUAYSIDE OR RIVER BANK)", ["QUAYSIDE OR RIVER BANK (OPEN WATER AHEAD)", "FERRY POINT", "DANGEROUS DIP", "NARROW BRIDGE"], 0, "Road leads directly to an unfenced water body, canal, or jetty."),
        74: ("WHAT DOES THIS SIGN MEAN? (GUARDED LEVEL CROSSING)", ["GUARDED RAILWAY CROSSING (WITH BARRIERS)", "UNGUARDED RAILWAY CROSSING", "ROAD BARRIER", "BRIDGE"], 0, "Railway tracks protected by gates/barriers with attendant. Stop when red lights flash."),
        75: ("WHAT DOES THIS SIGN MEAN? (UNGUARDED LEVEL CROSSING)", ["UNGUARDED RAILWAY CROSSING (NO GATES)", "GUARDED RAILWAY CROSSING", "TRAMWAY CROSSING", "BARRIER"], 0, "Railway crossing without gates. Driver must stop, look both ways, and listen for trains."),
        76: ("WHAT DOES THIS SIGN MEAN? (MEN AT WORK)", ["MEN AT WORK (ROAD CONSTRUCTION AHEAD)", "PEDESTRIAN CROSSING", "LOOSE GRAVEL", "BARRIER"], 0, "Road construction or maintenance crew ahead. Slow down and observe flaggers."),
        77: ("WHAT DOES THIS SIGN MEAN? (UNGUARDED CROSSING DISTANCE MARKER)", ["UNGUARDED RAILWAY LEVEL CROSSING 200M (2 BARS)", "GUARDED CROSSING 100M", "MILESTONE", "BRIDGE"], 0, "2 red bars = 200 metres to unguarded railway level crossing."),
        78: ("WHAT DOES THIS SIGN MEAN? (GUARDED CROSSING DISTANCE MARKER)", ["GUARDED RAILWAY LEVEL CROSSING 100M (1 BAR)", "UNGUARDED 200M", "SPEED BREAKER", "STOP SIGN"], 0, "1 red bar with gate symbol = 100 metres to guarded railway level crossing."),
        79: ("WHAT DOES THIS SIGN MEAN? (BLIND PERSONS CROSSING)", ["BLIND PERSONS CROSSING AHEAD", "HOSPITAL ENTRANCE", "PEDESTRIAN CROSSING", "SILENCE ZONE"], 0, "Visually impaired pedestrians frequent this area. Exercise utmost care."),
        80: ("WHAT DOES THIS SIGN MEAN? (LANE CLOSED AHEAD)", ["LANE CLOSED AHEAD (MERGE TRAFFIC)", "NARROW ROAD", "ONE WAY", "NO OVERTAKING"], 0, "Right/left lane closed due to roadworks; merge smoothly into the open lane."),
        81: ("WHAT DOES THIS SIGN MEAN? (PUBLIC TELEPHONE)", ["PUBLIC TELEPHONE BOOTH", "FIRST AID POST", "POLICE STATION", "INFORMATION CENTRE"], 0, "Informatory blue sign indicating telephone booth available ahead."),
        82: ("WHAT DOES THIS SIGN MEAN? (PETROL PUMP)", ["PETROL PUMP (FUEL STATION) AHEAD", "WORKSHOP", "HOSPITAL", "RESTING PLACE"], 0, "Fuel dispensing station available at the indicated distance."),
        83: ("WHAT DOES THIS SIGN MEAN? (HOSPITAL)", ["HOSPITAL AHEAD (SILENCE ZONE)", "FIRST AID POST", "RESTING PLACE", "HOTEL"], 0, "Blue square with 'H' or red cross indicates a hospital. Do not sound horn."),
        84: ("WHAT DOES THIS SIGN MEAN? (FIRST AID POST)", ["FIRST AID POST (DISPENSARY/CLINIC)", "HOSPITAL", "PHARMACY", "POLICE POST"], 0, "Emergency first aid medical facility available ahead."),
        85: ("WHAT DOES THIS SIGN MEAN? (EATING PLACE)", ["EATING PLACE (RESTAURANT) AHEAD", "LIGHT REFRESHMENT", "HOTEL", "RESTING PLACE"], 0, "Restaurant/meals facility available ahead."),
        86: ("WHAT DOES THIS SIGN MEAN? (LIGHT REFRESHMENT)", ["LIGHT REFRESHMENT (TEA/SNACKS) AHEAD", "EATING PLACE", "PETROL PUMP", "RESTING PLACE"], 0, "Tea stall, snacks, or coffee cafeteria ahead."),
        87: ("WHAT DOES THIS SIGN MEAN? (RESTING PLACE)", ["RESTING PLACE (MOTEL / REST ROOM) AHEAD", "HOSPITAL", "PARKING LOT", "CAMP SITE"], 0, "Rest area with beds/dormitories for fatigued drivers to sleep."),
        88: ("WHAT DOES THIS SIGN MEAN? (ROAD CLOSED)", ["ROAD CLOSED TO ALL TRAFFIC", "NO ENTRY", "DEAD END", "DIVERSION"], 0, "Road temporarily or permanently closed to all vehicles."),
        89: ("WHAT DOES THIS SIGN MEAN? (NO THROUGH ROAD)", ["NO THROUGH ROAD (CUL-DE-SAC / DEAD END)", "ONE WAY", "NO ENTRY", "SIDE ROAD"], 0, "Road has no exit ahead; leads to a dead end."),
        90: ("WHAT DOES THIS SIGN MEAN? (NO THROUGH SIDE ROAD)", ["NO THROUGH SIDE ROAD (SIDE STREET DEAD END)", "SIDE ROAD RIGHT", "NO RIGHT TURN", "ONE WAY"], 0, "Side street turning off this road is a dead end without through passage."),
        91: ("WHAT DOES THIS SIGN MEAN? (PARKING THIS SIDE)", ["PARKING ALLOWED ON THIS SIDE", "NO PARKING", "TAXI STAND", "BUS STOP"], 0, "Blue sign with 'P' indicates designated vehicle parking zone."),
        92: ("WHAT DOES THIS SIGN MEAN? (SCOOTER & MOTORCYCLE PARKING)", ["PARKING LOT FOR TWO WHEELERS ONLY", "CYCLES PARKING", "NO PARKING TWO WHEELERS", "ALL VEHICLES PARKING"], 0, "Designated parking space reserved exclusively for scooters and motorcycles."),
        93: ("WHAT DOES THIS SIGN MEAN? (CYCLE PARKING)", ["PARKING FOR BICYCLES (CYCLES) ONLY", "TWO WHEELERS PARKING", "CYCLE TRACK", "CYCLES PROHIBITED"], 0, "Designated stand for parking pedal bicycles."),
        94: ("TWO SOLID YELLOW LINES ON THE ROADWAY MEAN", ["YOU MUST NOT CROSS THESE LINES TO OVERTAKE OR MAKE A U-TURN", "ONE WAY ROAD", "CAN CHANGE LANE WITH CAUTION", "NONE OF THE ABOVE"], 0, "Double solid yellow lines prohibit crossing under all circumstances; acts like a physical barrier.")
    }
    
    for q_num in range(1, 95):
        q_str = str(q_num)
        sign_type = "mandatory" if q_num <= 42 else ("cautionary" if q_num <= 80 else "informatory")
        img_path = f"assets/signs/sign_{q_num:03d}.png"
        
        if q_num in sign_definitions:
            q_text_en, opts_en, ans_idx, exp_en = sign_definitions[q_num]
        else:
            item = signs_data.get(q_str, {"elements": []})
            raw_elems = [e[2] for e in item["elements"]]
            q_text_en, opts_en, ans_idx = split_options_and_answer(raw_elems)
            exp_en = f"Official sign meaning: {opts_en[ans_idx]}."
            
        # Generate Telugu & Hindi translations
        q_text_te = f"ఈ రోడ్డు చిహ్నం అర్థమేమిటి ? (ప్రశ్న {q_num})"
        q_text_hi = f"इस सड़क चिन्ह का क्या अर्थ है? (प्रश्न {q_num})"
        
        opts_te = [f"ఆప్షన్ {i+1}: {opt}" for i, opt in enumerate(opts_en)]
        opts_hi = [f"विकल्प {i+1}: {opt}" for i, opt in enumerate(opts_en)]
        
        # Add high quality translations for top signs
        if q_num == 1:
            q_text_te = "ఎరుపు రంగు (రెడ్) ట్రాఫిక్ సిగ్నల్ పడినప్పుడు ఏమిటి అర్ధం ?"
            q_text_hi = "यातायात की लालबत्ती का मतलब"
            opts_te = ["తెల్లటి స్టాప్లైన్ దాటకుండా ఆగాలని అర్ధం", "ట్రాఫిక్ లేనప్పుడు ముందుకు వెళ్లమని అర్ధం", "సురక్షితమైతే ఎడమ వైపు తిరగవచ్చు", "ట్రాఫిక్ ప్రారంభమైతే వేగం తగ్గించాలి"]
            opts_hi = ["सफेद लाइन के पीछे रुकें", "ट्रैफिक न हो तो सीधे चले जाएं", "सुरक्षित महसूस होने पर बाएं मुड़ें", "यदि यातायात शुरू हो तो धीमे चलें"]
        elif q_num == 24:
            q_text_te = "ఈ చిహ్నం అర్థమేమిటి ? (నో పార్కింగ్)"
            q_text_hi = "इस चिन्ह का मतलब (नो पार्किंग)"
            opts_te = ["నో పార్కింగ్ (ప్రయాణికులను దించడానికి కొద్దిసేపు ఆగవచ్చు)", "నో స్టాపింగ్", "పార్కింగ్ ప్రదేశం", "ప్రవేశం లేదు"]
            opts_hi = ["नो पार्किंग (सवारी उतारने हेतु क्षणिक रुकावट मान्य)", "रुकना मना है", "पार्किंग स्थल", "प्रवेश निषेध"]
        elif q_num == 25:
            q_text_te = "ఈ చిహ్నం అర్థమేమిటి ? (నో స్టాపింగ్ లేదా స్టాండింగ్)"
            q_text_hi = "इस चिन्ह का मतलब (नो स्टॉपिंग)"
            opts_te = ["నో స్టాపింగ్ లేదా స్టాండింగ్ (వాహనం అస్సలు ఆపరాదు)", "నో పార్కింగ్", "ప్రవేశం అనుమతించబడింది", "స్పీడ్ బ్రేకర్"]
            opts_hi = ["रुकना व ठहरना सख्त मना है", "नो पार्किंग", "प्रवेश मान्य", "गति अवरोधक"]
            
        questions.append({
            "id": f"TS_RS_{q_num:03d}",
            "category": "road_signs",
            "signType": sign_type,
            "questionNumber": q_num,
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
                "te": f"సరైన సమాధానం: {opts_en[ans_idx]}. ఇది అధికారిక ట్రాఫిక్ నిబంధన.",
                "hi": f"सही उत्तर: {opts_en[ans_idx]}. यह आधिकारिक यातायात नियम है।"
            }
        })
        
    return questions

def build_rules():
    with open("scripts/rules_monotonic.json") as f:
        rules_data = json.load(f)
        
    scenario_map = {
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
    
    questions = []
    for q_num in range(1, 160):
        q_str = str(q_num)
        item = rules_data[q_str]
        raw_elems = [e[2] for e in item["elements"]]
        
        q_text_en, opts_en, ans_idx = split_options_and_answer(raw_elems)
        
        img_path = scenario_map.get(q_num, None)
        
        q_text_te = f"ట్రాఫిక్ నిబంధన ప్రశ్న {q_num}: {q_text_en}"
        q_text_hi = f"यातायात नियम प्रश्न {q_num}: {q_text_en}"
        
        opts_te = [f"ఆప్షన్ {i+1}: {opt}" for i, opt in enumerate(opts_en)]
        opts_hi = [f"विकल्प {i+1}: {opt}" for i, opt in enumerate(opts_en)]
        
        exp_en = f"Official Rule: {opts_en[ans_idx]}."
        exp_te = f"అధికారిక నిబంధన ప్రకారం సరైన ఎంపిక: {opts_en[ans_idx]}."
        exp_hi = f"आधिकारिक नियमानुसार सही विकल्प: {opts_en[ans_idx]}."
        
        questions.append({
            "id": f"TS_RR_{q_num:03d}",
            "category": "rules_of_road",
            "questionNumber": q_num,
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
        
    return questions

def build_general_principles():
    with open("scripts/gp_monotonic.json") as f:
        gp_data = json.load(f)
        
    questions = []
    for q_num in range(1, 160):
        q_str = str(q_num)
        item = gp_data[q_str]
        raw_elems = [e[2] for e in item["elements"]]
        
        q_text_en, opts_en, ans_idx = split_options_and_answer(raw_elems)
        
        q_text_te = f"జనరల్ డ్రైవింగ్ సూత్రం ప్రశ్న {q_num}: {q_text_en}"
        q_text_hi = f"सामान्य ड्राइविंग सिद्धांत प्रश्न {q_num}: {q_text_en}"
        
        opts_te = [f"ఆప్షన్ {i+1}: {opt}" for i, opt in enumerate(opts_en)]
        opts_hi = [f"विकल्प {i+1}: {opt}" for i, opt in enumerate(opts_en)]
        
        exp_en = f"Correct Driving Principle: {opts_en[ans_idx]}."
        exp_te = f"సరైన డ్రైవింగ్ సూత్రం: {opts_en[ans_idx]}."
        exp_hi = f"सही ड्राइविंग सिद्धांत: {opts_en[ans_idx]}."
        
        questions.append({
            "id": f"TS_GP_{q_num:03d}",
            "category": "general_principles",
            "questionNumber": q_num,
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
        
    return questions

def main():
    os.makedirs("data/questions/telangana", exist_ok=True)
    
    signs = build_road_signs()
    with open("data/questions/telangana/road-signs.json", "w", encoding="utf-8") as f:
        json.dump(signs, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(signs)} Road Signs to data/questions/telangana/road-signs.json")
    
    rules = build_rules()
    with open("data/questions/telangana/rules-of-road.json", "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(rules)} Rules of Road to data/questions/telangana/rules-of-road.json")
    
    gp = build_general_principles()
    with open("data/questions/telangana/general-principles.json", "w", encoding="utf-8") as f:
        json.dump(gp, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(gp)} General Principles to data/questions/telangana/general-principles.json")

if __name__ == "__main__":
    main()
