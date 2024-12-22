import requests
from bs4 import BeautifulSoup
import json
import os


class DictionaryManager:
    def __init__(self, filename="dictionary.json"):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def get_means_rae(self, word):
        """Extrae las definiciones de una palabra desde el DLE (Diccionario de la Lengua Española)."""
        url = f"https://dle.rae.es/{word}?m=form"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            definitions = []
            for li in soup.find_all("li", class_="j"):
                definition_div = li.find("div", class_="c-definitions__item")
                if definition_div:
                    definition = definition_div.get_text(" ", strip=True)
                    definitions.append(self._clean_text(definition))

            if not definitions:
                return []
            return definitions
        except requests.exceptions.RequestException as e:
            print(f"Error al realizar la solicitud HTTP: {e}")
            return []
        except Exception as e:
            print(f"Error al procesar el HTML: {e}")
            return []

    def _clean_text(self, text):
        """Limpia el texto eliminando caracteres especiales y asegurando espacios correctos."""
        return (
            text.replace("\n", " ")
            .replace("\t", " ")
            .replace("\u00a0", " ")
            .replace("  ", " ")
        )

    def read_dictionary(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def write_word(self, word, definitions):
        data = self.read_dictionary()
        if word in data:
            print("La palabra ya existe.")
            return
        data[word] = {"means": definitions}
        self._write_to_file(data)
        print("Palabra añadida exitosamente.")

    def fetch_and_save_word(self, word):
        definitions = self.get_means_rae(word)
        if definitions:
            self.write_word(word, definitions)

    def fetch_and_save_words_from_file(self, filepath, start_word=None):
        if not os.path.exists(filepath):
            print(f"El archivo '{filepath}' no existe.")
            return

        with open(filepath, "r", encoding="utf-8") as file:
            words = file.read().splitlines()

        start_index = 0
        if start_word:
            try:
                start_index = words.index(start_word)
            except ValueError:
                print(f"La palabra '{start_word}' no se encontró en el archivo.")
                return

        for word in words[start_index:]:
            print(f"Procesando palabra: {word}")
            self.fetch_and_save_word(word)

    def _write_to_file(self, data):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


# Uso del programa
if __name__ == "__main__":
    manager = DictionaryManager()
    word_file = "diccionario_espanol.txt"

    # Especifica desde qué palabra comenzar (opcional)
    start_word = "acataba"  # Cambiar a la palabra deseada o dejar como None
    manager.fetch_and_save_words_from_file(word_file, start_word=start_word)
