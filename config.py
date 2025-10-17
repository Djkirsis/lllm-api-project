import os

# Google Gemini API atslēga
# Ieteicams ielādēt no vides mainīgā, lai nodrošinātu drošību
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Modeļa iestatījumi
MODEL_NAME = "gemini-2.5-flash"
TEMPERATURE = 0.3

# Failu ceļi un nosaukumi
INPUT_DIR = "inputs_files"
OUTPUT_DIR = "output_files"
JD_FILE = os.path.join(INPUT_DIR, "jd.txt")
PROMPT_FILE = "prompts.md"
CV_FILES = [
    os.path.join(INPUT_DIR, "cv1.txt"),
    os.path.join(INPUT_DIR, "cv2.txt"),
    os.path.join(INPUT_DIR, "cv3.txt"),
]

# JSON atbildes formāts (HR fokuss)
JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "match_score": {"type": "integer", "description": "Atbilstības rādītājs no 0 līdz 100."},
        "summary": {"type": "string", "description": "Īss apraksts, cik labi CV atbilst JD."},
        "strengths": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Galvenās prasmes/pieredze no CV, kas atbilst JD",
        },
        "missing_requirements": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Svarīgas JD prasības, kas CV nav redzamas",
        },
        "verdict": {
            "type": "string",
            "enum": ["strong match", "possible match", "not a match"],
            "description": "Kopējais spriedums par atbilstību.",
        },
    },
    "required": ["match_score", "summary", "strengths", "missing_requirements", "verdict"],
}