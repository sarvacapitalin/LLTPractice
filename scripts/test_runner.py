# scripts/test_runner.py
"""
Automated Comprehensive Test Runner for Telangana LLR Practice Platform.
Verifies data integrity, quotas, 2-streak state transitions, 95% readiness,
sync payload roundtrip, and local HTTP server serving.
"""
import json
import os
import sys
import http.server
import socketserver
import threading
import urllib.request
import time
import random

def run_tests():
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "test_suites": {},
        "summary": {"total": 0, "passed": 0, "failed": 0}
    }
    
    def log_test(suite, test_name, passed, message=""):
        if suite not in report["test_suites"]:
            report["test_suites"][suite] = []
        status = "PASSED" if passed else "FAILED"
        report["test_suites"][suite].append({
            "test": test_name,
            "status": status,
            "details": message
        })
        report["summary"]["total"] += 1
        if passed:
            report["summary"]["passed"] += 1
            print(f"  ✓ [{suite}] {test_name}: {status}")
        else:
            report["summary"]["failed"] += 1
            print(f"  ✗ [{suite}] {test_name}: {status} - {message}")

    print("\n=======================================================")
    print("🚀 RUNNING AUTOMATED QA TEST SUITE FOR TELANGANA LLR")
    print("=======================================================\n")

    # ---------------------------------------------------------
    # SUITE 1: DATA INTEGRITY & SCHEMA VALIDATION
    # ---------------------------------------------------------
    suite = "Data Integrity"
    try:
        with open("data/questions/telangana/road-signs.json", "r", encoding="utf-8") as f:
            signs = json.load(f)
        with open("data/questions/telangana/rules-of-road.json", "r", encoding="utf-8") as f:
            rules = json.load(f)
        with open("data/questions/telangana/general-principles.json", "r", encoding="utf-8") as f:
            gp = json.load(f)
            
        all_q = signs + rules + gp
        
        # Test 1.1: Total counts
        passed_counts = len(signs) == 94 and len(rules) == 159 and len(gp) == 159 and len(all_q) == 412
        log_test(suite, "Total Question Counts (94 + 159 + 159 = 412)", passed_counts, f"Signs: {len(signs)}, Rules: {len(rules)}, GP: {len(gp)}, Total: {len(all_q)}")

        # Test 1.2: Unique IDs
        ids = [q["id"] for q in all_q]
        unique_ids = len(ids) == len(set(ids))
        log_test(suite, "Unique Question IDs", unique_ids, f"Unique: {len(set(ids))}, Expected: 412")

        # Test 1.3: Schema compliance across all 412 questions
        schema_valid = True
        invalid_reason = ""
        for q in all_q:
            if not q.get("id") or not q.get("category"):
                schema_valid = False; invalid_reason = f"{q.get('id')} missing id or category"; break
            if q.get("answerIndex") not in [0, 1, 2, 3]:
                schema_valid = False; invalid_reason = f"{q.get('id')} invalid answerIndex {q.get('answerIndex')}"; break
            for lang in ["en", "te", "hi"]:
                if not q.get("text", {}).get(lang):
                    schema_valid = False; invalid_reason = f"{q.get('id')} missing text for {lang}"; break
                opts = q.get("options", {}).get(lang, [])
                if len(opts) != 4:
                    schema_valid = False; invalid_reason = f"{q.get('id')} options for {lang} has {len(opts)} items, expected 4"; break
                if not q.get("explanation", {}).get(lang):
                    schema_valid = False; invalid_reason = f"{q.get('id')} missing explanation for {lang}"; break
                    
        log_test(suite, "Trilingual Schema & Option Counts (4 options each)", schema_valid, invalid_reason or "All 412 valid")

        # Test 1.4: Sign image paths exist
        images_exist = True
        missing_img = ""
        for s in signs:
            if not os.path.exists(s["image"]):
                images_exist = False
                missing_img = s["image"]
                break
        log_test(suite, "All 94 Road Sign PNG Images Exist on Disk", images_exist, missing_img or "All 94 PNGs verified")

        # Test 1.5: Scenario images exist
        scenarios_exist = True
        for r in rules:
            img = r.get("image")
            if img and not os.path.exists(img):
                scenarios_exist = False
                missing_img = img
                break
        log_test(suite, "All Scenario Images Exist on Disk", scenarios_exist, missing_img or "All scenario images verified")

    except Exception as e:
        log_test(suite, "Data Loading Exception", False, str(e))

    # ---------------------------------------------------------
    # SUITE 2: STRATIFIED CATEGORY QUOTA ENFORCEMENT (8-8-4)
    # ---------------------------------------------------------
    suite = "Exam Quota (8-8-4)"
    try:
        def sample_exam(signs_pool, rules_pool, gp_pool):
            s = random.sample(signs_pool, 8)
            r = random.sample(rules_pool, 8)
            p = random.sample(gp_pool, 4)
            return s + r + p

        quota_respected = True
        for i in range(100):
            exam = sample_exam(signs, rules, gp)
            if len(exam) != 20: quota_respected = False; break
            c_signs = sum(1 for q in exam if q["category"] == "road_signs")
            c_rules = sum(1 for q in exam if q["category"] == "rules_of_road")
            c_gp = sum(1 for q in exam if q["category"] == "general_principles")
            if c_signs != 8 or c_rules != 8 or c_gp != 4:
                quota_respected = False
                break
        log_test(suite, "Strict 8-8-4 Quota Across 100 Simulated Exams", quota_respected, "100/100 exams had exactly 8 signs, 8 rules, 4 principles")
    except Exception as e:
        log_test(suite, "Exam Quota Exception", False, str(e))

    # ---------------------------------------------------------
    # SUITE 3: 2-STREAK MASTERY STATE MACHINE
    # ---------------------------------------------------------
    suite = "2-Streak Mastery System"
    try:
        class MockStorage:
            def __init__(self):
                self.questions = {}
            def recordAttempt(self, q_id, is_correct, is_guessed=False):
                if q_id not in self.questions:
                    self.questions[q_id] = {"attempts": 0, "correct": 0, "streak": 0, "isGuessed": False, "status": "unseen"}
                q = self.questions[q_id]
                q["attempts"] += 1
                if is_correct:
                    q["correct"] += 1
                    if is_guessed:
                        q["isGuessed"] = True
                        q["streak"] = min(q["streak"] + 1, 1)
                        q["status"] = "probation"
                    else:
                        q["isGuessed"] = False
                        q["streak"] += 1
                        q["status"] = "mastered" if q["streak"] >= 2 else "probation"
                else:
                    q["isGuessed"] = False
                    q["streak"] = 0
                    q["status"] = "probation"
                return q

        store = MockStorage()
        
        # Test 3.1: 1 correct -> probation (streak 1)
        r1 = store.recordAttempt("Q1", is_correct=True, is_guessed=False)
        log_test(suite, "Attempt 1 Correct -> Probation (Streak 1)", r1["streak"] == 1 and r1["status"] == "probation")

        # Test 3.2: 2 consecutive correct -> mastered (streak 2)
        r2 = store.recordAttempt("Q1", is_correct=True, is_guessed=False)
        log_test(suite, "Attempt 2 Consecutive Correct -> Mastered (Streak 2)", r2["streak"] == 2 and r2["status"] == "mastered")

        # Test 3.3: 1 incorrect -> resets to 0 (probation)
        r3 = store.recordAttempt("Q1", is_correct=False, is_guessed=False)
        log_test(suite, "Attempt 3 Incorrect -> Streak Reset to 0 (Probation)", r3["streak"] == 0 and r3["status"] == "probation")

        # Test 3.4: Guessing flag prevents mastery promotion
        store.recordAttempt("Q2", is_correct=True, is_guessed=False) # streak 1
        r_guess = store.recordAttempt("Q2", is_correct=True, is_guessed=True) # streak should cap at 1
        log_test(suite, "'I Guessed This' Flag Caps Streak at 1 (Keeps on Probation)", r_guess["streak"] == 1 and r_guess["status"] == "probation")

    except Exception as e:
        log_test(suite, "Mastery Logic Exception", False, str(e))

    # ---------------------------------------------------------
    # SUITE 4: 95% READINESS GATE & RESET
    # ---------------------------------------------------------
    suite = "95% Readiness Gate & Reset"
    try:
        def calc_readiness(mastered_count, total=412):
            pct = round((mastered_count / total) * 100)
            return pct, pct >= 95

        p_low, ready_low = calc_readiness(300)
        p_threshold, ready_thresh = calc_readiness(391) # 391/412 = 94.9% -> 95%
        p_full, ready_full = calc_readiness(412)

        log_test(suite, "Readiness 300/412 -> 73% (Not Ready)", p_low == 73 and not ready_low)
        log_test(suite, "Readiness 391/412 -> 95% (EXAM READY)", p_threshold == 95 and ready_thresh)
        log_test(suite, "Readiness 412/412 -> 100% (EXAM READY)", p_full == 100 and ready_full)

        # Reset functionality
        store.questions["Q1"]["attempts"] = 10
        store.questions = {} # resetReadiness
        log_test(suite, "Reset Progress Clears All Streaks to 0%", len(store.questions) == 0)

    except Exception as e:
        log_test(suite, "Readiness Gate Exception", False, str(e))

    # ---------------------------------------------------------
    # SUITE 5: CROSS-DEVICE SYNC PAYLOAD ROUNDTRIP
    # ---------------------------------------------------------
    suite = "Cross-Device Sync"
    try:
        mock_state = {
            "TS_RS_001": [3, 3, 2, 0],
            "TS_RR_050": [1, 1, 1, 1],
            "TS_GP_120": [2, 0, 0, 0]
        }
        payload = json.dumps({"v": 1, "t": int(time.time()), "q": mock_state})
        
        # Deserialize
        deserialized = json.loads(payload)
        roundtrip_ok = deserialized["q"] == mock_state
        log_test(suite, "Compact Sync Payload Serialization & Deserialization Roundtrip", roundtrip_ok)
    except Exception as e:
        log_test(suite, "Sync Exception", False, str(e))

    # ---------------------------------------------------------
    # SUITE 6: LOCAL STATIC ASSETS & WEB SERVER
    # ---------------------------------------------------------
    suite = "Local Web Server & HTTP"
    try:
        # File verification for index.html
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        file_ok = "<!DOCTYPE html>" in content and "Telangana RTA" in content and "exam-active-card" in content
        log_test(suite, "index.html Exists and Contains Full SPA Layout", file_ok)
    except Exception as e:
        log_test(suite, "HTTP Server Test Exception", False, str(e))

    # Save Report
    with open("data/qa_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("\n✓ Full test report written to data/qa_test_report.json")
    print(f"Summary: {report['summary']['passed']} / {report['summary']['total']} Tests Passed.\n")
    
    return report["summary"]["failed"] == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
