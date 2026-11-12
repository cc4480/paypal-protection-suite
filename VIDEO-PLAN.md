# Demo video plan — app in motion (Carlos's direction, 2026-11-11 ~14:02 CST)

**Direction (locked by Carlos):** modeled on the Vultr hackathon winners'
video from his email — no talking head, no slide deck. The video is
**the app itself, moving**: a real walkthrough of the suite being used,
feature by feature, with Framer-Motion-style movement — smooth push-ins,
pans across panels, and zooms that land on the exact control or verdict
that matters at that second. Captions in the house palette carry the
narration. Runtime ≤ 2:55 (Devpost limit: under 3:00, public).

## BUILD STATUS — Framer composition BUILT and served (2026-11-11 ~14:38 CST)

The Framer Motion composition exists and is live. Project:
`~/workspace/paypal-video/` (React + framer-motion + Vite
single-file build, 2,093,360 B, zero runtime dependencies). All
seven scenes from `VIDEO-SCRIPT.md` are choreographed — hero,
glide, WITNESS (typing + extraction + stamp + verdict + decline),
SEATBELT (flagged chat + quoted pressure + invoice), AUDITOR
(X-ray sweep + computed cards), receipts, close — with the VO
lines as on-screen captions and scene timing matched to the
script (2:48 total). It is served by the app at **`/video`**
(`app/static/video.html`); tests 46/46 on both copies; stills
verified firsthand by Cho-zen1 (in `video-stills/`). Open it in
any browser: it autoplays; space pauses, arrows step scenes,
H hides the controls, C toggles captions; `?scene=N` jumps
straight to a scene. Honest note: the agent panels are faithful
recreations of the app's real screens and copy; when the seeded
LIVE run is captured (needs Carlos's sandbox keys), those
captures can replace the recreations before the final render.

**FINAL RENDER DONE (2026-11-11 ~15:00 CST):** per Carlos's
direction, an 8th scene was added — a 6-second logo end-card
(PayPal chip + suite name + "Three agents. One side: yours."
over the dimmed backdrop, fading to black) — bringing the
runtime to **2:54**, and the full voiceover was generated from
`VIDEO-SCRIPT.md` (one clip per scene, timed to the scene
starts) and mixed under a full-length recording of the
composition. The finished file is **`paypal-demo-final.mp4`**
(1920×1080, H.264 + AAC, 174.5 s, 17.6 MB) in this folder,
frame-verified firsthand at the hero and the end-card. The
`/video` page on both copies serves the matching 8-scene
composition. If Carlos records his own narration instead, the
per-scene clips in `~/workspace/paypal-video/vo/` mark the
exact in/out points for a re-mix.

**RETIMED CUT (2026-11-11 ~15:12 CST, supersedes the runtime
above):** Carlos's pacing call — scene animations outlasted the
narration by 5–10 s of dead air. All eight scene durations and
internal delays were compressed so each scene's last beat lands
with its narration: total **96 s (1:36)**. The VO track was
re-padded to the new scene starts and the final MP4 re-rendered
(96.5 s, 12.0 MB), frame-verified at the WITNESS verdict and the
AUDITOR cards. The retimed composition is what `/video` serves
on both copies now.

## Production method

**Script first: `VIDEO-SCRIPT.md`** (drafted 2026-11-11 ~14:23 CST —
7 scenes, ~356 words ≈ 2:22 of VO; scene timings are the contract).

**Build: completely on Framer Motion (Carlos, 2026-11-11 ~14:23 CST).**
The real app stays on screen, but every push-in, pan, and zoom is
authored in Framer Motion and timed to the script — controllable beat
by beat, instead of hand-easing a raw recording after the fact.

1. Record AFTER the keys are seated, the spike (S1–S4) has run, and the
   demo account is seeded — so every receipt on camera is stamped
   LIVE SANDBOX, not SIMULATED.
2. Capture the real app at full screen on Cho-zen (127.0.0.1:5000),
   one clean take per beat below; the mouse does the actual clicks.
3. Framer Motion pass on the captures: ease-in push-ins on verdicts and
   receipts, pans that follow the eye from input → button → result,
   brief hold + caption card at each feature. Nothing on screen that
   isn't the real app.
4. Safety (SCOPE §6.7): never show the `.env`, keys, or a real PayPal
   login. Demo sandbox account only.

## Shot list (follows SCOPE §5 timings, opens on the new landing page)

| Time | Motion | Beat |
|---|---|---|
| 0:00–0:15 | Slow push-in on the hero; carousel glides Witness → Seatbelt → Auditor; click **Open the suite** | Hook caption: "Every AI agent in this hackathon works for the seller. These three work for you." |
| 0:15–1:05 | Pan to the invoice box; paste the "Norton renewal — $499.99" text; zoom to the extraction card, then the giant verdict; push-in on the LIVE SANDBOX receipt; click Decline, status flips on re-read | WITNESS: "No money has left your account." |
| 1:05–1:55 | Slide to SEATBELT; paste the Marketplace chat; zoom across each quoted pressure line as it flags; the F&F warning fills the frame; click Generate — the protected Goods & Services invoice is created and sent; hold on the exclusions line | SEATBELT converts the deal, honesty on camera |
| 1:55–2:40 | Slide to AUDITOR; click Run the X-ray; the four cards land one by one — forgotten subscription, duplicate charge, price crept +40%, true fee total | AUDITOR: figures computed by code, explained in plain language |
| 2:40–2:55 | Pull back to the landing hero; receipts page flashes once; repo URL + partner-approval sentence as the closing caption | Close: three agents, one app, buyer-side |

## Still gated on

Keys in `.env` (Carlos's step) → spike + seed (Cho-zen1, same day) →
record → motion pass → Carlos approves the cut and confirms PUBLIC →
submit before Thu Nov 12, 14:00 CST (building stops 10:00).
