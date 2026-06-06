import os

# ---------------------------------------------------------------------------
# Channel IDs
# Right-click a channel → Copy ID (Developer Mode must be on)
# ---------------------------------------------------------------------------
SOURCE_CHANNEL_ID = int(os.getenv('SOURCE_CHANNEL_ID', '0'))
DESTINATION_CHANNEL_ID = int(os.getenv('DESTINATION_CHANNEL_ID', '0'))

# ---------------------------------------------------------------------------
# Admin user IDs
# Right-click a user → Copy ID (Developer Mode must be on)
# ---------------------------------------------------------------------------
ADMIN_USER_IDS = [
    1355623077752475759,
    619779534975139850,
    1008908327989821542,
    600700144551329811,
    1343224286953078877,
    982459520385167400,
    1234938994840698920,
]

# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------
MVSEP_API_KEY = os.getenv('MVSEP_API_KEY', 'R9JjIJaLrd3QMo0olFkzRlTCFpyi41')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyCb6RHzvT5jpBl23ysaQgeV8cMQB7UJq9k')

# ---------------------------------------------------------------------------
# Song info database  (BPM / Key)
# Add new songs here: 'Song Name': 'BPM: X Key: Y'
# ---------------------------------------------------------------------------
SONG_INFO = {
    'For Once In My Life': 'BPM: 128 Key: Bb Major (tuned to 432 hz)',
    'Always': 'BPM: 105 Key: F Major',
    'Talking': 'BPM: 118 Key: E Major',
    'Hold Up, Get Up': 'BPM: 130 Key: C Minor',
    'Quiet': 'BPM: 89 Key: Ab Major',
    'Bobby Digital': 'BPM: 98 Key: C Minor',
    'All in Love': 'BPM: 120 Key: Bb Major',
    'Through The High Wire': 'BPM: 134 Key: D Major',
    'This One Here': 'BPM: 107 Key: D Major / Eb Major',
    'Church Girl': 'BPM: 137.8442511 (137.844) Key: Ab Minor',
    'Magic': 'BPM: 89 Key: Ab Major',
    'The Cross': 'idk lol but the song so beautiful we need dat leaked makes me levitate when i hear it so much potential god i wish kanye was real i love the cross',
}

# ---------------------------------------------------------------------------
# MVSEP model definitions
# Maps friendly names → MVSEP API sep_type IDs
# ---------------------------------------------------------------------------
MVSEP_MODELS = {
    # Core vocals/instrumental
    "bs_roformer":    {"id": 40, "name": "BS Roformer (vocals, instrumental)"},
    "mel_roformer":   {"id": 48, "name": "MelBand Roformer (vocals, instrumental)"},
    "mdx23c":         {"id": 25, "name": "MDX23C (vocals, instrumental)"},
    "scnet":          {"id": 46, "name": "SCNet (vocals, instrumental)"},
    "demucs4":        {"id": 20, "name": "Demucs4 HT (vocals, drums, bass, other)"},

    # Ensemble (highest quality, slower)
    "ensemble_2stem": {"id": 26, "name": "Ensemble (vocals, instrum)"},
    "ensemble_5stem": {"id": 28, "name": "Ensemble (vocals, instrum, bass, drums, other)"},
    "ensemble_allin": {"id": 30, "name": "Ensemble All-In (vocals, bass, drums, piano, guitar, lead/back vocals, other)"},

    # Karaoke
    "karaoke":        {"id": 49, "name": "MVSep Karaoke (lead/back vocals)"},

    # Individual instruments
    "piano":          {"id": 29, "name": "MVSep Piano (piano, other)"},
    "guitar":         {"id": 31, "name": "MVSep Guitar (guitar, other)"},
    "drums":          {"id": 44, "name": "MVSep Drums (drums, other)"},
    "bass":           {"id": 41, "name": "MVSep Bass (bass, other)"},
    "drumsep":        {"id": 37, "name": "DrumSep (kick, snare, cymbals, toms, ride, hh, crash)"},

    # Audio enhancement
    "reverb_removal": {"id": 22, "name": "Reverb Removal (noreverb)"},
    "crowd_removal":  {"id": 34, "name": "MVSep Crowd removal (crowd, other)"},
    "denoise":        {"id": 47, "name": "DeNoise by aufr33"},
}

# ---------------------------------------------------------------------------
# MVSEP blacklist — songs that cannot be processed
# Add song name fragments (lowercase) to block them
# ---------------------------------------------------------------------------
MVSEP_BLACKLIST = [
    'beauty and the beast',
    'preacher man',
    'this is the glory',
    'highs and lows',
    'last breath',
    'white lines',
    'i cant wait',
    'all the love',
    'mission control',
    'damn',
    'losing your mind',
    'bully',
    'serotonin',
    'cry for me',
]

# ---------------------------------------------------------------------------
# Magic 8-ball responses
# ---------------------------------------------------------------------------
EIGHTBALL_RESPONSES = [
    "yes", "yup", "mhm", "try again", "ill tell u later",
    "word it differently", "no", "nope", "idk", "mmmm prob not",
    "maybe", "mmm prob yeah", "try later im busy listening to chingy",
    "100%", "0%", "50%", "nah", "hell no",
    "do angels have wings", "do we turn into birds when we die",
    "no i dont think so",
]

# ---------------------------------------------------------------------------
# Tracker spreadsheet
# ---------------------------------------------------------------------------
TRACKER_SPREADSHEET_ID = "1IIp3t0sR_BN1SA3ph9xZ79xGu7JaGsKeO2a91nAq7P0"
TRACKER_SHEET_GID = "199908479"

# ---------------------------------------------------------------------------
# Fund command settings
# ---------------------------------------------------------------------------
FUND_LIMIT = 8000
