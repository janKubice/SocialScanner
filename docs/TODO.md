# SocialScanner TODO: Implementační plán krok za krokem

Tento dokument popisuje doporučený postup vývoje projektu **SocialScanner** od současného stavu až po první funkční MVP.

Cílem není dělat vše najednou. Cílem je postupovat po malých, ověřitelných blocích, aby byl projekt stabilní, rozšiřitelný a technicky čistý.

---

## Hlavní pravidlo postupu

Každý krok by měl skončit ověřitelným výsledkem.

Nepokračovat dál, dokud aktuální část:

- funguje lokálně,
- má základní test,
- je zdokumentovaná,
- nemíchá odpovědnosti mezi vrstvami,
- neobsahuje secrets v repozitáři.

---

## Fáze 0: Úklid repozitáře a základní standardy

### 0.1 Sjednotit strukturu projektu

Vytvořit nebo zkontrolovat strukturu:

```text
social-scanner/
├── docs/
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

Výsledek:

- [ ] projekt má jasnou adresářovou strukturu,
- [ ] každá vrstva má vlastní složku,
- [ ] dokumentace je ve složce `docs/`,
- [ ] repozitář neobsahuje citlivé soubory.

---

### 0.2 Zkontrolovat `.gitignore`

Doporučený obsah:

```gitignore
.env
.venv/
__pycache__/
.pytest_cache/
.ruff_cache/
*.pyc
.DS_Store
.idea/
.vscode/
```

Výsledek:

- [ ] `.env` je ignorovaný,
- [ ] `.venv` je ignorovaný,
- [ ] cache soubory jsou ignorované,
- [ ] IDE soubory nejsou commitované.

---

### 0.3 Vytvořit `.env.example`

Vytvořit soubor `.env.example`:

```text
SUPABASE_URL="https://[PROJECT-ID].supabase.co"
SUPABASE_KEY="[SERVICE-ROLE-KEY]"
OPENAI_API_KEY="sk-[TOKEN]"
APIFY_TOKEN="apify_[TOKEN]"
ENVIRONMENT="local"
LOG_LEVEL="INFO"
```

Výsledek:

- [ ] existuje `.env.example`,
- [ ] neobsahuje skutečné secrets,
- [ ] odpovídá tomu, co očekává `src/config.py`.

---

### 0.4 Ověřit základní příkazy

Spustit:

```powershell
uv sync
uv run ruff check . --fix
uv run ruff format .
uv run pytest
```

Výsledek:

- [ ] závislosti se nainstalují,
- [ ] linting projde,
- [ ] formátování projde,
- [ ] testy projdou nebo existuje jasný seznam chybějících testů.

---

## Fáze 1: Konfigurace a základní aplikační jádro

### 1.1 Dokončit `src/config.py`

Cíl:

- centralizované načítání konfigurace,
- validace povinných proměnných,
- přehledné chybové hlášky,
- žádné čtení `.env` přímo v jiných částech aplikace.

Doporučený model:

```text
Settings
├── supabase_url
├── supabase_key
├── openai_api_key
├── apify_token
├── environment
└── log_level
```

Výsledek:

- [ ] konfigurace se načítá přes jednu třídu/funkci,
- [ ] chybějící proměnná vyvolá srozumitelnou chybu,
- [ ] existuje test pro načtení konfigurace,
- [ ] README odpovídá reálným názvům proměnných.

---

### 1.2 Přidat základní logging

Vytvořit například:

```text
src/utils/logging.py
```

Požadavky:

- jednotný formát logů,
- log level podle konfigurace,
- žádné logování API klíčů,
- možnost používat logger napříč moduly.

Výsledek:

- [ ] aplikace loguje start,
- [ ] aplikace loguje chyby,
- [ ] log level lze změnit přes `.env`,
- [ ] secrets se v logu neobjevují.

---

### 1.3 Upravit `src/main.py`

Cíl:

- `main.py` má pouze spouštěcí logiku,
- neobsahuje implementaci celé pipeline,
- volá samostatné moduly.

Doporučený tok:

```text
load settings
setup logging
start pipeline
handle errors
exit cleanly
```

Výsledek:

- [ ] `uv run python src/main.py` funguje,
- [ ] při chybě konfigurace aplikace skončí čitelně,
- [ ] hlavní logika je delegována do samostatných funkcí.

---

## Fáze 2: Databáze a Supabase

### 2.1 Založit Supabase projekt

Cíl:

- vytvořit Supabase projekt,
- získat URL,
- získat service role key,
- nastavit lokální `.env`.

Výsledek:

- [ ] Supabase projekt existuje,
- [ ] `SUPABASE_URL` je nastavený,
- [ ] `SUPABASE_KEY` je nastavený lokálně,
- [ ] klíče nejsou v repozitáři.

---

### 2.2 Zapnout potřebná PostgreSQL rozšíření

Spustit v Supabase SQL editoru:

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;
```

Výsledek:

- [ ] `pgcrypto` je dostupné,
- [ ] `vector` je dostupné,
- [ ] databáze podporuje UUID a embeddingy.

---

### 2.3 Aplikovat databázové schéma

Použít schéma z:

```text
docs/database.md
```

Doporučené minimální jádro pro začátek:

```text
tenants
tenant_members
data_sources
collection_runs
raw_social_data
entities
entity_aliases
document_entities
processing_events
```

Výsledek:

- [ ] tabulky existují,
- [ ] indexy existují,
- [ ] constraints fungují,
- [ ] `pgvector` sloupec lze vytvořit,
- [ ] dokumentace odpovídá databázi.

---

### 2.4 Vytvořit první testovací tenant

Vložit testovací tenant:

```sql
INSERT INTO tenants (name, slug)
VALUES ('Local Development', 'local-dev');
```

Výsledek:

- [ ] existuje testovací tenant,
- [ ] jeho ID je možné použít v lokálním vývoji,
- [ ] není potřeba vkládat `tenant_id` ručně do kódu napevno bez konfigurace.

---

### 2.5 Připravit databázového klienta

Vytvořit například:

```text
src/load/db_client.py
```

Odpovědnosti:

- vytvoření Supabase klienta,
- kontrola připojení,
- základní helpery pro insert/upsert,
- žádná transformační logika.

Výsledek:

- [ ] aplikace se umí připojit k Supabase,
- [ ] existuje jednoduchý test nebo smoke test připojení,
- [ ] chyby připojení jsou čitelně zalogované.

---

## Fáze 3: Interní datové modely

### 3.1 Definovat model surového dokumentu

Vytvořit například:

```text
src/models.py
```

Nebo rozdělit modely podle domén:

```text
src/models/document.py
src/models/entity.py
src/models/source.py
```

Model `RawDocument` by měl obsahovat:

```text
tenant_id
source_id
external_id
source_platform
source_url
canonical_url
content_type
author_handle
title
content
language_code
published_at
metrics
raw_metadata
```

Výsledek:

- [ ] existuje interní model dokumentu,
- [ ] ingest vrstva vrací tento model,
- [ ] load vrstva tento model umí uložit,
- [ ] transform vrstva ho umí obohatit.

---

### 3.2 Definovat model datového zdroje

Model by měl obsahovat:

```text
name
source_type
source_platform
base_url
config
is_active
```

Výsledek:

- [ ] existuje model zdroje,
- [ ] odpovídá tabulce `data_sources`,
- [ ] lze podle něj vytvořit první zdroj.

---

### 3.3 Definovat model entity

Model by měl obsahovat:

```text
entity_name
normalized_name
entity_type
aliases
is_tracked
```

Výsledek:

- [ ] existuje model entity,
- [ ] existuje model aliasu,
- [ ] model podporuje sledované i extrahované entity.

---

## Fáze 4: První datový zdroj

### 4.1 Začít nejjednodušším zdrojem

Doporučení:

Začít s RSS nebo jednoduchým veřejným zpravodajským zdrojem.

Nezačínat hned složitou sociální sítí, protože sociální platformy mají:

- API limity,
- právní omezení,
- nestabilní struktury,
- často problematickou dostupnost dat.

Výsledek:

- [ ] vybraný první zdroj,
- [ ] zdroj je veřejný,
- [ ] je technicky jednoduchý,
- [ ] má známé podmínky použití,
- [ ] je zapsaný v `docs/data_sources.md`.

---

### 4.2 Přidat zdroj do tabulky `data_sources`

Vložit první zdroj ručně nebo přes seed skript.

Příklad:

```text
name: Example RSS Source
source_type: rss
source_platform: rss
base_url: https://example.com/rss
config: {}
is_active: true
```

Výsledek:

- [ ] první zdroj je v databázi,
- [ ] je aktivní,
- [ ] pipeline ho umí načíst.

---

### 4.3 Implementovat ingest modul

Vytvořit například:

```text
src/ingest/rss_ingest.py
```

Odpovědnosti:

- načíst RSS feed,
- získat položky,
- převést položky na interní model,
- vrátit seznam dokumentů,
- nelogovat citlivá data,
- neukládat přímo do databáze.

Výsledek:

- [ ] ingest stáhne data,
- [ ] ingest vrací interní modely,
- [ ] ingest má test s ukázkovým RSS vstupem,
- [ ] chyby zdroje jsou ošetřené.

---

## Fáze 5: Normalizace a deduplikace

### 5.1 Normalizovat URL

Vytvořit například:

```text
src/transform/url_normalizer.py
```

Normalizace může řešit:

- odstranění tracking parametrů,
- sjednocení trailing slash,
- lowercase hostu,
- odstranění fragmentů,
- canonical URL.

Výsledek:

- [ ] stejná URL se neukládá vícekrát kvůli UTM parametrům,
- [ ] existují testy pro běžné varianty URL,
- [ ] canonical URL se ukládá do databáze.

---

### 5.2 Vytvořit hash obsahu

Vytvořit například:

```text
src/transform/content_hash.py
```

Hash by měl vznikat z normalizovaného textu.

Výsledek:

- [ ] stejný obsah má stejný hash,
- [ ] hash se ukládá do `content_hash`,
- [ ] duplicity lze odhalit i bez `external_id`.

---

### 5.3 Vyčistit text

Vytvořit například:

```text
src/transform/text_cleaning.py
```

Čištění může řešit:

- nadbytečné mezery,
- HTML entity,
- prázdné řádky,
- boilerplate texty,
- extrémně krátký obsah.

Výsledek:

- [ ] texty jsou ukládány v rozumné podobě,
- [ ] prázdné a nevalidní záznamy jsou ignorované,
- [ ] existují testy pro čištění textu.

---

## Fáze 6: Ukládání dokumentů

### 6.1 Implementovat `collection_runs`

Při každém spuštění ingest pipeline vytvořit záznam v `collection_runs`.

Tok:

```text
create collection_run(status='running')
run ingest
store documents
update counts
finish collection_run(status='success' or 'error')
```

Výsledek:

- [ ] každý běh pipeline je auditovatelný,
- [ ] počet stažených záznamů se ukládá,
- [ ] počet vložených záznamů se ukládá,
- [ ] počet duplicit se ukládá,
- [ ] chyby se ukládají.

---

### 6.2 Implementovat upsert do `raw_social_data`

Vytvořit například:

```text
src/load/documents.py
```

Požadavky:

- ukládat dokumenty,
- respektovat deduplikační indexy,
- nepádat při duplicitě,
- vracet statistiky vložení.

Výsledek:

- [ ] dokument lze uložit,
- [ ] duplicita se neuloží dvakrát,
- [ ] chyba se zapíše do logu nebo `processing_events`,
- [ ] existuje test nebo smoke test ukládání.

---

### 6.3 Přidat `processing_events`

Logovat důležité události:

- start ingestu,
- konec ingestu,
- chyba zdroje,
- chyba transformace,
- chyba databáze,
- ignorovaný záznam,
- duplicita.

Výsledek:

- [ ] pipeline má auditní stopu,
- [ ] chyby lze dohledat v databázi,
- [ ] debugging není závislý pouze na konzolových logách.

---

## Fáze 7: Entity model a základní matching

### 7.1 Přidat ručně sledované entity

Nejdřív nepoužívat složité NLP.

Začít ručně definovanými entitami:

```text
OpenAI
ChatGPT
Microsoft
Google
Škoda Auto
```

Výsledek:

- [ ] entity jsou uložené v tabulce `entities`,
- [ ] mají `normalized_name`,
- [ ] sledované entity mají `is_tracked = true`,
- [ ] dokumentace v `docs/entities.md` odpovídá implementaci.

---

### 7.2 Přidat aliasy

Příklad:

```text
OpenAI -> Open AI, ChatGPT, GPT
Škoda Auto -> Skoda Auto, Škoda, Škodovka, Skodovka
```

Výsledek:

- [ ] aliasy jsou v `entity_aliases`,
- [ ] alias matching funguje,
- [ ] normalizace řeší diakritiku,
- [ ] existují testy pro alias matching.

---

### 7.3 Implementovat jednoduchý entity matcher

Vytvořit například:

```text
src/transform/entity_matching.py
```

První verze:

- exact match,
- normalized match,
- alias match.

Pozdější verze:

- regex,
- NER model,
- LLM extrakce.

Výsledek:

- [ ] dokument se spáruje s entitou,
- [ ] vazba se uloží do `document_entities`,
- [ ] ukládá se `matched_text`,
- [ ] ukládá se `occurrence_count`,
- [ ] ukládá se `detection_method`.

---

## Fáze 8: Základní NLP vrstva

### 8.1 Detekce jazyka

Implementovat detekci jazyka pro každý dokument.

Výsledek:

- [ ] `language_code` se ukládá,
- [ ] neznámý jazyk je ošetřený,
- [ ] jazyk lze použít pro výběr dalších modelů.

---

### 8.2 Jednoduchý sentiment

Začít jednoduše.

Možnosti:

- pravidlový baseline,
- levný LLM prompt,
- lokální model,
- externí API.

Výsledek:

- [ ] dokument má `sentiment_score`,
- [ ] sentiment je v rozsahu `-1.0 až 1.0`,
- [ ] chyba sentimentu nezastaví celou pipeline,
- [ ] výsledek je uložený do databáze.

---

### 8.3 Entity-level sentiment

Po dokumentovém sentimentu přidat sentiment vůči konkrétní entitě.

Výsledek:

- [ ] `document_entities.sentiment_score` se plní,
- [ ] sentiment entity může být jiný než sentiment celého dokumentu,
- [ ] existuje jasná fallback strategie.

---

### 8.4 Embeddingy

Vytvořit například:

```text
src/transform/embeddings.py
```

Požadavky:

- nevytvářet embedding pro prázdný text,
- batchovat požadavky,
- ošetřit rate limits,
- ukládat embedding do `raw_social_data.embedding`,
- logovat chyby bezpečně.

Výsledek:

- [ ] dokument má embedding,
- [ ] embedding má správnou dimenzi,
- [ ] lze spustit sémantický dotaz,
- [ ] chyba OpenAI API nezničí celý běh.

---

## Fáze 9: První analytická vrstva

### 9.1 Vytvořit agregaci zmínek podle entity

Vytvořit například:

```text
src/analyze/entity_mentions.py
```

Agregace:

- počet zmínek za den,
- počet zmínek za hodinu,
- průměrný sentiment,
- počet negativních zmínek,
- počet zdrojů.

Výsledek:

- [ ] lze zjistit počet zmínek entity v čase,
- [ ] lze zobrazit jednoduchou časovou řadu,
- [ ] dotazy jsou omezené na tenant_id.

---

### 9.2 Plnit `trend_snapshots`

Začít denním a hodinovým oknem.

První verze:

```text
window_granularity = 'hour'
window_granularity = 'day'
```

Výsledek:

- [ ] `trend_snapshots` se plní,
- [ ] pro každou sledovanou entitu vzniká časový snímek,
- [ ] ukládá se `mention_count`,
- [ ] ukládá se `negative_count`,
- [ ] ukládá se `avg_sentiment_score`.

---

### 9.3 Přidat jednoduchý trend score

První verze může být pravidlová.

Příklad:

```text
trend_score = aktuální počet zmínek / historický baseline
```

Potom normalizovat do rozsahu `0.0 až 1.0`.

Výsledek:

- [ ] entity mají trend score,
- [ ] trend score reaguje na nárůst zmínek,
- [ ] trend score není pouze absolutní počet zmínek,
- [ ] malé entity nejsou automaticky znevýhodněné.

---

### 9.4 Přidat jednoduchý anomaly score

První verze:

- porovnání proti průměru za posledních 7 dní,
- porovnání proti průměru za posledních 30 dní,
- jednoduchý z-score nebo poměr vůči baseline.

Výsledek:

- [ ] systém pozná náhlý nárůst,
- [ ] anomaly score se ukládá,
- [ ] výpočet je zdokumentovaný v `docs/trend_detection.md`.

---

## Fáze 10: Alerting

### 10.1 Definovat první alert pravidla

Začít s jednoduchými pravidly:

```text
mention_spike
negative_sentiment_spike
risk_score_spike
new_topic
```

První pravidlo může být:

```text
Pokud mention_count za poslední hodinu překročí 3x běžný hodinový baseline, vytvoř alert.
```

Výsledek:

- [ ] existuje první alert rule,
- [ ] alert se uloží do tabulky `alerts`,
- [ ] alert má severity,
- [ ] alert má status `open`,
- [ ] alert je navázaný na entitu nebo téma.

---

### 10.2 Deduplikace alertů

Cíl:

Nespamovat zákazníka deseti alerty pro stejný problém.

Pravidlo:

- pokud existuje otevřený alert pro stejnou entitu a stejný typ, aktualizovat ho,
- nevytvářet nový alert pokaždé.

Výsledek:

- [ ] opakovaný problém aktualizuje existující alert,
- [ ] `last_updated_at` se mění,
- [ ] `alert_payload` se doplňuje,
- [ ] alerting nespamuje.

---

### 10.3 Připravit výstup alertů

Nejdřív stačí konzole nebo databáze.

Potom:

- e-mail,
- Slack,
- Teams,
- webhook.

Výsledek první verze:

- [ ] alerty jsou dohledatelné v databázi,
- [ ] existuje jednoduchý výpis otevřených alertů,
- [ ] alert obsahuje srozumitelný popis.

---

## Fáze 11: CLI nebo jednoduché interní API

### 11.1 Přidat jednoduché příkazy pro lokální práci

Možné příkazy:

```powershell
uv run python src/main.py ingest
uv run python src/main.py analyze
uv run python src/main.py alerts
uv run python src/main.py full-run
```

Výsledek:

- [ ] lze spustit pouze ingest,
- [ ] lze spustit pouze analýzu,
- [ ] lze spustit alerting,
- [ ] lze spustit celý tok.

---

### 11.2 Připravit API až později

API není nutné pro první datové MVP.

API začít řešit až po tom, co funguje:

- databáze,
- ingest,
- transformace,
- entity matching,
- trend snapshots,
- alerty.

Výsledek:

- [ ] API se nezačne stavět předčasně,
- [ ] nejdřív existuje funkční datové jádro.

---

## Fáze 12: Testování

### 12.1 Unit testy pro transformace

Testovat hlavně:

- URL normalizaci,
- čištění textu,
- content hash,
- normalizaci názvů entit,
- alias matching,
- výpočet trend score.

Výsledek:

- [ ] transformace mají unit testy,
- [ ] testy běží přes `uv run pytest`,
- [ ] kritické části nejsou testované pouze ručně.

---

### 12.2 Testovací fixtures

Vytvořit:

```text
tests/fixtures/rss_sample.xml
tests/fixtures/raw_documents.json
tests/fixtures/entities.json
```

Výsledek:

- [ ] testy nepoužívají živý externí zdroj,
- [ ] testy jsou deterministické,
- [ ] lze testovat pipeline offline.

---

### 12.3 Integrační test pipeline

Cíl:

Spustit zjednodušenou pipeline nad fixture daty.

Tok:

```text
fixture source
→ ingest parser
→ transform
→ entity matching
→ fake load or test DB
```

Výsledek:

- [ ] pipeline funguje jako celek,
- [ ] chyby ve vazbách mezi moduly se objeví v testech,
- [ ] základní MVP je možné ověřit jedním příkazem.

---

## Fáze 13: Deployment

### 13.1 Připravit Railway pro lehké joby

Použití:

- cron,
- webhooky,
- jednoduché API,
- lehký worker.

Výsledek:

- [ ] Railway projekt existuje,
- [ ] env vars jsou nastavené v Railway,
- [ ] aplikace se deployne,
- [ ] logy jsou čitelné,
- [ ] secrets nejsou v repozitáři.

---

### 13.2 Připravit Modal pro těžší úlohy

Použití:

- embeddingy,
- dávkové LLM zpracování,
- větší NLP joby.

Výsledek:

- [ ] Modal projekt existuje,
- [ ] secrets jsou nastavené v Modal,
- [ ] jeden jednoduchý job se spustí,
- [ ] náklady jsou kontrolované.

---

### 13.3 Nastavit prostředí

Používat prostředí:

```text
local
staging
production
```

Výsledek:

- [ ] každé prostředí má vlastní konfiguraci,
- [ ] produkční secrets nejsou lokálně v repozitáři,
- [ ] staging lze použít pro testování před produkcí.

---

## Fáze 14: Bezpečnost a compliance

### 14.1 Service role key pouze na serveru

Ověřit:

- není ve frontendu,
- není v logu,
- není v repozitáři,
- není v dokumentaci s reálnou hodnotou.

Výsledek:

- [ ] service role key je pouze v serverovém prostředí,
- [ ] veřejný klient ho nikdy nepoužívá.

---

### 14.2 Připravit RLS policies

RLS policies řešit před tím, než bude existovat frontend nebo přístup zákazníků.

Minimální princip:

```text
Uživatel smí číst pouze data tenantů, kde je členem.
```

Výsledek:

- [ ] RLS je zapnuté,
- [ ] policies jsou otestované,
- [ ] uživatel nevidí data jiného tenanta,
- [ ] role mají jasné možnosti.

---

### 14.3 Pravidla pro externí zdroje

Před přidáním každého zdroje ověřit:

- technickou dostupnost,
- API limity,
- podmínky použití,
- zda jde o veřejná data,
- zda je možné data ukládat,
- zda není nutná licence.

Výsledek:

- [ ] každý zdroj má záznam v `docs/data_sources.md`,
- [ ] každý zdroj má poznámku k právním omezením,
- [ ] neobcházejí se přístupy k neveřejným datům.

---

## Fáze 15: První MVP scénář

### 15.1 Definovat MVP use case

Doporučený první use case:

```text
Systém jednou za čas stáhne články z jednoho RSS zdroje, uloží je, najde v nich sledované entity, spočítá počet zmínek a vytvoří alert, pokud zmínky výrazně vzrostou.
```

Výsledek:

- [ ] MVP má jasný cíl,
- [ ] není příliš široké,
- [ ] lze ho předvést,
- [ ] lze ho otestovat.

---

### 15.2 MVP checklist

MVP je hotové, když platí:

- [ ] existuje Supabase databáze,
- [ ] existuje minimální schéma,
- [ ] existuje jeden tenant,
- [ ] existuje jeden data source,
- [ ] ingest stáhne data,
- [ ] data se normalizují,
- [ ] duplicity se neukládají,
- [ ] dokumenty se uloží do `raw_social_data`,
- [ ] existují sledované entity,
- [ ] entity matching funguje,
- [ ] vazby se uloží do `document_entities`,
- [ ] vznikne základní agregace,
- [ ] vznikne `trend_snapshot`,
- [ ] vznikne alert při překročení pravidla,
- [ ] vše lze spustit jedním příkazem,
- [ ] základní tok je zdokumentovaný.

---

## Fáze 16: Po MVP

### 16.1 Přidat další zdroje

Po funkčním MVP přidávat zdroje postupně.

Doporučené pořadí:

1. další RSS zdroje,
2. zpravodajské weby,
3. Apify actor,
4. YouTube nebo jiná platforma s dostupným API,
5. další sociální signály podle právní dostupnosti.

Výsledek:

- [ ] každý nový zdroj má vlastní dokumentaci,
- [ ] každý nový zdroj má test,
- [ ] každý nový zdroj má jasnou mapovací logiku.

---

### 16.2 Přidat lepší NLP

Postupně přidat:

- lepší sentiment,
- entity-level sentiment,
- topic clustering,
- similarity search,
- toxicitu,
- risk classification,
- LLM shrnutí trendů.

Výsledek:

- [ ] NLP vrstva je rozšiřitelná,
- [ ] modely jsou verzované,
- [ ] výsledky jsou auditovatelné.

---

### 16.3 Přidat dashboard

Dashboard řešit až ve chvíli, kdy existují data.

První dashboard by měl ukazovat:

- počet zmínek v čase,
- top entity,
- sentiment,
- otevřené alerty,
- nejrizikovější dokumenty,
- zdroje zmínek.

Výsledek:

- [ ] dashboard čte existující agregovaná data,
- [ ] nedělá těžké výpočty na klientovi,
- [ ] respektuje tenant izolaci.

---

### 16.4 Přidat reporty

První report:

```text
Denní souhrn pro tenant_id
```

Obsah:

- top zmínky,
- nové alerty,
- nejvíce rostoucí entity,
- negativní témata,
- doporučení ke kontrole.

Výsledek:

- [ ] report lze vygenerovat ručně,
- [ ] report lze později posílat e-mailem,
- [ ] report je stručný a použitelný.

---

## Doporučené pořadí práce v nejbližších dnech

### Den 1: Repo a konfigurace

- [ ] upravit README,
- [ ] vložit dokumentaci do `docs/`,
- [ ] vytvořit `.env.example`,
- [ ] zkontrolovat `.gitignore`,
- [ ] zkontrolovat `src/config.py`,
- [ ] zprovoznit logging,
- [ ] ověřit `uv sync`, `ruff`, `pytest`.

---

### Den 2: Databáze

- [ ] založit Supabase projekt,
- [ ] zapnout `pgcrypto`,
- [ ] zapnout `vector`,
- [ ] aplikovat minimální DDL,
- [ ] vytvořit testovací tenant,
- [ ] vytvořit databázového klienta,
- [ ] ověřit připojení z lokální aplikace.

---

### Den 3: První zdroj

- [ ] vybrat první jednoduchý RSS zdroj,
- [ ] zapsat ho do `docs/data_sources.md`,
- [ ] vložit ho do `data_sources`,
- [ ] implementovat RSS ingest,
- [ ] vytvořit fixture test,
- [ ] převést RSS položky na interní dokumenty.

---

### Den 4: Transformace

- [ ] normalizovat URL,
- [ ] čistit text,
- [ ] vytvořit content hash,
- [ ] doplnit language code,
- [ ] připravit dokumenty pro uložení,
- [ ] otestovat deduplikaci.

---

### Den 5: Load pipeline

- [ ] vytvořit `collection_run`,
- [ ] ukládat dokumenty do `raw_social_data`,
- [ ] řešit duplicity,
- [ ] zapisovat `processing_events`,
- [ ] vytvořit první end-to-end běh.

---

### Den 6: Entity

- [ ] vložit první sledované entity,
- [ ] přidat aliasy,
- [ ] implementovat entity matching,
- [ ] ukládat `document_entities`,
- [ ] otestovat entity matching na reálných textech.

---

### Den 7: Analýza a první alert

- [ ] spočítat zmínky podle entity,
- [ ] vytvořit první `trend_snapshot`,
- [ ] přidat jednoduchý trend score,
- [ ] vytvořit první alert rule,
- [ ] uložit alert do tabulky `alerts`,
- [ ] připravit jednoduchý výpis otevřených alertů.

---

## Technický dluh, který neodkládat příliš dlouho

- [ ] testy pro každou transformační funkci,
- [ ] dokumentace každého datového zdroje,
- [ ] jasná pravidla pro retry,
- [ ] jasná pravidla pro deduplikaci,
- [ ] RLS před frontendem,
- [ ] audit secrets,
- [ ] monitoring nákladů OpenAI/Apify/Modal,
- [ ] jednoduché metriky úspěšnosti pipeline,
- [ ] zálohy databáze,
- [ ] changelog databázových změn.

---

## Co zatím nedělat

V první fázi nedělat:

- složitý frontend,
- billing,
- kompletní SaaS administraci,
- moc datových zdrojů najednou,
- pokročilé mapování šíření,
- složité grafové algoritmy,
- perfektní sentiment model,
- automatické LLM reporty pro vše,
- drahé realtime zpracování,
- sociální platformy bez jasného legálního přístupu.

Důvod:

Nejdřív musí vzniknout stabilní datové jádro. Bez něj budou dashboardy, alerty i analýzy nespolehlivé.

---

## První skutečný milník

První skutečný milník projektu:

```text
Jedním příkazem spustím pipeline, která stáhne veřejná data z jednoho zdroje, uloží je do databáze, najde sledované entity, vytvoří trendový snapshot a případně založí alert.
```

Ověřovací příkaz může být například:

```powershell
uv run python src/main.py full-run
```

Úspěšný výstup:

```text
collection_run: success
fetched_count: 25
inserted_count: 18
duplicate_count: 7
entities_matched: 12
trend_snapshots_created: 5
alerts_created: 1
```

Jakmile tento tok funguje, projekt má skutečný technický základ pro další rozvoj.
