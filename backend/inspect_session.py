import httpx, json

r = httpx.get('http://127.0.0.1:8000/api/v1/sessions', follow_redirects=True)
sessions = r.json()
# Find the bus video session
s = [x for x in sessions if x['id'].startswith('e36c2a09')][0]
print("Transcript:", repr(s.get('transcript','')[:200]))
print("\nSummary:", s.get('summary','')[:300])
print("\nKeyframes:")
va = s.get('video_analysis', {})
kfs = va.get('keyframes', [])
for kf in kfs:
    ts = kf.get('timestamp', '')
    url = kf.get('url', '')[:80]
    label = kf.get('label', '')[:60]
    path = kf.get('path', '')[:80]
    quote = kf.get('subtitle_quote', '')[:60]
    print(f"  - ts={ts}, url={url}, label={label}")
    if path:
        print(f"    path={path}")
    if quote:
        print(f"    quote={quote}")

print("\nTopics:", json.dumps(s.get('topics', [])[:3], indent=2))
print("\nTimeline:", json.dumps(s.get('timeline', [])[:3], indent=2))
print("\nAction items:", json.dumps(s.get('action_items', [])[:3], indent=2))
print("\nDecisions:", json.dumps(s.get('decisions', [])[:3], indent=2))
