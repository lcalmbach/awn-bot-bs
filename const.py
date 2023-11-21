ADR_FILE = "data/entries.parquet"
APARTMENT_FILE = "data/apartments.parquet"
STREETS_FILE = "data/streets.parquet"
LLM_RETRIES = 3
SLEEP_TIME_AFTER_ERROR = 30
SYSTEM_PROMPT = """Du bist ein freundlicher Assistent und hilfst dem User, seine Wohnungsnummer zu finden. Dazu benötigst du zuerst die Adresse. Eine Adresse besteht aus Strasse, Hausnummer, Postleitzahl und Ort. Extrahiere die Element die du findest. Die Angaben müssen mindestens den Strassennamen beinhalten."""
user_questions = {
    "street": "Gib deine Adresse ein z.B. Hauptstrasse 34, 4058, Basel:",
}
assistant_questions = {
    "street": """Extrahiere Strasse, Hausnummer, Postleitzahl und Ort aus folgender Adresse: ***{}***. Gib das Resultat als JSON in folgendem Format zurück: {{"street": "Hauptstrasse", "housenumber": "34", "plz": "4058", "location": "Basel"}}*** Lass die Element die du nicht findest leer, z.B. {{"street": "Hauptstrasse", "housenumber": "", "plz": "", "location": ""}} wenn nur der Strassenname gefunden wurde.
    """
}
