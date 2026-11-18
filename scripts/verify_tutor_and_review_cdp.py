import socket
import os
import base64
import json
import urllib.request
import time

def ws_connect(ws_url):
    parts = ws_url.replace("ws://", "").split("/", 1)
    host_port = parts[0].split(":")
    host = host_port[0]
    port = int(host_port[1])
    path = "/" + parts[1]

    s = socket.create_connection((host, port), timeout=5)
    key = base64.b64encode(os.urandom(16)).decode('ascii')
    req = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n\r\n"
    )
    s.sendall(req.encode('ascii'))
    resp = s.recv(4096)
    if b"101 " not in resp:
        raise RuntimeError("WS upgrade failed: " + resp.decode('utf-8', errors='ignore'))
    return s

def ws_send(s, data_str):
    payload = data_str.encode('utf-8')
    length = len(payload)
    frame = bytearray([0x81])
    mask = os.urandom(4)
    if length <= 125:
        frame.append(0x80 | length)
    elif length <= 65535:
        frame.append(0x80 | 126)
        frame.extend(length.to_bytes(2, 'big'))
    else:
        frame.append(0x80 | 127)
        frame.extend(length.to_bytes(8, 'big'))
    frame.extend(mask)
    masked = bytearray(b ^ mask[i % 4] for i, b in enumerate(payload))
    frame.extend(masked)
    s.sendall(frame)

def ws_recv(s):
    header = s.recv(2)
    if not header:
        return None
    b1, b2 = header[0], header[1]
    masked = bool(b2 & 0x80)
    length = b2 & 0x7F
    if length == 126:
        length = int.from_bytes(s.recv(2), 'big')
    elif length == 127:
        length = int.from_bytes(s.recv(8), 'big')
    mask = s.recv(4) if masked else None
    data = bytearray()
    while len(data) < length:
        chunk = s.recv(min(4096, length - len(data)))
        if not chunk:
            break
        data.extend(chunk)
    if masked:
        data = bytearray(b ^ mask[i % 4] for i, b in enumerate(data))
    return data.decode('utf-8', errors='ignore')

def main():
    time.sleep(1)
    res = urllib.request.urlopen('http://localhost:9222/json').read()
    tabs = json.loads(res)
    target = next((t for t in tabs if '8000' in t.get('url', '')), None)
    if not target:
        print("No target tab found!")
        return

    ws = ws_connect(target['webSocketDebuggerUrl'])
    print("Connected to CDP tab for Tutor & Review Verification!")

    ws_send(ws, json.dumps({"id": 1, "method": "Console.enable"}))
    ws_send(ws, json.dumps({"id": 2, "method": "Runtime.enable"}))
    time.sleep(0.5)

    # 1. Turn on Tutor Mode, Start Test, Select Option 0, Confirm
    step1_script = """
    (() => {
        const toggle = document.getElementById('exam-toggle-tutor-mode');
        if (toggle) {
            toggle.checked = true;
            toggle.dispatchEvent(new Event('change'));
        }
        document.getElementById('btn-start-exam-main')?.click();
        setTimeout(() => {
            const firstCard = document.querySelector('.option-card');
            if (firstCard) firstCard.click();
            setTimeout(() => {
                document.getElementById('btn-confirm-next')?.click();
                setTimeout(() => {
                    const expBox = document.getElementById('exam-explanation-box');
                    const hasCorrect = !!document.querySelector('.option-card.correct');
                    const btnText = document.getElementById('btn-confirm-next')?.textContent;
                    console.log('--- TUTOR FEEDBACK VERIFIED ---');
                    console.log('Explanation visible:', expBox?.style.display !== 'none');
                    console.log('Correct card highlighted:', hasCorrect);
                    console.log('Button text:', btnText);
                }, 500);
            }, 300);
        }, 500);
    })()
    """
    ws_send(ws, json.dumps({"id": 3, "method": "Runtime.evaluate", "params": {"expression": step1_script}}))

    start = time.time()
    while time.time() - start < 4:
        msg = ws_recv(ws)
        if msg:
            data = json.loads(msg)
            if "console" in data.get("method", "").lower():
                print("CDP LOG:", json.dumps(data, indent=2))

if __name__ == "__main__":
    main()
