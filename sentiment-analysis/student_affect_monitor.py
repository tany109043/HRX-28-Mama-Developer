'''
student_affect_monitor.py
─────────────────────────
Real‑time student‑affect analysis (headless).

Outputs one JSON line per inference, e.g.:
    {"timestamp": 172721, "label": "tired"}

The JSON is consumed by api.py and then polled by the browser bookmarklet to
render in‑page notifications. No GUI pop‑ups or system sounds are produced
here – all user‑facing UX is handled in the browser.

Labels:
    • tired                (EAR‑based drowsiness)
    • sleep                (eyes fully shut for several seconds)
    • tension/frustration  (angry, fear)
    • confusion            (disgust, surprise)
    • boredom              (sad)
    • engagement/focus     (happy, neutral)

Every 30 s:
    Prints a textual summary to stderr for debugging. No alerts are raised –
    the browser decides what to do with the JSON stream.
Quit with Esc or press 'q' in the (optional) webcam window.
'''

import cv2, threading, time, statistics, sys, json
from collections import Counter
from deepface import DeepFace
import mediapipe as mp
from pynput import keyboard, mouse
from scipy.spatial import distance as dist

# ─────────── Tunables ───────────
EMOTION_SAMPLE_INTERVAL  = 1     # seconds between DeepFace inferences
EMOTION_REPORT_INTERVAL  = 30    # seconds between fusion reports
ALERT_THRESHOLD          = 5     # ≥ this → alert (logged only)
EAR_THRESH               = 0.23  # Eye‑Aspect‑Ratio limit for closed eyes
EAR_CONSEC_FRAMES        = 15    # consecutive frames below EAR → tired
SLEEP_CONSEC_FRAMES      = 90    # consecutive frames → sleep  (≈3 s @30 fps)

# ─────────── Runtime globals ────
emotion_window, typing_metrics = [], []
scroll_events, eye_closed_counter = 0, 0
key_press_times = {}

# ─────────── Face‑mesh setup ────
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False,
                                  max_num_faces=1,
                                  refine_landmarks=True,
                                  min_detection_confidence=0.5,
                                  min_tracking_confidence=0.5)

LEFT_EYE  = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# ─────────── Mapping helper ─────
RAW_TO_HIGH = {
    'angry'   : 'You Look tensed try attempting quiz',
    'fear'    : 'You Look tensed try attempting quiz',
    'disgust' : 'You Look bored  generate a meme,relax a bit',
    'surprise': 'You Look tensed try attempting quiz',
    'sad'     : 'You Look bored  generate a meme,relax a bit',
    'happy'   : 'engagement/focus',
    'neutral' : 'engagement/focus'
}
NEGATIVE_EMOTIONS = {
    'tired',
    'sleep',
    'You Look tensed try attempting quiz',
    'You Look bored  generate a meme,relax a bit'
}

def harmonise(raw_face: str, tired_flag: bool) -> str:
    """Map raw DeepFace emotion + tired flag → high‑level label."""
    return 'tired' if tired_flag else RAW_TO_HIGH.get(raw_face, 'engagement/focus')

# ─────────── EAR utility ────────

def ear(pts):
    A = dist.euclidean(pts[1], pts[5])
    B = dist.euclidean(pts[2], pts[4])
    C = dist.euclidean(pts[0], pts[3])
    return (A + B) / (2.0 * C)

# ─────────── Webcam thread ──────

def detect_emotion():
    global eye_closed_counter

    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW if sys.platform.startswith('win') else 0)
    if not cam.isOpened():
        sys.stderr.write('❌  Cannot access webcam.\n')
        return

    last_inf = 0.0
    while True:
        ok, frame = cam.read()
        if not ok:
            continue
        now = time.time()
        tired_now, sleep_now = False, False

        # EAR each frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = face_mesh.process(rgb)
        if res.multi_face_landmarks:
            lm = res.multi_face_landmarks[0].landmark
            l_eye = [(lm[i].x, lm[i].y) for i in LEFT_EYE]
            r_eye = [(lm[i].x, lm[i].y) for i in RIGHT_EYE]

            if ear(l_eye + r_eye) < EAR_THRESH:
                eye_closed_counter += 1
                if eye_closed_counter >= SLEEP_CONSEC_FRAMES:
                    sleep_now = True
            else:
                if eye_closed_counter >= EAR_CONSEC_FRAMES:
                    tired_now = True
                eye_closed_counter = 0

        # DeepFace every N seconds
        if now - last_inf >= EMOTION_SAMPLE_INTERVAL:
            try:
                out = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                raw = out[0]['dominant_emotion'] if isinstance(out, list) else out['dominant_emotion']
            except Exception:
                raw = 'neutral'

            label = 'sleep' if sleep_now else harmonise(raw, tired_now)
            emotion_window.append(label)

            # JSON output expected by api.py
            sys.stdout.write(json.dumps({
                'timestamp': int(now),
                'label'    : label
            }) + '\n')
            sys.stdout.flush()
            last_inf = now

        # Comment these two lines if you want *completely* headless operation
        # cv2.imshow('Webcam (q quits)', frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    cam.release()
    cv2.destroyAllWindows()

# ─────────── Keyboard callbacks ─

def on_press(key):
    key_press_times[str(key)] = time.time()

def on_release(key):
    rel = time.time(); prs = key_press_times.pop(str(key), None)
    if prs:
        typing_metrics.append(rel - prs)
    if key == keyboard.Key.esc:
        return False

# ─────────── Mouse callback ─────

def on_scroll(x, y, dx, dy):
    global scroll_events
    scroll_events += 1

# ─────────── 30 s fusion thread ─

def analyze_emotions():
    """Aggregate stats every EMOTION_REPORT_INTERVAL seconds."""
    global emotion_window, typing_metrics, scroll_events

    while True:
        time.sleep(EMOTION_REPORT_INTERVAL)

        counts = Counter(e for e in emotion_window if e in NEGATIVE_EMOTIONS)

        for emo, cnt in counts.items():
            if cnt >= ALERT_THRESHOLD:
                sys.stderr.write(f"[ALERT] {emo} occurred {cnt}× in the last 30 s\n")
                emotion_window = [e for e in emotion_window if e != emo]

        face_mode = (max(set(emotion_window), key=emotion_window.count)
                     if emotion_window else 'engagement/focus')

        if typing_metrics:
            avg = statistics.mean(typing_metrics)
            typing_state = ('confused/frustrated' if avg > 0.5 else
                            'confident'          if avg < 0.15 else
                            'neutral')
        else:
            typing_state = 'inactive'

        scroll_state = 'impatient/restless' if scroll_events > 10 else 'focused'
        if face_mode == 'engagement/focus' and scroll_events > 15:
            face_mode = 'boredom'

        sys.stderr.write('\n[30‑second EMOTION REPORT]\n')
        sys.stderr.write(f'Facial   : {face_mode}\n')
        sys.stderr.write(f'Typing   : {typing_state}\n')
        sys.stderr.write(f'Scrolling: {scroll_state}\n')
        sys.stderr.write('-' * 30 + '\n\n')
        sys.stderr.flush()

        typing_metrics.clear()
        scroll_events = 0

# ─────────── Main ───────────────
if __name__ == '__main__':
    cam_thread      = threading.Thread(target=detect_emotion, daemon=True)
    fuse_thread     = threading.Thread(target=analyze_emotions, daemon=True)
    kb_listener     = keyboard.Listener(on_press=on_press, on_release=on_release)
    mouse_listener  = mouse.Listener(on_scroll=on_scroll)

    cam_thread.start(); fuse_thread.start()
    kb_listener.start(); mouse_listener.start()

    kb_listener.join()
    mouse_listener.stop()
    sys.stderr.write('\nSession ended.\n')
