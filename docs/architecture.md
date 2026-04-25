# Architektura systému: SocialScanner

Tento dokument popisuje technickou architekturu projektu **SocialScanner**.

SocialScanner je systém pro sběr, normalizaci, ukládání a analýzu veřejně dostupných online zmínek. Jeho účelem je sledovat vybrané entity, rozpoznávat vznikající témata, analyzovat sentiment, vyhodnocovat riziko a vytvářet podklady pro alerting, reporting a dashboardy.

---

## Cíle architektury

Architektura je navržena tak, aby podporovala:

- postupné rozšiřování datových zdrojů,
- multi-tenant režim pro více zákazníků,
- oddělení ingest, transform, load a analyze vrstvy,
- auditovatelné zpracování dat,
- snadné ladění pipeline,
- nízké fixní provozní náklady,
- serverless-first provoz,
- budoucí dashboardy, alerty, reporty a API,
- bezpečné nakládání s API klíči a zákaznickými daty.

---

## Základní principy

### 1. Modulární pipeline

Systém je rozdělen do samostatných vrstev:

```text
Externí zdroje
    ↓
Ingest
    ↓
Transform
    ↓
Load
    ↓
Analyze
    ↓
Alerting / Reporting / Dashboardy
```

Každá vrstva má jasně vymezenou odpovědnost. Tím se snižuje složitost, zlepšuje testovatelnost a usnadňuje budoucí rozšíření.

---

### 2. Oddělení odpovědností

Jednotlivé vrstvy by neměly přebírat odpovědnost jiné vrstvy.

Například:

- `ingest` pouze získává data,
- `transform` data čistí a obohacuje,
- `load` zapisuje do databáze,
- `analyze` počítá agregace, trendy a anomálie,
- `alerting` rozhoduje, zda má být uživatel upozorněn.

Toto pravidlo je důležité pro dlouhodobou udržitelnost projektu.

---

### 3. Serverless-first přístup

Projekt preferuje služby, které umožňují škálování bez manuální správy serverů.

Typické služby:

- **Supabase / PostgreSQL** pro databázi,
- **Railway** pro API, cron joby, webhooky a dlouhodobě běžící procesy,
- **Modal** pro dávkové výpočty, LLM pipeline, embeddingy a náročnější ETL úlohy,
- **Apify** pro vybrané crawling nebo scraping scénáře.

---

### 4. Multi-tenant design

Systém je připraven na více zákazníků.

Každý zákazník je reprezentován tenantem. Většina hlavních tabulek obsahuje `tenant_id`, aby bylo možné oddělit data jednotlivých zákazníků.

To umožňuje:

- samostatné sledované entity pro každého zákazníka,
- samostatné datové zdroje,
- samostatné alerty,
- samostatné dashboardy,
- agenturní režim pro více klientů.

---

## Hlavní komponenty

### 1. Ingest vrstva

Ingest vrstva zajišťuje získávání dat z externích zdrojů.

Typické zdroje:

- RSS feedy,
- zpravodajské weby,
- veřejná API,
- Apify actors,
- veřejné diskusní zdroje,
- ruční importy,
- webhooky.

Odpovědnosti:

- připojení ke zdroji,
- stažení dat,
- základní validace dostupnosti obsahu,
- zachování původních metadat,
- předání dat do další fáze pipeline.

Ingest vrstva nesmí obsahovat hlubokou transformační, analytickou ani databázovou logiku.

---

### 2. Transform vrstva

Transform vrstva převádí surová data na normalizovaný interní formát.

Odpovědnosti:

- čištění textu,
- normalizace URL,
- normalizace autora,
- výpočet hashe obsahu,
- deduplikace na úrovni obsahu,
- detekce jazyka,
- extrakce entit,
- matching aliasů,
- sentiment analýza,
- výpočet embeddingů,
- příprava dat pro databázový zápis.

Transform vrstva by neměla zapisovat přímo do databáze. Výstupem by měl být validovaný datový objekt předaný load vrstvě.

---

### 3. Load vrstva

Load vrstva zajišťuje bezpečný zápis do databáze.

Odpovědnosti:

- insert,
- update,
- upsert,
- transakce,
- řešení duplicit,
- ukládání vazeb mezi dokumenty a entitami,
- ukládání vazeb mezi dokumenty a tématy,
- ukládání auditních událostí.

Load vrstva nesmí obsahovat NLP, business scoring ani scraping logiku.

---

### 4. Analyze vrstva

Analyze vrstva vytváří analytické výstupy nad uloženými daty.

Odpovědnosti:

- agregace podle času,
- agregace podle entit,
- agregace podle témat,
- výpočet trend score,
- výpočet anomaly score,
- výpočet risk score,
- hledání náhlých změn,
- příprava dat pro dashboardy,
- příprava dat pro alerting.

---

### 5. Alerting vrstva

Alerting vrstva rozhoduje, zda je situace natolik důležitá, aby vznikl alert.

Odpovědnosti:

- vyhodnocení alert pravidel,
- deduplikace alertů,
- aktualizace existujících alertů,
- změna severity,
- uzavření alertu,
- příprava notifikace,
- předání alertu do e-mailu, Slacku, Teams nebo webhooku.

---

### 6. Reporting vrstva

Reporting vrstva vytváří periodické souhrny.

Typické reporty:

- denní přehled zmínek,
- týdenní přehled trendů,
- report pro konkrétní entitu,
- report negativních zmínek,
- report nových témat,
- krizový report k alertu.

---

### 7. API vrstva

API vrstva bude sloužit pro přístup frontendové aplikace, dashboardů a externích integrací.

Typické oblasti API:

- tenants,
- data sources,
- documents,
- entities,
- topics,
- trends,
- alerts,
- reports.

API musí respektovat tenant isolation a oprávnění uživatele.

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
│   ├── alerting/
│   ├── reports/
│   ├── utils/
│   ├── config.py
│   └── main.py
├── tests/
├── .env.example
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## Vrstvy v adresáři `src`

### `src/config.py`

Načítání a validace konfigurace.

Typicky obsahuje:

- Supabase URL,
- Supabase key,
- OpenAI API key,
- Apify token,
- nastavení prostředí,
- nastavení logování,
- limity pipeline.

---

### `src/ingest/`

Moduly pro sběr dat.

Příklady modulů:

```text
src/ingest/
├── rss.py
├── apify.py
├── web_api.py
├── manual_import.py
└── base.py
```

---

### `src/transform/`

Moduly pro zpracování obsahu.

Příklady modulů:

```text
src/transform/
├── normalize.py
├── deduplicate.py
├── language.py
├── entities.py
├── sentiment.py
├── embeddings.py
└── models.py
```

---

### `src/load/`

Databázová vrstva.

Příklady modulů:

```text
src/load/
├── db.py
├── documents.py
├── entities.py
├── topics.py
├── runs.py
└── events.py
```

---

### `src/analyze/`

Analytická vrstva.

Příklady modulů:

```text
src/analyze/
├── trends.py
├── anomalies.py
├── scoring.py
├── aggregation.py
└── similarity.py
```

---

### `src/alerting/`

Alerting logika.

Příklady modulů:

```text
src/alerting/
├── rules.py
├── evaluator.py
├── notifier.py
└── lifecycle.py
```

---

### `src/utils/`

Sdílené pomocné funkce.

Typicky:

- logování,
- práce s časem,
- hashování,
- URL normalizace,
- retry helpery,
- validace.

---

## Datový tok

### 1. Stažení dat

Systém spustí konkrétní `data_source`.

Výstupem je kolekce surových záznamů.

---

### 2. Založení collection run

Pro každý běh sběru se vytvoří záznam v `collection_runs`.

Ukládá se:

- začátek běhu,
- konec běhu,
- počet stažených záznamů,
- počet vložených záznamů,
- počet duplicit,
- počet chyb,
- stav běhu.

---

### 3. Normalizace

Každý záznam se převede na interní formát.

Normalizují se zejména:

- URL,
- autor,
- platforma,
- čas publikace,
- text,
- metadata,
- metriky.

---

### 4. Deduplikace

Deduplikace probíhá podle:

- externího ID,
- canonical URL,
- hashe obsahu,
- případně sémantické podobnosti.

---

### 5. Uložení dokumentu

Normalizovaný dokument se uloží do `raw_social_data`.

---

### 6. NLP zpracování

Po uložení nebo před uložením se provádí:

- detekce jazyka,
- extrakce entit,
- sentiment,
- risk score,
- embedding.

---

### 7. Uložení vazeb

Zjištěné entity se ukládají do:

- `entities`,
- `entity_aliases`,
- `document_entities`.

Zjištěná témata se ukládají do:

- `topics`,
- `document_topics`.

---

### 8. Analýza trendů

Analyze vrstva vytváří časové agregace v `trend_snapshots`.

---

### 9. Alerting

Alerting vrstva vyhodnotí, zda vznikl důležitý signál.

Výsledkem může být nový záznam v `alerts`.

---

## Externí služby

### Supabase

Použití:

- PostgreSQL databáze,
- pgvector,
- Supabase Auth,
- RLS,
- API nad tabulkami.

---

### Railway

Použití:

- běh aplikace,
- cron joby,
- webhooky,
- jednoduché API,
- deployment z Git repozitáře.

---

### Modal

Použití:

- dávkové výpočty,
- paralelní NLP zpracování,
- embeddingy,
- LLM úlohy,
- náročnější ETL.

---

### OpenAI API

Použití:

- embeddingy,
- klasifikace,
- extrakce entit,
- sumarizace,
- interpretace trendů,
- generování reportů.

---

### Apify

Použití:

- scraping tam, kde je to povolené,
- crawling vybraných zdrojů,
- spouštění existujících actorů,
- experimentální datové zdroje.

---

## Stavové modely

### Stav dokumentu

```text
pending
processing
processed
error
ignored
duplicate
```

### Stav collection run

```text
running
success
partial_success
error
cancelled
```

### Stav alertu

```text
open
acknowledged
resolved
ignored
```

---

## Chybové scénáře

Systém musí být připraven na:

- výpadek API,
- rate limit,
- změnu struktury zdroje,
- nevalidní data,
- prázdný obsah,
- duplicitní obsah,
- výpadek databáze,
- chybu LLM služby,
- nedostupnost embedding modelu,
- neúspěšný zápis do databáze.

Každá chyba musí být logována v dostatečném detailu, ale bez úniku secrets nebo citlivých údajů.

---

## Logování

Logy by měly obsahovat:

- ID collection run,
- ID zdroje,
- tenant ID,
- počet zpracovaných záznamů,
- chyby,
- délku běhu,
- stav pipeline.

Logy nesmí obsahovat:

- API klíče,
- access tokeny,
- service role key,
- zbytečně velké raw payloady,
- citlivé osobní údaje bez legitimního důvodu.

---

## Bezpečnostní zásady

- `SERVICE_ROLE_KEY` používat pouze na serveru.
- Nikdy neposílat service role key do frontendu.
- Nikdy necommitovat `.env`.
- Používat secrets management produkčních platforem.
- Oddělit zákaznická data pomocí tenantů.
- Při frontendovém přístupu použít RLS.
- Auditovat přístupy a změny důležitých dat.
- Respektovat podmínky externích platforem.

---

## Budoucí rozšíření

Architektura počítá s budoucím rozšířením o:

- frontend dashboard,
- API pro klienty,
- týmové role,
- billing,
- webhook notifikace,
- Slack a Teams integrace,
- generování reportů,
- pokročilé mapování šíření,
- krizové scénáře,
- white-label režim pro agentury.
