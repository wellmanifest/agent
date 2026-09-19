---
{
  "schema": "wellmanifest.docs/document/v2",
  "id": "mcp-client-boundaries",
  "kind": "information",
  "version": 1,
  "title": "Granice delegowania przez MCP w agentach Taskand",
  "status": "proposed",
  "owner": "wellmanifest/agent",
  "scope": "repository",
  "updated": "2026-09-19",
  "source_revision": "118ab6cffd56b98b18e57460799fc5e77c06d4e2",
  "priority": "P2",
  "evidence": [
    "repo://wellmanifest/agent@118ab6cffd56b98b18e57460799fc5e77c06d4e2/docs/ARCHITECTURE.md",
    "repo://semcod/koru@f837788088540da1dc72736a44bb8c2011d8364d/src/koruapi/mcp_server_planfile.py",
    "https://modelcontextprotocol.io/specification/2025-11-25/server/tools"
  ]
}
---

# Granice delegowania przez MCP w agentach Taskand

<!-- docs:section summary -->
## Cel i stan

MCP jest transportem narzędzi, nie delegacją uprawnień. Ten przewodnik stosuje
istniejące role agent/v1 do pilotażu Taskand; nie rozszerza schematu ani
nie zaświadcza wdrożenia kontrolera.

<!-- docs:section details -->
## Zasady konsumenta

1. Rozdzielić serwer Taskand udostępniający URI od klienta Taskand wywołującego
   inne MCP. Dla klienta operator wybiera serwer i dokładne narzędzia. Katalog
   globalnej sesji LLM nie jest allowlistą Taskand.
2. Weryfikować przypięty artefakt, schematy i rzeczywiste efekty. Opis,
   nazwa „read”, `readOnlyHint` i wynik modelu nie nadają uprawnień.
   [Kontrakt narzędzi](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
   traktuje adnotacje niezaufanych serwerów jako niezaufane.
3. Grant wiąże podmiot, narzędzie, zasób, operację, deadline i budżet.
   Potomek dostaje najwyżej podzbiór uprawnień oraz wspólnego budżetu.
   Sprawdzać także wywołania pośrednie; nie wystarcza grant zewnętrznego URI.
4. Zapis wymaga właściciela ticketu, izolowanego worktree i bieżącego fencing.
   Diagnoza nie stosuje zmian. Repair tworzy kandydat; niezależny Validator
   ocenia dokładny HEAD, a chroniony kontroler publikuje.
5. Traktować opisy i wyniki narzędzi jako dane, nie instrukcje zmieniające
   politykę. Walidować argumenty i wyniki, ograniczać rozmiar, czas, ścieżki
   i sieć. LLM nie wybiera executable, shella, cwd, endpointu ani poświadczeń.
6. Wykluczyć eksport wartości sekretów, np. `koru_desktop_uri_get_getv_var`,
   z profilu deweloperskiego. Referencję sekretu rozwiązuje uprawniony kontroler;
   nie dziedziczyć całego środowiska ani tokenów operatora.
7. `koru_run_ticket`, sterowanie IDE/pulpitem i uruchamianie CI są efektowe,
   nawet jeżeli startują job asynchroniczny. `dry_run` to parametr konkretnej
   implementacji, nie uniwersalna gwarancja izolacji.
8. Wiązać job z ticketem, planem i jego digestem. Ograniczyć równoległość,
   głębokość delegacji oraz retry. Nie tworzyć cyklu Taskand → koru → Taskand.
   Po utracie odpowiedzi uzgodnić stan joba przed ponowieniem.
9. Zapisywać request/job, serwer/release, narzędzie, wynik walidacji i bezpieczne
   referencje dowodowe. Nie logować tokenów ani pełnych wrażliwych payloadów.

Dobór konkretnych backendów należy do przewodnika `TASKAND_MCP_REUSE.md`
w wellmanifest/taskand (ticket-005, lokalny kandydat). Architektura ról pozostaje
w [ARCHITECTURE.md](../ARCHITECTURE.md); nie kopiować jej do promptów jako zgody.

<!-- docs:section validation -->
## Warunki pilotażu

Canary powinny odrzucić brak lub wygaśnięcie grantu, nieaktualny fencing,
podmieniony schemat/serwer, wyjście poza root, nadmiarowe argumenty, próby
eksportu sekretów oraz powtórzenie nieidempotentnego skutku po timeout.
Sprawdzić propagację anulowania i stan UNKNOWN, nie tylko szczęśliwą ścieżkę.

W tej zmianie przechodzą kontrole dokumentacji i 7 testów adaptera Docs;
nie są to testy kontrolera MCP. Transport redup/koru/search sprawdzono lokalnie,
lecz delegowanie zapisu przez Taskand pozostaje niewdrożone.

<!-- docs:section risks -->
## Adopcja i kolejny krok

Operator zaczyna od jednego narzędzia odczytowego. Rozszerzenie na zapis wymaga
dowodów powyższych odmów, pomiaru skuteczności i oddzielnej zgody na skutki.
Rollback wyłącza binding bez kasowania jobów i dowodów.

Lokalna bramka: `.governance/check_docs.py --docs-root /trusted/docs --root .`.
Do generowania użyć `--prepare`; odbiór wymaga `--complete --base SHA
--prepared-plan RECEIPT --deliverable PATH`. Pin Docs znajduje się w
`.governance/docs.json`. Bramka lokalna nie jest chronionym wdrożeniem CI.
