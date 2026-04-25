# SocialScanner

**SocialScanner** je datová platforma pro sběr, normalizaci, ukládání a analýzu veřejně dostupných online zmínek ze sociálních sítí, zpravodajských webů, RSS kanálů, diskusních platforem a dalších digitálních zdrojů.

Cílem projektu je vytvořit základ pro systém, který bude schopný sledovat vybrané entity, analyzovat online zmínky, rozpoznávat vznikající témata, měřit sentiment, detekovat anomálie a upozorňovat na potenciálně rizikové trendy v online prostoru.

Projekt je navržen jako modulární **data pipeline** s architekturou **serverless-first**, která je připravená na budoucí SaaS režim, více zákazníků, analytické dashboardy, alerting a automatické reporty.

---

## Hlavní účel projektu

SocialScanner řeší kompletní tok dat od získání externího obsahu až po analytické výstupy.

Základní cíle systému:

- sbírat veřejně dostupná data z definovaných zdrojů,
- normalizovat obsah do jednotného interního modelu,
- ukládat surová i zpracovaná data do PostgreSQL/Supabase,
- extrahovat entity, témata a další signály,
- vytvářet embeddingy pro sémantické vyhledávání,
- počítat sentiment, riziko a trendové metriky,
- detekovat anomálie a náhlé změny v online diskusi,
- připravovat podklady pro alerty, dashboardy a reporty.

---

## Stav projektu

Projekt je ve vývojové fázi.

Aktuální priorita je vytvořit stabilní technické jádro:

1. databázové schéma,
2. základní ingest pipeline,
3. normalizaci a deduplikaci dat,
4. ukládání do Supabase/PostgreSQL,
5. první podporovaný datový zdroj,
6. základní entity matching,
7. jednoduchou analytickou vrstvu,
8. první trendové a alertovací mechanismy.

---

## Technologický stack

| Oblast | Technologie |
|---|---|
| Jazyk | Python |
| Správa závislostí | `uv` |
| Linting a formátování | `ruff` |
| Testování | `pytest` |
| Databáze | Supabase / PostgreSQL |
| Vektorové vyhledávání | `pgvector` |
| NLP / LLM | OpenAI API | Gemini API |
| Scraping / crawling | Apify |
| Výpočetně náročné úlohy | Modal |
| API / Cron / Webhooky | Railway |
| Konfigurace | `.env`, Pydantic settings |

---

## Doporučená struktura projektu

```text
social-scanner/
├── docs/
│   ├── architecture.md
│   ├── database.md
│   ├── data_sources.md
│   ├── pipeline.md
│   ├── entities.md
│   ├── trend_detection.md
│   └── alerting.md
├── src/
│   ├── ingest/
│   ├── transform/
│   ├── load/
│   ├── analyze/
│   ├── utils/
│   ├── config.py
│   └── main.py
├── tests/
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
├── README.md
└── TODO.md
```

---

## Dokumentace

Detailní dokumentace je rozdělena do samostatných souborů ve složce `docs/`.

| Dokument | Popis |
|---|---|
| `docs/architecture.md` | Architektura systému a hlavní komponenty |
| `docs/database.md` | Databázový model a DDL schéma |
| `docs/data_sources.md` | Šablona a pravidla pro budoucí datové zdroje |
| `docs/pipeline.md` | Popis datové pipeline a stavů zpracování |
| `docs/entities.md` | Model entit, aliasů a entity matchingu |
| `docs/trend_detection.md` | Principy detekce trendů a anomálií |
| `docs/alerting.md` | Návrh alertů, severity a alert lifecycle |
| `TODO.md` | Postup implementace krok za krokem |

---

## Rychlý start

### 1. Naklonování repozitáře

```powershell
git clone <repository-url>
cd social-scanner
```

### 2. Instalace závislostí

```powershell
uv sync
```

Příkaz vytvoří lokální virtuální prostředí `.venv` a nainstaluje závislosti podle `pyproject.toml` a `uv.lock`.

---

## Konfigurace prostředí

Aplikace vyžaduje lokální soubor `.env` v kořenovém adresáři projektu.

Doporučený postup:

```powershell
copy .env.example .env
```

Doporučený obsah `.env.example`:

```text
SUPABASE_URL="https://[PROJECT-ID].supabase.co"
SUPABASE_KEY="[SERVICE-ROLE-KEY]"
OPENAI_API_KEY="sk-[TOKEN]"
APIFY_TOKEN="apify_[TOKEN]"
ENVIRONMENT="local"
LOG_LEVEL="INFO"
```

Pokud aktuální implementace `src/config.py` používá názvy proměnných malými písmeny, ponechte názvy podle implementace nebo upravte konfiguraci na standardní uppercase tvar.

Citlivé údaje nikdy necommitujte do repozitáře.

---

## Spouštění aplikace

Doporučený způsob spuštění:

```powershell
uv run python src/main.py
```

Nástroj `uv` automaticky použije lokální `.venv`, takže není nutné virtuální prostředí ručně aktivovat.

---

## Manuální aktivace virtuálního prostředí

Pro delší vývojovou relaci lze prostředí aktivovat ručně:

```powershell
.\.venv\Scripts\activate
```

Deaktivace:

```powershell
deactivate
```

---

## Vývojový cyklus

Před každým commitem spusťte následující příkazy.

### 1. Linting

```powershell
uv run ruff check . --fix
```

### 2. Formátování

```powershell
uv run ruff format .
```

### 3. Testy

```powershell
uv run pytest
```

---

## Správa závislostí

### Přidání knihovny

```powershell
uv add <nazev_knihovny>
```

### Odebrání knihovny

```powershell
uv remove <nazev_knihovny>
```

### Synchronizace prostředí

```powershell
uv sync
```

---

## Vrstvy aplikace

Aplikace je rozdělena do jasně oddělených vrstev.

### `src/config.py`

Načítá a validuje konfiguraci aplikace.

Odpovědnosti:

- načtení `.env`,
- validace povinných proměnných,
- typově bezpečný přístup ke konfiguraci,
- selhání při chybějící nebo nevalidní konfiguraci.

---

### `src/ingest/`

Vrstva pro sběr dat.

Odpovědnosti:

- napojení na API,
- práce s RSS,
- integrace Apify actorů,
- jednoduchý crawling veřejných zdrojů,
- předání surových dat do normalizační vrstvy.

Tato vrstva by neměla obsahovat analytickou ani databázovou logiku.

---

### `src/transform/`

Vrstva pro čištění, obohacení a normalizaci dat.

Odpovědnosti:

- čištění textu,
- normalizace URL,
- tvorba hashů pro deduplikaci,
- detekce jazyka,
- extrakce entit,
- výpočet sentimentu,
- tvorba embeddingů,
- příprava interních datových modelů.

Tato vrstva by neměla přímo zapisovat do databáze.

---

### `src/load/`

Vrstva pro ukládání dat.

Odpovědnosti:

- databázové transakce,
- insert/update/upsert operace,
- ukládání dokumentů,
- ukládání entit,
- ukládání vazeb mezi dokumenty a entitami,
- ukládání běhů pipeline a chyb.

Tato vrstva by neměla obsahovat NLP ani analytickou logiku.

---

### `src/analyze/`

Vrstva pro analytické výpočty.

Odpovědnosti:

- agregace zmínek,
- výpočet trendových snímků,
- detekce anomálií,
- výpočet rizikového skóre,
- výpočet trend score,
- příprava podkladů pro alerty a reporty.

---

### `src/utils/`

Sdílené pomocné funkce.

Odpovědnosti:

- logování,
- práce se soubory,
- obecné validátory,
- normalizační utility,
- helper funkce používané napříč vrstvami.

---

## Základní datový tok

```text
Externí zdroj
    ↓
Ingest
    ↓
Transformace
    ↓
Load do databáze
    ↓
Analýza
    ↓
Alerty / Dashboardy / Reporty
```

---

## Infrastruktura

Projekt je navržen jako serverless-first.

### Supabase / PostgreSQL

Použití:

- hlavní databáze,
- ukládání raw dat,
- ukládání entit,
- ukládání trendů,
- ukládání alertů,
- pgvector pro embeddingy,
- Supabase Auth pro budoucí uživatele a tenanty.

### Railway

Použití:

- běh API,
- webhooky,
- jednoduché cron úlohy,
- deployment při `git push`,
- lehčí background workery.

### Modal

Použití:

- dávkové NLP úlohy,
- embedding pipeline,
- LLM processing,
- výpočetně náročné joby,
- úlohy vyžadující paralelizaci nebo GPU.

---

## Bezpečnostní zásady

- Nikdy necommitovat `.env`.
- Nikdy necommitovat API klíče.
- `SUPABASE_SERVICE_ROLE_KEY` používat pouze na serverové straně.
- Service role key nikdy nesmí být ve frontendu.
- Logy nesmí obsahovat secrets.
- Logy nesmí zbytečně obsahovat osobní údaje.
- Pro produkční prostředí používat secrets manager dané platformy.
- Pro budoucí frontend zapnout a správně nastavit RLS policies.

---

## Doporučený commit checklist

Před commitem ověřit:

- [ ] aplikace se spustí lokálně,
- [ ] `.env` není součástí commitu,
- [ ] nejsou commitnuté žádné tokeny nebo secrets,
- [ ] `uv run ruff check . --fix` proběhl bez chyb,
- [ ] `uv run ruff format .` proběhl bez chyb,
- [ ] `uv run pytest` proběhl úspěšně,
- [ ] nové moduly respektují vrstvy aplikace,
- [ ] databázové změny jsou zdokumentované,
- [ ] změny v pipeline jsou popsány v dokumentaci.

---

## Minimální MVP cíl

První funkční MVP by mělo umět:

- načíst konfiguraci z `.env`,
- připojit se k Supabase,
- spustit jeden ingest zdroj,
- stáhnout několik veřejných záznamů,
- normalizovat je,
- deduplikovat je,
- uložit je do `raw_social_data`,
- detekovat základní entity,
- uložit vazby do `document_entities`,
- vytvořit jednoduchý trendový přehled,
- vygenerovat jednoduchý alert při nárůstu zmínek.

---

## Budoucí rozšíření

Možné další směry vývoje:

- dashboard pro zákazníky,
- multi-tenant SaaS režim,
- role a oprávnění,
- monitoring více platforem,
- sentiment scoring,
- risk scoring,
- trend scoring,
- detekce šíření mezi platformami,
- mapování vztahů mezi dokumenty,
- denní a týdenní reporty,
- Slack/Teams/e-mail alerty,
- API pro externí integrace,
- billing a klientské tarify.
