"""
Script para convertir company_data.json en archivos TXT planos, uno por cada url.
Cada archivo contendrá los datos relevantes de la compañía en formato legible.
"""

import json
import os
import re


def company_to_text(company):
    def remove_html(text):
        if not isinstance(text, str):
            return text
        return re.sub(r"<[^>]+>", "", text)

    lines = []
    for k, v in company.items():
        clean_v = remove_html(v)
        lines.append(f"{k.capitalize()}: {clean_v}")
    return "\n".join(lines)


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    raw_dir = os.path.join(base_dir, "data", "raw")
    processed_dir = os.path.join(base_dir, "data", "processed", "company")
    os.makedirs(processed_dir, exist_ok=True)
    input_json = os.path.join(raw_dir, "company_data.json")

    with open(input_json, "r", encoding="utf-8") as f:
        companies = json.load(f)

    output_txt = os.path.join(processed_dir, "company_context.txt")
    with open(output_txt, "w", encoding="utf-8") as out:
        for company in companies:
            out.write(company_to_text(company))
            out.write("\n\n" + "="*80 + "\n\n")
    print("Archivo único de contexto de compañía generado correctamente.")


if __name__ == "__main__":
    main()
