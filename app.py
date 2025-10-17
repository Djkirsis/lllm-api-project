import os
import json
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Ielādējam konfigurāciju
from config import (
    GEMINI_API_KEY, MODEL_NAME, TEMPERATURE,
    JD_FILE, CV_FILES, PROMPT_FILE, OUTPUT_DIR, JSON_SCHEMA
)

def read_file(file_path):
    """Nolasa faila saturu."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Kļūda: Fails nav atrasts: {file_path}")
        return None
    except Exception as e:
        print(f"Kļūda, nolasot failu {file_path}: {e}")
        return None

def generate_markdown_report(json_data, cv_filename):
    """Ģenerē īsu Markdown pārskatu no JSON datiem."""
    report = f"# CV Vērtējuma Pārskats: {os.path.basename(cv_filename)}\n\n"
    report += f"**Spriedums:** <span style='font-size: 1.2em; font-weight: bold;'>{json_data.get('verdict', 'N/A').upper()}</span>\n"
    report += f"**Atbilstības Rādītājs:** **{json_data.get('match_score', 'N/A')}/100**\n\n"
    report += "--- \n\n"
    report += "## Kopsavilkums\n"
    report += f"{json_data.get('summary', 'Nav kopsavilkuma.')}\n\n"

    report += "## Stiprās Puses (Atbilst JD)\n"
    strengths = json_data.get('strengths', [])
    if strengths:
        report += "\n".join([f"* {s}" for s in strengths]) + "\n\n"
    else:
        report += "* Nav skaidri definētu stipro pušu.\n\n"

    report += "## Trūkstošās Prasības\n"
    missing = json_data.get('missing_requirements', [])
    if missing:
        report += "\n".join([f"* {m}" for m in missing]) + "\n\n"
    else:
        report += "* Visas svarīgās JD prasības ir izpildītas (pēc AI novērtējuma).\n\n"
    
    return report

def evaluate_cv(jd_text, cv_text, prompt_template):
    """Izsauc Gemini Flash 2.5, lai novērtētu CV."""
    if not GEMINI_API_KEY:
        print("Kļūda: GEMINI_API_KEY nav iestatīta. Pārtraucam.")
        return None

    try:
        # Aizvietojam šablonus ar faktisko tekstu
        full_prompt = (
            prompt_template
            .replace("$$$${JD_TEXT}$$$$", jd_text)
            .replace("$$$${CV_TEXT}$$$$", cv_text)
        )
        
        client = genai.Client(api_key=GEMINI_API_KEY)

        # Konfigurējam modeļa izsaukumu
        config = types.GenerateContentConfig(
            temperature=TEMPERATURE,
            response_mime_type="application/json",
            response_schema=JSON_SCHEMA,
        )

        # Izsaucam modeli
        print(f"  > Izsauc modei {MODEL_NAME}...")
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt,
            config=config
        )
        print("  > Atbilde saņemta.")
        
        # Atgriežam modeļa izvadi kā Python dictionary
        return json.loads(response.text)

    except APIError as e:
        print(f"Kļūda Gemini API izsaukumā: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Kļūda dekodējot JSON atbildi: {e}. Iespējams, modelis neatgrieza derīgu JSON.")
        print(f"Neapstrādāta atbilde (fragments): {response.text[:200]}...")
        return None
    except Exception as e:
        print(f"Neparedzēta kļūda: {e}")
        return None


def main():
    """Galvenā funkcija CV vērtētāja izpildei."""
    print("--- AI CV Vērtētājs Sākas ---")

    # 1. Sagatavošanās
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Nolasiet darba aprakstu (jd.txt) un prompt.md [cite: 7, 8]
    jd_text = read_file(JD_FILE)
    prompt_template = read_file(PROMPT_FILE)

    if not all([jd_text, prompt_template]):
        print("Pārliecinieties, ka faili 'inputs_files/jd.txt' un 'prompts.md' eksistē un ir lasāmi.")
        return

    # 6. Atkārtojiet 2.-5. soli visiem trim CV [cite: 12]
    for cv_file_path in CV_FILES:
        print(f"\n* Apstrādā: {cv_file_path} *")
        
        cv_text = read_file(cv_file_path)
        if not cv_text:
            continue

        # Izgūstam bāzes nosaukumu (piem., 'cv1' no 'inputs_files/cv1.txt')
        base_name = os.path.splitext(os.path.basename(cv_file_path))[0]
        json_output_path = os.path.join(OUTPUT_DIR, f"{base_name}.json")
        report_output_path = os.path.join(OUTPUT_DIR, f"{base_name}_report.md")

        # 2.-4. Sagatavojiet promptu, izsauciet Gemini un saglabājiet JSON [cite: 8, 9, 10]
        json_result = evaluate_cv(jd_text, cv_text, prompt_template)
        
        if json_result:
            # Saglabājam JSON failu
            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(json_result, f, indent=4, ensure_ascii=False)
            print(f"  > JSON saglabāts: {json_output_path}")

            # 5. Ģenerējiet īsu pārskatu (Markdown) [cite: 11]
            markdown_report = generate_markdown_report(json_result, cv_file_path)
            with open(report_output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_report)
            print(f"  > Pārskats saglabāts: {report_output_path}")
        else:
            print(f"  > Nevarēja novērtēt {base_name}. Pārejam pie nākamā CV.")

    print("\n--- AI CV Vērtētājs Pabeigts ---")


if __name__ == "__main__":
    # Pārliecinieties, ka esat iestatījis savu GEMINI_API_KEY vides mainīgo
    # Vai arī ievadiet to tieši config.py (nav ieteicams)
    if GEMINI_API_KEY:
        main()
    else:
        print("Lūdzu, iestatiet vides mainīgo GEMINI_API_KEY un mēģiniet vēlreiz.")