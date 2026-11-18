import json
import os

def validate():
    print("=== Validating Telangana LLR Practice Workspace ===")
    
    # 1. Validate JSON Files
    json_files = [
        "data/questions/telangana/road-signs.json",
        "data/questions/telangana/rules-of-road.json",
        "data/questions/telangana/general-principles.json",
        "data/i18n/en.json",
        "data/i18n/te.json",
        "data/i18n/hi.json",
        "data/states.json",
        "data/rto-guide.json",
        "data/tricky-twins.json",
        "data/last-minute-cheatsheet.json",
        "manifest.json"
    ]
    
    for jf in json_files:
        assert os.path.exists(jf), f"Missing JSON file: {jf}"
        with open(jf, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"✓ {jf}: Valid JSON (type: {type(data).__name__})")
        
    # 2. Check Question Counts
    with open("data/questions/telangana/road-signs.json") as f:
        signs = json.load(f)
    assert len(signs) == 94, f"Expected 94 signs, got {len(signs)}"
    print(f"✓ Road Signs: Exactly {len(signs)} / 94 questions")
    
    with open("data/questions/telangana/rules-of-road.json") as f:
        rules = json.load(f)
    assert len(rules) == 159, f"Expected 159 rules, got {len(rules)}"
    print(f"✓ Rules of the Road: Exactly {len(rules)} / 159 questions")
    
    with open("data/questions/telangana/general-principles.json") as f:
        gp = json.load(f)
    assert len(gp) == 159, f"Expected 159 general principles, got {len(gp)}"
    print(f"✓ General Principles: Exactly {len(gp)} / 159 questions")
    
    total = len(signs) + len(rules) + len(gp)
    assert total == 412, f"Expected 412 total questions, got {total}"
    print(f"✓ Total Questions Bank: {total} / 412 (100% complete)")
    
    # 3. Check Image References
    for s in signs:
        assert os.path.exists(s["image"]), f"Sign image missing: {s['image']}"
    print(f"✓ All 94 Road Sign images exist on disk (sign_001.png..sign_094.png)")
    
    # Check scenario images
    scenario_found = 0
    for r in rules:
        if r.get("image"):
            assert os.path.exists(r["image"]), f"Scenario image missing: {r['image']}"
            scenario_found += 1
    print(f"✓ All {scenario_found} scenario images exist and are mapped")
    
    # 4. Check Frontend Files
    frontend_files = [
        "index.html",
        "manifest.json",
        "sw.js",
        "css/styles.css",
        "css/exam-stall.css",
        "js/app.js",
        "js/i18n.js",
        "js/storage-engine.js",
        "js/coverage-engine.js",
        "js/exam-engine.js",
        "js/practice-engine.js",
        "js/flashcards-engine.js",
        "js/tricky-twins-engine.js",
        "js/cheatsheet-engine.js",
        "js/sync-engine.js",
        "js/qrcode-generator.js",
        "js/speech-engine.js",
        "js/sound-effects.js",
        "README.md"
    ]
    for ff in frontend_files:
        assert os.path.exists(ff), f"Missing frontend file: {ff}"
        size = os.path.getsize(ff)
        assert size > 0, f"File {ff} is empty!"
        print(f"✓ {ff} ({size} bytes)")
        
    print("\n🎉 ALL WORKSPACE ASSETS & DATASETS VALIDATED SUCCESSFULLY!")

if __name__ == "__main__":
    validate()
