# SocialScanner: Data Pipeline

Repozitář obsahuje kontejnerizovanou architekturu pro sběr, transformaci a analýzu dat. Systém využívá `uv` pro deterministickou správu závislostí a `ruff` pro statickou analýzu kódu.

## 1. Prvotní sestavení projektu (Nová instalace)
Postup pro inicializaci po naklonování repozitáře.

**Krok 1: Instalace závislostí**
Příkaz vytvoří virtuální prostředí (`.venv`) a nainstaluje přesné verze knihoven z `pyproject.toml` (resp. `uv.lock`).
```powershell
uv sync
```

**Krok 2: Konfigurace prostředí**
Aplikace vyžaduje lokální definici proměnných. Vytvořte soubor `.env` v kořenovém adresáři:
```text
supabase_url="https://[PROJECT-ID].supabase.co"
supabase_key="[SERVICE-ROLE-KEY]"
openai_api_key="sk-[TOKEN]"
apify_token="apify_[TOKEN]"
```
*Poznámka: Chybějící klíč způsobí fatální chybu při startu kvůli striktní validaci Pydantic.*

## 2. Spouštění a aktivace (Každodenní práce)
Nástroj `uv` eliminuje nutnost manuální aktivace virtuálního prostředí. Příkaz `uv run` automaticky detekuje `.venv` a spouští kód v jeho kontextu.

**Metoda A: Přímé spuštění (Doporučeno)**
Spouští izolovaný proces bez změny stavu terminálu.
```powershell
uv run python src/main.py
```

**Metoda B: Manuální aktivace prostředí**
Pro trvalou aktivaci v daném terminálovém okně (např. pro debugování). Změní prompt terminálu, čímž indikuje aktivní kontext.
```powershell
.\.venv\Scripts\activate
```
*(Pro ukončení izolovaného kontextu zadejte příkaz `deactivate`)*

## 3. Vývojový cyklus (Standardní operační postup)
Pro udržení integrity kódu aplikujte před každým commitem následující sekvenci.

**1. Analýza logiky (Linter)**
Detekuje nepoužité importy a syntaktické anomálie. Přepínač `--fix` aplikuje bezpečné automatické opravy.
```powershell
uv run ruff check . --fix
```

**2. Sjednocení formátu (Formatter)**
Zarovná kód podle standardů.
```powershell
uv run ruff format .
```

**3. Validace testů**
```powershell
uv run pytest
```

## 4. Správa závislostí
Příkazy pro modifikaci systémového prostředí.

Přidání nové analytické nebo systémové knihovny (aktualizuje `pyproject.toml`):
```powershell
uv add <nazev_knihovny>
```
Odstranění existující knihovny:
```powershell
uv remove <nazev_knihovny>
```

## 5. Architektura adresáře src/
Logika musí být striktně izolována do definovaných vrstev. Křížové závislosti mezi výpočetními fázemi nejsou povoleny.

* `config.py`: Načítání a typová kontrola konfigurace z `.env`.
* `ingest/`: Moduly pro sběr dat (API, scrapping). Žádné modifikace struktury dat.
* `transform/`: NLP procesy, formátování, LLM volání. Zákaz I/O operací do databáze.
* `load/`: Databázové transakce. Zákaz transformační logiky.
* `analyze/`: Agregace, detekce trendů a anomálií pro analytické výstupy.
* `utils/`: Sdílené I/O, logování a pomocné funkce.


## 6. Infrastruktura a nasazení (Serverless)
Architektura „Serverless first“ minimalizuje fixní provozní náklady a eliminuje nutnost manuální správy operačních systémů.

* **Databáze (Supabase / PostgreSQL):**
  Centrální úložiště strukturovaných dat. Zajišťuje ukládání surových textů a jejich vektorových reprezentací (embeddingů) pomocí nativního rozšíření pgvector. Přístupové údaje (URL, anon/public klíč) se distribuují výhradně přes proměnné prostředí.
* **Výpočetní server (Railway):**
  Prostředí pro kontinuální běh aplikačních rozhraní (API), naslouchání webhookům a exekuci plánovaných úloh (Cron). Podporuje přímou integraci s verzovacím systémem pro automatický deployment při každém odeslání kódu (git push).
* **Strojové učení a ETL (Modal):**
  Dedikovaná platforma pro asynchronní a výpočetně náročné úlohy, jako je hromadné zpracování tisíců záznamů přes LLM. Umožňuje dynamickou alokaci hardwarových zdrojů (včetně GPU) s účtováním pouze za exekuční čas.
* **Správa citlivých údajů:**
  Lokální soubor `.env` je v produkčním prostředí striktně nahrazen nativními správci tajných kódů (Secrets) v ovládacích panelech příslušných služeb (Railway, Modal, Supabase).

Následující modul modeluje odhadovanou propustnost a nákladovost infrastruktury.

## 7. Architektura systému a Databáze

Vizualizace naší data pipeline a struktury databáze:

![Schéma architektury](docs/architecture.png)
![Schéma databáze](docs/db_schema.png)

Pro detailní popis tabulek nahlédněte do [dokumentace databáze](docs/database.md).