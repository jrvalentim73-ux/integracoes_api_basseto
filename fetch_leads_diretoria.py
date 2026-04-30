"""
Puxa leads do CRM agrupados por diretoria para o mês corrente.
Uso: python fetch_leads_diretoria.py [--mes YYYY-MM]
"""

import sys
import argparse
from datetime import date, datetime
from collections import defaultdict

import requests
from config import CRM_API_KEY

BASE_URL = "https://crmbassetobackend.up.railway.app"

CANDIDATE_ENDPOINTS = [
    "/leads",
    "/api/leads",
    "/api/v1/leads",
    "/webhooks/leads",
]

HEADERS = {
    "X-API-Key": CRM_API_KEY,
    "Content-Type": "application/json",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Leads por diretoria — mês corrente")
    parser.add_argument(
        "--mes",
        default=None,
        metavar="YYYY-MM",
        help="Mês desejado (padrão: mês atual)",
    )
    return parser.parse_args()


def mes_range(mes_str: str | None):
    if mes_str:
        ref = datetime.strptime(mes_str, "%Y-%m").date()
    else:
        ref = date.today().replace(day=1)
    inicio = ref.replace(day=1)
    # último dia do mês
    if inicio.month == 12:
        fim = inicio.replace(year=inicio.year + 1, month=1, day=1)
    else:
        fim = inicio.replace(month=inicio.month + 1, day=1)
    from datetime import timedelta
    fim = fim - timedelta(days=1)
    return inicio, fim


def fetch_leads(inicio: date, fim: date) -> list[dict]:
    params = {
        "startDate": inicio.isoformat(),
        "endDate": fim.isoformat(),
        "start_date": inicio.isoformat(),
        "end_date": fim.isoformat(),
        "dateFrom": inicio.isoformat(),
        "dateTo": fim.isoformat(),
        "per_page": 10000,
        "limit": 10000,
    }

    for endpoint in CANDIDATE_ENDPOINTS:
        url = BASE_URL + endpoint
        try:
            resp = requests.get(url, headers=HEADERS, params=params, timeout=20)
            if resp.status_code in (200, 206):
                data = resp.json()
                # normaliza para lista
                if isinstance(data, list):
                    return data
                for key in ("leads", "data", "items", "results"):
                    if key in data and isinstance(data[key], list):
                        return data[key]
                return [data] if isinstance(data, dict) else []
            if resp.status_code == 404:
                continue
            print(f"  [{resp.status_code}] {url}: {resp.text[:120]}")
        except requests.RequestException as e:
            print(f"  Erro ao chamar {url}: {e}")

    return []


def diretoria_de(lead: dict) -> str:
    for key in ("diretoria", "department", "departamento", "team", "equipe", "grupo",
                "source", "origin", "origem", "campaignId", "campaign_id"):
        val = lead.get(key)
        if val:
            return str(val)
    return "sem diretoria"


def dentro_do_mes(lead: dict, inicio: date, fim: date) -> bool:
    for key in ("createdAt", "created_at", "date", "data", "created", "timestamp"):
        val = lead.get(key)
        if val:
            try:
                d = datetime.fromisoformat(str(val).replace("Z", "+00:00")).date()
                return inicio <= d <= fim
            except ValueError:
                continue
    # sem data → inclui (o filtro já foi enviado como parâmetro)
    return True


def exibir_relatorio(grupos: dict[str, list], inicio: date, fim: date):
    total = sum(len(v) for v in grupos.values())
    print()
    print("=" * 55)
    print(f"  LEADS POR DIRETORIA — {inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}")
    print("=" * 55)

    if not total:
        print("  Nenhum lead encontrado para o período.")
        print("=" * 55)
        return

    for diretoria, leads in sorted(grupos.items(), key=lambda x: -len(x[1])):
        pct = len(leads) / total * 100
        barra = "█" * int(pct / 2)
        print(f"  {diretoria:<30} {len(leads):>5}  ({pct:5.1f}%)  {barra}")

    print("-" * 55)
    print(f"  {'TOTAL':<30} {total:>5}")
    print("=" * 55)
    print()


def main():
    args = parse_args()
    inicio, fim = mes_range(args.mes)
    label = inicio.strftime("%m/%Y")
    print(f"Buscando leads do CRM para {label}...")

    leads = fetch_leads(inicio, fim)

    if not leads:
        print("Nenhum dado retornado pela API. Verifique:")
        print("  • CRM_API_KEY no .env está correto")
        print("  • Endpoints disponíveis no CRM")
        sys.exit(1)

    print(f"{len(leads)} lead(s) recebido(s).")

    grupos: dict[str, list] = defaultdict(list)
    for lead in leads:
        if dentro_do_mes(lead, inicio, fim):
            grupos[diretoria_de(lead)].append(lead)

    exibir_relatorio(grupos, inicio, fim)


if __name__ == "__main__":
    main()
