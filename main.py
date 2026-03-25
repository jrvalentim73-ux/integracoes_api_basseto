from config import DEFAULT_CAMPAIGN_ID
from sheets import get_pending_leads, update_row_status
from crm import send_lead


def main():
    print("Buscando leads pendentes na planilha...")
    leads, ws, status_col = get_pending_leads()

    if not leads:
        print("Nenhum lead pendente encontrado.")
        return

    print(f"{len(leads)} lead(s) pendente(s) encontrado(s).\n")

    sent = 0
    errors = 0

    for lead in leads:
        row = lead["row_number"]

        # Validar campos obrigatórios
        missing = [f for f in ("name", "email", "phone") if not lead[f]]
        if missing:
            msg = f"error: campos obrigatórios vazios ({', '.join(missing)})"
            update_row_status(ws, row, status_col, msg)
            print(f"  Linha {row}: {msg}")
            errors += 1
            continue

        # Aplicar campaignId padrão se vazio
        if not lead["campaignId"]:
            lead["campaignId"] = DEFAULT_CAMPAIGN_ID

        # Enviar ao CRM
        result = send_lead(lead)

        if result["success"]:
            update_row_status(ws, row, status_col, "sent")
            print(f"  Linha {row}: enviado com sucesso")
            sent += 1
        else:
            msg = f"error: {result['detail']}"
            update_row_status(ws, row, status_col, msg)
            print(f"  Linha {row}: {msg}")
            errors += 1

    print(f"\nConcluído. {sent} enviado(s), {errors} erro(s).")


if __name__ == "__main__":
    main()
