#!/usr/bin/env python3
import json
import argparse
import sys
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


# ---------- utilidades de leitura ----------
def load_urls(file_path):
    """Lê URLs de um arquivo ou stdin (se ‘-’)."""
    src = sys.stdin if file_path == "-" else open(file_path, "r", encoding="utf-8")
    with src as f:
        return [ln.strip() for ln in f if ln.strip()]


def load_patterns(json_path):
    """Lê o JSON de patterns, removendo ‘=’ e espaços extras."""
    with open(json_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return [p.strip(" =") for p in cfg.get("patterns", [])]


# ---------- matching ----------
def match_key(key, patterns, case_insensitive):
    """Retorna True se key casa com qualquer pattern (==, prefixo, sufixo)."""
    for pattern in patterns:
        k = key.lower() if case_insensitive else key
        p = pattern.lower() if case_insensitive else pattern
        if k == p or k.startswith(p) or k.endswith(p):
            return True
    return False


# ---------- substituição ----------
def replace_query_params(url, patterns, case_insensitive, new_value):
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)

    # 1) Algum nome de parâmetro corresponde aos patterns?
    param_match = any(
        match_key(k, patterns, case_insensitive) for k in query.keys()
    )
    # 2) Algum valor começa com http/https?
    url_value_match = any(
        any(v.startswith(("http://", "https://")) for v in vals)
        for vals in query.values()
    )

    # Se nada atender, descarta a URL
    if not (param_match or url_value_match):
        return None

    # Constrói novo dicionário de query
    new_query_dict: dict[str, list[str]] = {}
    for key, values in query.items():
        if match_key(key, patterns, case_insensitive):
            # Nome bate → troca todos os valores
            new_query_dict[key] = [new_value] * len(values)
        else:
            # Nome não bate → troca somente valores http/https
            new_query_dict[key] = [
                new_value if v.startswith(("http://", "https://")) else v
                for v in values
            ]

    new_query = urlencode(new_query_dict, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser(
        description="query-string replacement driven by gf-patterns"
    )
    parser.add_argument(
        "-u", "--urls",
        nargs="?",
        default="-",
        help="file with urls, or - to stdin (default: '-')",
    )
    parser.add_argument(
        "-j", "--json",
        required=True,
        help="path to json pattern file",
    )
    parser.add_argument(
        "-v", "--value",
        default="REPLACED",
        help="value to inject (default: 'REPLACED')",
    )
    parser.add_argument(
        "-o", "--output",
        help="(optional)File to save modified urls"
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="use case sentivie in patterns",
    )
    args = parser.parse_args()

    urls = load_urls(args.urls)
    patterns = load_patterns(args.json)
    case_insensitive = not args.case_sensitive

    transformed: list[str] = []
    for url in urls:
        new_url = replace_query_params(url, patterns, case_insensitive, args.value)
        if new_url:
            transformed.append(new_url)

    # saída
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(transformed) + ("\n" if transformed else ""))
    else:
        print("\n".join(transformed))


if __name__ == "__main__":
    main()
