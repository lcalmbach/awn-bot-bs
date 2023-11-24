ADR_FILE = "data/entries.parquet"
APARTMENT_FILE = "data/apartments.parquet"
STREETS_FILE = "data/streets.parquet"
LLM_RETRIES = 3
SLEEP_TIME_AFTER_ERROR = 30
SYSTEM_PROMPT = """Du bist ein freundlicher Assistent und hilfst dem User, seine Wohnungsnummer zu finden. Du sprichst den User konsequent mit Du an. Du benötigst vom User als erstes die Adresse. Eine Adresse besteht aus Strasse, Hausnummer, Postleitzahl und Ort. Extrahiere die Element die du findest. Die Angaben müssen mindestens den Strassennamen beinhalten. Wenn der User Prompt keinen Bezug zur Adresse hat, versuche seine Frage freundliche zu beantworten wenn du das kannst und frage ihn nochmals nach der Adresse mit dem Hinweis, dass es deine Aufgabe ist seine Adminstrative Wohnungsnummer zu finden. Gib das Resultat als JSON in folgendem Format zurück:\n{{"street": "Hauptstrasse", "housenumber": "34", "plz": "4058", "location": "Basel"}}*** Lass die Element die du nicht findest leer, z.B. input: "ich wohne an der Hauptstrasse", output: {{"street": "Hauptstrasse", "housenumber": "", "plz": "", "location": "", "floor": ""}}. wenn der User mehrmals nicht seine Adresse angibt werde ungeduldig und gib ihm einen Hinweis, dass du seine Adresse brauchst.
"""

user_questions = {
    "street": """Extrahiere Strasse, Hausnummer, Postleitzahl und Ort aus folgender Adresse: ***{}***. Antworte nur mit dem json Objekt wenn mindest ein Adresselemnt gefunden wurde. Wenn es keine Adressangaben gibt, gib einen Hinweis, dass du die Adresee brauchst.""",
    "housenumber": """Hausnummer, Postleitzahl und Ort aus folgender Adresse: ***{}***.""",
    "floor": """Extrahiere das Stockwerk aus folgendem Text: ***{}***. Gib das Resultat als json zurück. Beispiel: input: 1, output: {{"floor": 1"}}."""
}

assistant_responses = {
    "street": {"content": "Damit ich deine Wohnungsnummer bestimmen kann, brauche ich zunächst deine Adresse: z.B. Hauptstrasse 34, 4058, Basel:", "includes": []},
    "housenumber": {"content": "Prima, du wohnst an der {}. Nun brauche ich aber noch eine Hausnummer.", "includes": []},
    "plz": {"content": "Tut mir leide, die Postleitzahl oder der Ort brauche ich ebenfalls.", "includes": []},
    "location": {"content": "Tut mir leid, den Ort oder die Postleitzahl brauche ich ebenfalls.", "includes": []},
    "floor": {"content": "Prima, wir haben es fast geschafft. Wenn das richtig ist, gib mir bitte noch das Stockwerk an. Ich finde an der Adresse *{}* folgende Stockewerke: {}. Wenn das nicht deine Adresse ist, so drücke einfach die *Start nochmals neu* Schaltfläche.", "includes": ["adrs", 'floors']}
}
