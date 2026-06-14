#!/usr/bin/env python3
"""Generate the grandfather narration with ElevenLabs.
Key: pass --key, set XI_API_KEY, or put it in video/.elevenlabs_key (one line).
Voice: pass --voice <id>; default auto-picks a mature/old male voice from your account.
Output: video/vo.mp3
  py tts.py                 # auto voice
  py tts.py --list          # just list available voices
  py tts.py --voice <id>
"""
import argparse, os, sys, json, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
def get_key(cli):
    if cli: return cli.strip()
    if os.environ.get("XI_API_KEY"): return os.environ["XI_API_KEY"].strip()
    kf = os.path.join(HERE, ".elevenlabs_key")
    if os.path.exists(kf):
        return open(kf).read().strip()
    sys.exit("No ElevenLabs API key. Use --key, XI_API_KEY, or video/.elevenlabs_key")

def api(method, url, key, data=None):
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("xi-api-key", key)
    if data is not None: req.add_header("Content-Type", "application/json")
    try:
        return urllib.request.urlopen(req, timeout=120)
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs error {e.code}: {e.read().decode()[:300]}")

def list_voices(key):
    r = api("GET", "https://api.elevenlabs.io/v1/voices", key)
    return json.load(r).get("voices", [])

def pick_voice(voices):
    # prefer an old/elderly male, then mature/middle-aged male, else first male, else first
    def labels(v): return {k: (v.get("labels") or {}).get(k, "").lower() for k in ("gender","age","description")}
    for want in ("old", "elderly"):
        for v in voices:
            l = labels(v)
            if l["gender"] == "male" and want in (l["age"] + l["description"]): return v
    for v in voices:
        l = labels(v)
        if l["gender"] == "male" and ("middle" in l["age"] or "mature" in l["description"]): return v
    for v in voices:
        if labels(v)["gender"] == "male": return v
    return voices[0] if voices else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key"); ap.add_argument("--voice"); ap.add_argument("--list", action="store_true")
    ap.add_argument("--text", default=os.path.join(HERE, "narration.txt"))
    ap.add_argument("--out", default=os.path.join(HERE, "vo.mp3"))
    ap.add_argument("--model", default="eleven_multilingual_v2")
    a = ap.parse_args()
    key = get_key(a.key)
    voices = list_voices(key)
    if a.list:
        for v in voices:
            print(f"{v['voice_id']}  {v['name']:22s} {v.get('labels',{})}")
        return
    vid = a.voice
    if not vid:
        v = pick_voice(voices)
        if not v: sys.exit("No voices on this account; pass --voice <id>")
        vid = v["voice_id"]; print(f"auto voice: {v['name']} ({vid}) {v.get('labels',{})}")
    text = open(a.text, encoding="utf-8").read().strip()
    body = json.dumps({
        "text": text, "model_id": a.model,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True}
    }).encode()
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128"
    r = api("POST", url, key, body)
    with open(a.out, "wb") as f: f.write(r.read())
    print("wrote", a.out, os.path.getsize(a.out), "bytes")

if __name__ == "__main__":
    main()
