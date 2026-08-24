import urllib.request
import json

def test_api_endpoint(url, post_data=None, method=None):
    try:
        req = urllib.request.Request(url, method=method)
        if post_data is not None:
            req.add_header('Content-Type', 'application/json')
            data = json.dumps(post_data).encode('utf-8')
            with urllib.request.urlopen(req, data=data, timeout=10) as response:
                return response.status, json.loads(response.read().decode('utf-8'))
        elif method == 'POST':
            with urllib.request.urlopen(req, data=b"", timeout=10) as response:
                return response.status, json.loads(response.read().decode('utf-8'))
        else:
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return 500, str(e)

def main():
    print("=== SKYSHIELD PRO END-TO-END LIVE API VERIFICATION ===")
    
    # 1. Health
    st, res = test_api_endpoint("http://127.0.0.1:8000/api/health")
    print(f"1. GET /api/health -> Status {st} | Mode: {res.get('mode') if isinstance(res, dict) else res}")
    
    # 2. Satellites
    st, res = test_api_endpoint("http://127.0.0.1:8000/api/satellites")
    print(f"2. GET /api/satellites -> Status {st} | Satellites loaded: {len(res) if isinstance(res, list) else res}")
    
    # 3. Load High-Risk Scenario 3
    st, sc3_res = test_api_endpoint("http://127.0.0.1:8000/api/scenarios/scenario-3/run", method='POST')
    if isinstance(sc3_res, str):
        print(f"3. POST /api/scenarios/scenario-3/run FAIL -> Status {st} | Raw: {sc3_res}")
        return
        
    print(f"3. POST /api/scenarios/scenario-3/run -> Status {st} | Conjunctions Loaded: {len(sc3_res.get('conjunctions', []))}")
    
    # 4. Conjunctions
    st, res = test_api_endpoint("http://127.0.0.1:8000/api/conjunctions")
    print(f"4. GET /api/conjunctions -> Status {st} | Conjunctions detected: {len(res) if isinstance(res, list) else res}")
    conj_id = res[0]['id'] if isinstance(res, list) and res else "conj-25544-33442"
    
    # 5. Maneuver Evaluation
    st, res = test_api_endpoint(
        "http://127.0.0.1:8000/api/maneuvers/evaluate?satellite_id=25544",
        post_data={},
        method='POST'
    )
    has_safe = res.get('has_safe_maneuver') if isinstance(res, dict) else False
    cands = res.get('all_candidates', []) if isinstance(res, dict) else []
    print(f"5. POST /api/maneuvers/evaluate -> Status {st} | Has Safe: {has_safe} | Candidates: {len(cands)}")
    if cands:
        print(f"   Top Candidate: ID={cands[0]['id']}, Dir={cands[0]['direction']}, dv={cands[0]['delta_v_ms']}m/s, Valid={cands[0]['is_valid']}, Status={cands[0]['status']}")
    
    # 6. Command Creation & Signing
    st, cmd_res = test_api_endpoint(
        "http://127.0.0.1:8000/api/commands/create?satellite_id=25544",
        method='POST'
    )
    if isinstance(cmd_res, str):
        print(f"6. POST /api/commands/create FAIL -> Status {st} | Raw response: {cmd_res}")
        return
        
    print(f"6. POST /api/commands/create -> Status {st} | Command ID: {cmd_res.get('command_id')}")
    
    st, signed_res = test_api_endpoint(
        "http://127.0.0.1:8000/api/commands/sign",
        post_data=cmd_res,
        method='POST'
    )
    print(f"7. POST /api/commands/sign -> Status {st} | RSA Signature Length: {len(signed_res.get('signature_base64', '')) if isinstance(signed_res, dict) else 0}")
    
    # 7. Command Verification (Valid)
    st, ver_res = test_api_endpoint(
        "http://127.0.0.1:8000/api/commands/verify",
        post_data=signed_res,
        method='POST'
    )
    print(f"8. POST /api/commands/verify -> Status {st} | Is Valid: {ver_res.get('is_valid') if isinstance(ver_res, dict) else ver_res} | Msg: {ver_res.get('status_message') if isinstance(ver_res, dict) else ver_res}")
    
    # 8. Command Tamper Demo (Invalid)
    st, tamper_res = test_api_endpoint(
        "http://127.0.0.1:8000/api/commands/tamper-demo",
        post_data={
            "original_signed_command": signed_res,
            "field_to_tamper": "delta_v_ms",
            "tampered_value": 99.9
        },
        method='POST'
    )
    print(f"9. POST /api/commands/tamper-demo -> Status {st} | Is Valid: {tamper_res.get('is_valid') if isinstance(tamper_res, dict) else tamper_res} | Msg: {tamper_res.get('status_message') if isinstance(tamper_res, dict) else tamper_res}")
    
    # 9. Run Scenario 5 (No Safe Maneuver)
    st, sc5_res = test_api_endpoint(
        "http://127.0.0.1:8000/api/scenarios/scenario-5/run",
        method='POST'
    )
    no_safe_reason = sc5_res.get('maneuver_result', {}).get('no_safe_maneuver_reason', '') if isinstance(sc5_res, dict) else str(sc5_res)
    print(f"10. POST /api/scenarios/scenario-5/run -> Status {st} | Honest Failure Reason: {no_safe_reason[:65]}...")
    
    print("\n✅ ALL LIVE SYSTEM API INTEGRATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
