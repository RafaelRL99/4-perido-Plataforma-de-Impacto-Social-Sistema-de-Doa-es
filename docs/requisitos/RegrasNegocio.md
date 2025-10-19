
# Regras de Negócio (RB)

- **RB01 — Vínculo de Item ao Doador:** todo *Item* pertence a um *Doador* válido.
- **RB02 — Vínculo de Solicitação ao Beneficiário:** toda *Solicitação* pertence a um *Beneficiário* válido.
- **RB03 — Status de Item Entregue:** item em **Entregue** não retorna a **Disponível** sem justificativa registrada.
- **RB04 — Conclusão por Organização:** apenas *Organização* (ou perfil autorizado) pode concluir entregas.
- **RB05 — Integridade de Quantidade:** `quantidade >= 0` para *Item*.
- **RB06 — Cancelamento de Solicitação:** cancelamento permitido apenas antes de **Atendida**.
