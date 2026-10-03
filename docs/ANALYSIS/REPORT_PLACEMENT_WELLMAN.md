---
{
  "schema": "wellmanifest.docs/document/v2",
  "id": "report-placement-wellman",
  "kind": "analysis",
  "version": 2,
  "title": "Raport agenta w repozytorium i bezpieczna adopcja Wellmana",
  "status": "proposed",
  "owner": "wellmanifest/agent",
  "scope": "repository",
  "updated": "2026-10-03",
  "source_revision": "942d6289f729e997815bf35bad378d653ea78b9a",
  "priority": "P1",
  "evidence": [
    "repo://wellmanifest/docs@19efafbeb18923cfd51cc69bd519330488500137/docs/standard/POLICY.md",
    "repo://wellmanifest/wellman@901ea472ace68e18771a13f011554e8fe5f3c15c/src/wellman/cli.py",
    "repo://wellmanifest/wellman@82c9936e9c3a92aff325fb5293e729e0b5bd0a1d/src/wellman/adoption.py",
    "https://github.com/wellmanifest/wellman/issues/2",
    "https://github.com/wellmanifest/taskand/pull/6",
    "https://github.com/wellmanifest/agent/pull/15",
    "receipt:repo-local-report-20260919.path-probe"
  ]
}
---

# Raport agenta i ścieżki lokalne

<!-- docs:section summary -->
## Przyczyna incydentu

Po publikacji wskazówek MCP agent podał `~/.local/state/mcp-repair-20260919/publication-delivery.json`
jako pełny raport dostawy. To pomylenie pomocniczego rejestru operacyjnego
z rezultatem dla użytkownika. Docs DOCS-003/007 wymaga wersjonowanego wyniku
w repozytorium właściciela, indeksu i jawnego stanu publikacji.
Wskazówki MCP były scalone, lecz sam podlinkowany raport pozostawał prywatny.
Ta analiza dotyczy zachowania agenta; nie jest audytem zgodności całej floty.

<!-- docs:section details -->
## Rozdzielenie ścieżek

| Dane | Miejsce i warunek |
| --- | --- |
| Wynik dla zespołu | `docs/` aktywnego repo/worktree, zatwierdzona ścieżka Docs, indeks, Git |
| Surowe dowody lokalne | Ignorowane `.subactor/receipts/` i `.subactor/recovery/`; przed usunięciem worktree zachowanie w głównym checkoutcie |
| Lease i układ worktree | Główny checkout rozpoznany przez Git; `.subactor/leases/` oraz `.worktrees/ticket-NNN--slug` |
| Kontroler, sekrety, niezależny Validator | Chroniony magazyn poza checkoutem PR; nie migrować do `docs/` |
| Zainstalowany CLI | Instalacja użytkownika może być poza repo; nie jest raportem ani dowodem adopcji |

Nie należy utożsamiać `Path.resolve()` z identyfikacją repozytorium.
Ustal Git root, główny checkout lease/recovery oraz bezpieczną ścieżkę docelową.
Zewnętrzny katalog nie jest domyślnie repozytorium; bootstrap wymaga jawnego trybu.

## Stan Wellmana obserwowany 2026-09-19

Zainstalowany Wellman 0.20.36 ma katalog standardów, ale wybranie Docs zwraca
`GOV-STANDARD-NOT-IMPLEMENTED`. Dotychczasowy `adopt` tworzy podstawowy manifest;
nie uruchamia przygotowania/odbioru dokumentu ani nie instaluje chronionej bramy.
Nowa addytywna rejestracja w ticket-002 jest osobnym, niescalonym kandydatem.
Rejestracja, dostępność checkera, konfiguracja CI i zweryfikowane wdrożenie
muszą pozostać osobnymi stanami. Nie stosować `adopt --force` do istniejących pinów.

<!-- docs:section validation -->
## Obserwacja 2026-09-19

Trzy wywołania zainstalowanego `wellman adopt baseline --root PATH` wykonano
wyłącznie w jednorazowych fixture'ach, bez kodu i danych projektów:

- Podkatalog repo: zapis w `nested/.governance`, nie w Git root.
- Katalog bez Git: zapis przyjęty bez rozróżnienia bootstrapu.
- `.governance` jako symlink: zapis przeszedł do zewnętrznego celu.

To reprodukcje braków, nie testy naprawy. Układ bieżącego ticket-011
przeszedł zarządzane `feature-probe` i `validate --check-filesystem` v5.
Lokalne Docs prepare zaakceptowało oba dokumenty przed zapisem.
Oba odbiory Docs przeszły; 7 regresji adaptera, 4 pozytywne/15 negatywnych
przypadków agenta i 1 pozytywny/14 negatywnych publishera również przeszły.
Docs wybiera środowisko wykonania; lokalny PASS nie zaświadcza wdrożenia Wellmana.

<!-- docs:section risks -->
## Stan przekazania z 2026-09-19

Poprawiono wskazówki agenta i umieszczono tę analizę w indeksowanym repozytorium.
Runtime pozostaje bez zmian. Użytkownik zatwierdził przekazanie Wellman
ticket-002; kontroler anulował stary lease i wydał nowy z fencing 40.
Migracja lokalnej tożsamości ticketu nadal wymaga opublikowanego allocatora;
jej naprawa istnieje w [PR #388](https://github.com/wellmanifest/new-project/pull/388).
Kolejka PLF-009 wiąże dalsze prace z istniejącym issue #2; timeout nie daje własności.
Po dopuszczeniu ticketu: resolver i testy root/subdirectory/worktree/symlink,
integracja przypiętego Docs, jeden kontrolowany adopter, dopiero potem kolejne
repozytoria z testem zachowania pinów i idempotencji. Zachować stare bramy
oraz prywatne kopie; nie zgłaszać masowej adopcji na podstawie scaffoldingu.

## Aktualizacja 2026-10-03

Użytkownik zlecił publikację istniejącego ticket-011. Powyższe reprodukcje dotyczą 2026-09-19. [Issue Wellmana #2](https://github.com/wellmanifest/wellman/issues/2) zamknięto 2026-09-28; nie dowodzi to wdrożenia floty. Zakres obejmuje analizę i wskazówki, z ponownym Docs/conformance/governance oraz niezależnym zatwierdzeniem HEAD. Nie zmienia runtime ani admission.
