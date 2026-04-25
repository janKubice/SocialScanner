# SocialScanner TODO

Cíl: postavit systém tak, aby od začátku běžel automatizovaně bez ručního spouštění pipeline. Lokální prostředí slouží pouze pro vývoj a debug. Produkční běh musí být řízen přes Railway / Modal / Supabase / plánované úlohy / fronty / automatické reporty.

---

## 0. Základní pravidla projektu

- [ ] Neprovozovat produkční pipeline ručně z lokálního počítače.
- [ ] Všechny produkční secrets držet pouze v Railway / Modal / Supabase secrets.
- [ ] Každý krok pipeline musí být idempotentní.
- [ ] Každý job musí ukládat stav běhu do databáze.
- [ ] Každý job musí mít logování, error handling a retry strategii.
- [ ] Každý externí zdroj musí mít vlastní konfiguraci v databázi.
- [ ] Žádný token, API klíč ani service role key nesmí být v repozitáři.
- [ ] Každá část systému musí jít znovu spustit bez rozbití dat.
- [ ] Dashboard a reporty mají číst pouze uložená data, nevolat drahé API přímo.
- [ ] LLM volání používat jen tam, kde levnější pravidla nestačí.

---

## 1. Repozitář a základní struktura

- [ ] Sjednotit strukturu projektu.

```text
src/
├── analyze/
├── config.py
├── ingest/
├── jobs/
├── load/
├── reports/
├── transform/
├── utils/
└── main.py
```

- [ ] Přidat adresář `src/jobs/` pro produkční spouštěcí skripty.
- [ ] Přidat adresář `src/reports/` pro generování denních a týdenních reportů.
- [ ] Přidat adresář `migrations/` nebo jasně určit, kde budou SQL migrace.
- [ ] Přidat `.env.example` bez skutečných hodnot.
- [ ] Přidat `.gitignore` pro `.env`, `.venv`, lokální výstupy, cache a logy.
- [ ] Ověřit, že `uv sync` funguje na čistém repozitáři.
- [ ] Ověřit, že `uv run ruff check . --fix` projde bez chyb.
- [ ] Ověřit, že `uv run ruff format .` projde bez chyb.
- [ ] Ověřit, že `uv run pytest` projde i při prázdném/minimálním testovacím základu.

---

## 2. Konfigurace aplikace

- [ ] Upravit `src/config.py` tak, aby četl konfiguraci přes Pydantic settings.
- [ ] Používat uppercase názvy environment variables.

```text
ENVIRONMENT=local|staging|production
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_ANON_KEY=
OPENAI_API_KEY=
APIFY_TOKEN=
DATABASE_URL=
LOG_LEVEL=INFO
PIPELINE_BATCH_SIZE=100
DEFAULT_LANGUAGE=cs
```

- [ ] Přidat validaci povinných proměnných.
- [ ] Přidat rozlišení `local`, `staging`, `production`.
- [ ] Přidat bezpečné maskování secrets v logu.
- [ ] Přidat testy pro načítání konfigurace.

Definition of done:

- [ ] Aplikace spadne s jasnou chybou, pokud chybí povinný secret.
- [ ] Produkční secrets se nikdy nevypisují do logu.
- [ ] Lokální `.env` není potřeba v produkci.

---

## 3. Databáze a migrace

- [ ] Vytvořit finální SQL migraci podle `docs/database.md`.
- [ ] Zapnout potřebná PostgreSQL rozšíření.

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;
```

- [ ] Vytvořit tabulky:
  - [ ] `tenants`
  - [ ] `tenant_members`
  - [ ] `data_sources`
  - [ ] `collection_runs`
  - [ ] `raw_social_data`
  - [ ] `entities`
  - [ ] `entity_aliases`
  - [ ] `document_entities`
  - [ ] `topics`
  - [ ] `document_topics`
  - [ ] `document_relations`
  - [ ] `trend_snapshots`
  - [ ] `alerts`
  - [ ] `processing_events`

- [ ] Přidat základní indexy.
- [ ] Přidat unique indexy pro deduplikaci.
- [ ] Přidat `updated_at` trigger.
- [ ] Zapnout RLS na tabulkách.
- [ ] Přidat minimální RLS policies pro budoucí frontend.
- [ ] Připravit seed pro prvního testovacího tenanta.
- [ ] Připravit seed pro první sledované entity.

Definition of done:

- [ ] Databázi lze vytvořit z nuly jedním postupem.
- [ ] Migrace lze aplikovat opakovatelně.
- [ ] Unikátní indexy brání duplicitám.
- [ ] První tenant a entity existují bez ručního klikání v databázi.

---

## 4. Databázová access vrstva

- [ ] Vytvořit `src/load/db.py`.
- [ ] Vytvořit centrální Supabase/PostgreSQL klient.
- [ ] Vytvořit repository funkce pro:
  - [ ] tenants,
  - [ ] data sources,
  - [ ] collection runs,
  - [ ] raw social data,
  - [ ] entities,
  - [ ] document entities,
  - [ ] topics,
  - [ ] trend snapshots,
  - [ ] alerts,
  - [ ] processing events.

- [ ] Přidat helper pro `insert_collection_run_start`.
- [ ] Přidat helper pro `finish_collection_run_success`.
- [ ] Přidat helper pro `finish_collection_run_error`.
- [ ] Přidat helper pro `log_processing_event`.
- [ ] Přidat upsert pro `raw_social_data` podle `external_id`, `canonical_url` nebo `content_hash`.

Definition of done:

- [ ] Ingest modul nikdy nepracuje přímo s SQL mimo load vrstvu.
- [ ] Transform modul nikdy nezapisuje přímo do DB mimo load vrstvu.
- [ ] Každý produkční job umí zapsat svůj stav do databáze.

---

## 5. Logging a observability

- [ ] Vytvořit `src/utils/logging.py`.
- [ ] Nastavit strukturované logování.
- [ ] Každý log musí obsahovat:
  - [ ] environment,
  - [ ] job name,
  - [ ] tenant id, pokud existuje,
  - [ ] source id, pokud existuje,
  - [ ] collection run id, pokud existuje.

- [ ] Přidat logování startu a konce každého jobu.
- [ ] Přidat logování počtu zpracovaných záznamů.
- [ ] Přidat logování chyb bez secrets.
- [ ] Přidat tabulkové logování do `processing_events`.
- [ ] Přidat health check endpoint nebo health check job.

Definition of done:

- [ ] Z logů lze zjistit, co běželo, kdy to běželo a proč to spadlo.
- [ ] Kritická chyba se uloží do databáze.
- [ ] Secrets nejsou v logu.

---

## 6. Railway základ

- [ ] Vytvořit Railway projekt pro `staging`.
- [ ] Vytvořit Railway projekt nebo prostředí pro `production`.
- [ ] Napojit Railway na GitHub repozitář.
- [ ] Nastavit automatický deployment po pushi do hlavní větve nebo deployment větve.
- [ ] Přidat Railway variables:
  - [ ] `ENVIRONMENT`
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_SERVICE_ROLE_KEY`
  - [ ] `OPENAI_API_KEY`
  - [ ] `APIFY_TOKEN`
  - [ ] `LOG_LEVEL`
  - [ ] `PIPELINE_BATCH_SIZE`

- [ ] Přidat Railway build/start command.
- [ ] Přidat jednoduchý health command.
- [ ] Ověřit, že Railway umí spustit `uv run python src/main.py`.
- [ ] Přidat samostatné Railway služby nebo joby pro plánované úlohy.

Definition of done:

- [ ] Po pushi se aplikace sama deployne.
- [ ] Produkční běh nevyžaduje lokální počítač.
- [ ] Secrets jsou pouze v Railway variables.

---

## 7. Produkční job entrypointy

Vytvořit samostatné skripty v `src/jobs/`.

- [ ] `src/jobs/health_check.py`
- [ ] `src/jobs/ingest_sources.py`
- [ ] `src/jobs/process_pending_documents.py`
- [ ] `src/jobs/extract_entities.py`
- [ ] `src/jobs/generate_embeddings.py`
- [ ] `src/jobs/analyze_trends.py`
- [ ] `src/jobs/generate_alerts.py`
- [ ] `src/jobs/send_daily_reports.py`
- [ ] `src/jobs/cleanup_old_data.py`

Každý job musí mít:

- [ ] jasný `main()` entrypoint,
- [ ] načtení configu,
- [ ] strukturované logování,
- [ ] zápis startu běhu,
- [ ] zápis výsledku běhu,
- [ ] error handling,
- [ ] bezpečné ukončení při chybě,
- [ ] idempotentní chování.

Definition of done:

- [ ] Každý job lze spustit samostatně přes `uv run python -m src.jobs.<job_name>`.
- [ ] Každý job lze později naplánovat v Railway nebo Modal.
- [ ] Žádný job nevyžaduje ruční zásah.

---

## 8. Railway cron / scheduled jobs

Nastavit plánované úlohy od začátku.

Doporučený první plán:

```text
health_check.py                 každých 15 minut
ingest_sources.py               každou hodinu
process_pending_documents.py    každých 10 minut
extract_entities.py             každých 15 minut
generate_embeddings.py          každých 30 minut
analyze_trends.py               každou hodinu
generate_alerts.py              každých 15 minut
send_daily_reports.py           každý den ráno
cleanup_old_data.py             jednou týdně
```

- [ ] Přidat cron pro health check.
- [ ] Přidat cron pro ingest.
- [ ] Přidat cron pro processing pending dokumentů.
- [ ] Přidat cron pro entity extraction.
- [ ] Přidat cron pro embeddings.
- [ ] Přidat cron pro trend analysis.
- [ ] Přidat cron pro alerting.
- [ ] Přidat cron pro denní report.
- [ ] Přidat cron pro cleanup.

Definition of done:

- [ ] Po nasazení systém běží sám.
- [ ] Data se sbírají bez lokálního spuštění.
- [ ] Pending dokumenty se samy zpracovávají.
- [ ] Trendy a alerty vznikají automaticky.
- [ ] Denní report se vytvoří automaticky.

---

## 9. Data sources základ

Nejdřív vytvořit univerzální framework, i když konkrétní zdroje ještě nejsou finální.

- [ ] Vytvořit `src/ingest/base.py`.
- [ ] Definovat abstraktní rozhraní pro ingest source.

```text
fetch_items(source_config) -> list[RawItem]
normalize_item(raw_item) -> NormalizedDocument
```

- [ ] Vytvořit datový model `RawItem`.
- [ ] Vytvořit datový model `NormalizedDocument`.
- [ ] Přidat validaci povinných polí:
  - [ ] source platform,
  - [ ] source URL nebo external ID,
  - [ ] content nebo title,
  - [ ] published_at, pokud existuje.

- [ ] Vytvořit obecný RSS ingest modul.
- [ ] Vytvořit obecný Apify ingest modul.
- [ ] Vytvořit ruční/mock ingest modul pro testování.
- [ ] Připravit data source template v databázi.

Definition of done:

- [ ] Nový zdroj lze přidat konfigurací v DB.
- [ ] Ingest job načte aktivní zdroje z DB.
- [ ] Ingest job stáhne data a uloží nové záznamy.
- [ ] Duplicity se neukládají opakovaně.

---

## 10. První automatizovaný ingest

Cíl: mít první reálně běžící automatický sběr.

- [ ] Přidat první testovací RSS zdroj.
- [ ] Přidat druhý testovací RSS zdroj.
- [ ] Přidat třetí testovací RSS zdroj.
- [ ] Ověřit, že `ingest_sources.py` načte zdroje z DB.
- [ ] Ověřit, že každý běh vytvoří `collection_runs` záznam.
- [ ] Ověřit, že nové články se uloží do `raw_social_data`.
- [ ] Ověřit, že duplicity se započítají jako duplicity.
- [ ] Ověřit, že chyba jednoho zdroje neshodí celý ingest všech zdrojů.
- [ ] Ověřit, že Railway cron spouští ingest bez ručního zásahu.

Definition of done:

- [ ] Každou hodinu se automaticky zkontrolují zdroje.
- [ ] Nové záznamy se uloží.
- [ ] Duplicity se neukládají znovu.
- [ ] Stav běhu je vidět v databázi.

---

## 11. Deduplikace

- [ ] Vytvořit `src/transform/deduplication.py`.
- [ ] Normalizovat URL do `canonical_url`.
- [ ] Vytvořit `content_hash` z normalizovaného obsahu.
- [ ] Deduplikovat podle:
  - [ ] `external_id`, pokud existuje,
  - [ ] `canonical_url`, pokud existuje,
  - [ ] `content_hash`, pokud existuje.

- [ ] Označovat duplicitní záznamy jako `duplicate`, pokud se mají uchovat.
- [ ] Nebo neukládat duplicitní záznamy, pokud nejsou potřeba.
- [ ] Logovat počet duplicit do `collection_runs.duplicate_count`.

Definition of done:

- [ ] Opakované spuštění ingestu nevytváří duplicitní data.
- [ ] Stejný článek z RSS se neukládá vícekrát.
- [ ] Deduplikace funguje bez ruční kontroly.

---

## 12. Základní transformace dokumentů

- [ ] Vytvořit `src/transform/normalize_text.py`.
- [ ] Čistit HTML.
- [ ] Normalizovat whitespace.
- [ ] Odstraňovat prázdné a příliš krátké dokumenty.
- [ ] Detekovat jazyk.
- [ ] Ukládat `language_code`.
- [ ] Nastavit `processing_status`.
- [ ] Zpracovat pouze dokumenty ve stavu `pending`.
- [ ] Po úspěchu nastavit `processing_status = processed` nebo další mezistav.
- [ ] Po chybě nastavit `processing_status = error`.

Definition of done:

- [ ] Nové dokumenty se automaticky čistí.
- [ ] Dokumenty mají jazyk.
- [ ] Chybné dokumenty neblokují pipeline.

---

## 13. Entity monitoring

- [ ] Vytvořit první sledované entity v DB.
- [ ] Ke každé entitě přidat aliasy.
- [ ] Vytvořit `src/transform/entity_matching.py`.
- [ ] Implementovat exact match.
- [ ] Implementovat normalized match bez diakritiky.
- [ ] Implementovat alias match.
- [ ] Implementovat jednoduchý regex match pro hashtagy.
- [ ] Ukládat výsledky do `document_entities`.
- [ ] Ukládat `occurrence_count`.
- [ ] Ukládat `matched_text`.
- [ ] Ukládat `context_snippet`.
- [ ] Ukládat `detection_method`.

Definition of done:

- [ ] Systém automaticky najde zmínky sledovaných entit.
- [ ] Každý dokument ví, jaké entity obsahuje.
- [ ] Entity matching běží v plánovaném jobu.

---

## 14. Sentiment a risk scoring MVP

Nejdřív jednoduchá a levná verze.

- [ ] Vytvořit `src/transform/sentiment.py`.
- [ ] Vytvořit `src/transform/risk_scoring.py`.
- [ ] Implementovat jednoduchá pravidla pro negativní slova.
- [ ] Implementovat základní sentiment score v rozsahu `-1` až `1`.
- [ ] Implementovat základní risk score v rozsahu `0` až `1`.
- [ ] Skórovat pouze dokumenty, které obsahují sledovanou entitu.
- [ ] Ukládat skóre na úrovni dokumentu.
- [ ] Ukládat skóre na úrovni `document_entities`.
- [ ] Přidat LLM klasifikaci pouze pro kandidáty s vyšším rizikem.
- [ ] Ukládat použitý model a metadata klasifikace do `processing_metadata`.

Definition of done:

- [ ] Systém umí rozlišit neutrální a rizikovější zmínky.
- [ ] LLM se nevolá na všechny dokumenty.
- [ ] Náklady jsou kontrolované.

---

## 15. Embeddingy

- [ ] Vytvořit `src/transform/embeddings.py`.
- [ ] Generovat embeddingy pouze pro relevantní dokumenty.
- [ ] Dávkovat dokumenty po rozumných dávkách.
- [ ] Ukládat embedding do `raw_social_data.embedding`.
- [ ] Zamezit opakovanému generování embeddingu pro stejný dokument.
- [ ] Přidat retry při chybě API.
- [ ] Přidat limit na počet dokumentů zpracovaných jedním během.
- [ ] Přidat monitoring nákladů přes počet zpracovaných dokumentů.

Definition of done:

- [ ] Embeddingy se generují automaticky.
- [ ] Embedding job lze spouštět přes Railway cron.
- [ ] Později lze job přesunout do Modal bez změny datového modelu.

---

## 16. Modal pro těžké úlohy

Modal použít pro dražší nebo dávkové úlohy, které nemají běžet dlouho na Railway.

- [ ] Připravit Modal projekt.
- [ ] Nastavit Modal secrets:
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_SERVICE_ROLE_KEY`
  - [ ] `OPENAI_API_KEY`

- [ ] Připravit Modal job pro batch embeddings.
- [ ] Připravit Modal job pro větší LLM klasifikace.
- [ ] Připravit Modal job pro historickou reanalýzu dokumentů.
- [ ] Připravit Modal job pro re-clustering témat.
- [ ] Omezit Modal úlohy dávkováním a limity.

Definition of done:

- [ ] Railway drží orchestraci a lehčí joby.
- [ ] Modal řeší výpočetně nebo nákladově těžší batch úlohy.
- [ ] Systém se nemusí spouštět ručně lokálně.

---

## 17. Trend snapshots MVP

- [ ] Vytvořit `src/analyze/trends.py`.
- [ ] Agregovat počet zmínek podle entity.
- [ ] Agregovat počet negativních zmínek podle entity.
- [ ] Agregovat průměrný sentiment podle entity.
- [ ] Agregovat průměrný risk score podle entity.
- [ ] Vytvářet hodinové snapshoty.
- [ ] Vytvářet denní snapshoty.
- [ ] Ukládat výsledky do `trend_snapshots`.
- [ ] Nepřepisovat historii bez důvodu.
- [ ] Přepočet stejného okna musí být idempotentní.

Definition of done:

- [ ] Trendy se počítají automaticky každou hodinu.
- [ ] Denní trendy vznikají automaticky.
- [ ] Data jsou připravena pro grafy a reporty.

---

## 18. Anomaly detection MVP

- [ ] Vypočítat baseline za posledních 7 dní.
- [ ] Vypočítat baseline za posledních 30 dní.
- [ ] Porovnat aktuální okno s baseline.
- [ ] Vypočítat `trend_score`.
- [ ] Vypočítat `anomaly_score`.
- [ ] Rozlišit běžný růst a rizikový růst.
- [ ] Více vážit negativní zmínky.
- [ ] Více vážit růst zmínek u sledovaných entit.
- [ ] Ukládat výsledek do `trend_snapshots`.

Definition of done:

- [ ] Systém pozná neobvyklý nárůst zmínek.
- [ ] Systém pozná neobvyklý nárůst negativních zmínek.
- [ ] Výsledek lze použít pro alerting.

---

## 19. Alerting MVP

- [ ] Vytvořit `src/analyze/alert_rules.py`.
- [ ] Vytvořit `src/jobs/generate_alerts.py`.
- [ ] Implementovat alert typy:
  - [ ] `mention_spike`,
  - [ ] `negative_sentiment_spike`,
  - [ ] `risk_score_spike`,
  - [ ] `new_topic`,
  - [ ] `high_engagement`.

- [ ] Implementovat severity:
  - [ ] `info`,
  - [ ] `low`,
  - [ ] `medium`,
  - [ ] `high`,
  - [ ] `critical`.

- [ ] Deduplikovat alerty.
- [ ] Aktualizovat existující otevřený alert místo vytváření nového, pokud jde o stejný problém.
- [ ] Ukládat alert payload s důvody, proč alert vznikl.
- [ ] Ukládat top dokumenty, které alert způsobily.
- [ ] Ukládat doporučený další krok.

Definition of done:

- [ ] Alerty vznikají automaticky.
- [ ] Jeden problém nevytváří desítky duplicitních alertů.
- [ ] Alert obsahuje jasný důvod vzniku.

---

## 20. Notifikace alertů

- [ ] Vytvořit `src/utils/notifications.py`.
- [ ] Přidat e-mail notifikace.
- [ ] Přidat Slack webhook notifikace.
- [ ] Přidat volitelně Teams webhook notifikace.
- [ ] Posílat pouze nové nebo významně aktualizované alerty.
- [ ] Neposílat stále stejný alert dokola.
- [ ] Ukládat čas posledního odeslání notifikace.
- [ ] Přidat fail-safe při výpadku notifikační služby.

Definition of done:

- [ ] Kritický alert přijde bez ručního zásahu.
- [ ] Systém nespamuje.
- [ ] Chyba notifikace se zaloguje a nezastaví pipeline.

---

## 21. Denní report MVP

- [ ] Vytvořit `src/reports/daily_report.py`.
- [ ] Generovat denní report pro každého tenanta.
- [ ] Report musí obsahovat:
  - [ ] sledované entity,
  - [ ] počet nových zmínek,
  - [ ] počet negativních zmínek,
  - [ ] top zdroje,
  - [ ] top dokumenty,
  - [ ] nejrizikovější dokumenty,
  - [ ] nové alerty,
  - [ ] srovnání s předchozím dnem,
  - [ ] stručné shrnutí.

- [ ] Generovat report jako Markdown.
- [ ] Později přidat HTML.
- [ ] Později přidat PDF.
- [ ] Posílat report e-mailem.
- [ ] Ukládat vygenerovaný report do databáze nebo storage.

Definition of done:

- [ ] Každý den vznikne report automaticky.
- [ ] Report lze poslat klientovi bez ručních úprav.
- [ ] Chyba u jednoho tenanta nezastaví reporty ostatních tenantů.

---

## 22. Základní administrační CLI

CLI slouží jen pro správu a debug, ne pro běžný produkční provoz.

- [ ] Přidat příkaz pro vytvoření tenanta.
- [ ] Přidat příkaz pro přidání entity.
- [ ] Přidat příkaz pro přidání aliasu.
- [ ] Přidat příkaz pro přidání data source.
- [ ] Přidat příkaz pro ruční spuštění jobu ve stagingu.
- [ ] Přidat příkaz pro kontrolu posledních collection runs.
- [ ] Přidat příkaz pro kontrolu otevřených alertů.

Definition of done:

- [ ] Základní správa systému nevyžaduje ruční SQL.
- [ ] Produkční pipeline stále běží automaticky přes cron.

---

## 23. Dashboard později, ale data připravovat hned

- [ ] Navrhnout dotazy pro přehled entit.
- [ ] Navrhnout dotazy pro seznam dokumentů.
- [ ] Navrhnout dotazy pro trend grafy.
- [ ] Navrhnout dotazy pro alerty.
- [ ] Navrhnout dotazy pro detail entity.
- [ ] Navrhnout dotazy pro detail dokumentu.
- [ ] Nezačínat komplexním dashboardem, dokud nefunguje automatická pipeline.

Definition of done:

- [ ] Databáze umí obsloužit budoucí dashboard.
- [ ] MVP není blokované frontendem.

---

## 24. Testování

- [ ] Přidat unit testy pro config.
- [ ] Přidat unit testy pro normalizaci URL.
- [ ] Přidat unit testy pro content hash.
- [ ] Přidat unit testy pro deduplikaci.
- [ ] Přidat unit testy pro entity matching.
- [ ] Přidat unit testy pro risk scoring.
- [ ] Přidat unit testy pro trend score.
- [ ] Přidat testy pro alert rules.
- [ ] Přidat testovací RSS payload.
- [ ] Přidat testovací článek bez obsahu.
- [ ] Přidat testovací duplicitní článek.
- [ ] Přidat testovací negativní zmínku.
- [ ] Přidat testovací neutrální zmínku.

Definition of done:

- [ ] Základní logika je chráněná testy.
- [ ] Před deploymentem běží lint, format a testy.

---

## 25. CI/CD

- [ ] Přidat GitHub Actions workflow.
- [ ] Workflow musí spouštět:
  - [ ] `uv sync`,
  - [ ] `uv run ruff check .`,
  - [ ] `uv run ruff format . --check`,
  - [ ] `uv run pytest`.

- [ ] Zabránit merge, pokud testy neprojdou.
- [ ] Přidat kontrolu, že v commitu nejsou secrets.
- [ ] Přidat základní secret scanning.
- [ ] Railway deployment spouštět až po úspěšném CI.

Definition of done:

- [ ] Rozbitý kód se nedostane do produkce.
- [ ] Deployment je automatický, ale kontrolovaný.

---

## 26. Fail-safe režim

- [ ] Pokud selže ingest jednoho zdroje, ostatní zdroje pokračují.
- [ ] Pokud selže LLM volání, dokument se označí jako error nebo retry candidate.
- [ ] Pokud selže embedding job, ostatní pipeline kroky pokračují.
- [ ] Pokud selže report pro jednoho tenanta, ostatní reporty pokračují.
- [ ] Pokud selže notifikace, alert zůstane uložený jako neodeslaný.
- [ ] Přidat retry count k relevantním záznamům.
- [ ] Přidat maximální počet retry pokusů.
- [ ] Přidat dead-letter stav pro opakovaně chybující záznamy.

Definition of done:

- [ ] Jedna chyba nezastaví celý systém.
- [ ] Chybové záznamy lze dohledat a později opravit.

---

## 27. Nákladová kontrola

- [ ] Nevolat OpenAI API na irelevantní dokumenty.
- [ ] Nevolat embeddingy na duplicitní dokumenty.
- [ ] Nevolat LLM na dokumenty bez sledované entity.
- [ ] Přidat denní limit LLM zpracování.
- [ ] Přidat denní limit embedding zpracování.
- [ ] Logovat počet LLM volání.
- [ ] Logovat počet embedding volání.
- [ ] Přidat jednoduchý cost report do denního interního reportu.

Definition of done:

- [ ] Náklady jsou předvídatelné.
- [ ] Chyba v pipeline nemůže nekontrolovaně spálit API kredit.

---

## 28. Bezpečnost

- [ ] Ověřit, že `.env` není v repozitáři.
- [ ] Ověřit, že service role key není použit ve frontendu.
- [ ] Ověřit, že secrets nejsou v logu.
- [ ] Omezit přístup k produkční Supabase databázi.
- [ ] Omezit přístup k Railway projektu.
- [ ] Omezit přístup k Modal projektu.
- [ ] Zapnout RLS.
- [ ] Připravit minimální policies pro budoucí frontend.
- [ ] Logovat administrativní změny tenantů, entit a zdrojů.

Definition of done:

- [ ] Produkční secrets jsou chráněné.
- [ ] Tenant data jsou oddělená.
- [ ] Veřejný klient nikdy nemá service role key.

---

## 29. Privacy a compliance základ

- [ ] Dokumentovat, jaké typy dat systém ukládá.
- [ ] Neukládat zbytečná osobní data.
- [ ] Neukládat neveřejný obsah bez oprávnění.
- [ ] U každého data source evidovat právní/technickou poznámku.
- [ ] Přidat možnost deaktivovat zdroj.
- [ ] Přidat možnost mazat data konkrétního tenanta.
- [ ] Přidat retenční pravidla pro stará data.
- [ ] Přidat cleanup job.

Definition of done:

- [ ] Je jasné, odkud data pochází.
- [ ] Je jasné, proč jsou data uložena.
- [ ] Je možné data odstranit nebo omezit jejich uchování.

---

## 30. První MVP bez dashboardu

Cíl: automatický monitoring a report bez ručního spouštění.

- [ ] Supabase databáze běží.
- [ ] Railway deployment běží.
- [ ] Railway crony běží.
- [ ] První tenant existuje.
- [ ] První entity existují.
- [ ] První aliasy existují.
- [ ] První RSS zdroje existují.
- [ ] Ingest běží každou hodinu.
- [ ] Processing běží automaticky.
- [ ] Entity matching běží automaticky.
- [ ] Sentiment/risk scoring běží automaticky.
- [ ] Trend snapshots se generují automaticky.
- [ ] Alerty vznikají automaticky.
- [ ] Denní report se generuje automaticky.
- [ ] Denní report se posílá automaticky.

Definition of done:

- [ ] Systém může běžet několik dní bez ručního zásahu.
- [ ] Po několika dnech existují data, trendy, alerty a reporty.
- [ ] Výstup lze ukázat prvnímu testovacímu zákazníkovi.

---

## 31. První pilotní výstup

- [ ] Vybrat jednu testovací značku nebo entitu.
- [ ] Sledovat ji minimálně 7 dní.
- [ ] Nasbírat data z prvních zdrojů.
- [ ] Vygenerovat denní reporty.
- [ ] Vygenerovat týdenní shrnutí.
- [ ] Ručně zkontrolovat přesnost entity matching.
- [ ] Ručně zkontrolovat sentiment/risk scoring.
- [ ] Upravit aliasy podle reálných dat.
- [ ] Upravit risk pravidla podle reálných dat.
- [ ] Připravit ukázkový report pro PR agenturu nebo klienta.

Definition of done:

- [ ] Existuje reálný ukázkový výstup.
- [ ] Výstup není jen technické demo.
- [ ] Dá se ukázat člověku mimo projekt.

---

## 32. První obchodní validace

- [ ] Připravit krátký popis služby.
- [ ] Připravit ukázkový report.
- [ ] Připravit seznam 10 PR agentur nebo potenciálních klientů.
- [ ] Oslovit první 3 kontakty.
- [ ] Zjistit, jak dnes řeší monitoring.
- [ ] Zjistit, co jim vadí na současných nástrojích.
- [ ] Zjistit, jak často potřebují reporty.
- [ ] Zjistit, jaké zdroje jsou pro ně klíčové.
- [ ] Zjistit, kolik by byli ochotni platit za pilot.
- [ ] Nabídnout omezený měsíční pilot.

Definition of done:

- [ ] Existuje reálná zpětná vazba z trhu.
- [ ] Je jasné, co doplnit před placeným pilotem.
- [ ] Projekt se nerozvíjí jen podle domněnek.

---

## 33. Verze 1.0 MVP checklist

MVP je hotové, pokud platí:

- [ ] Systém běží v produkčním prostředí.
- [ ] Systém nevyžaduje lokální ruční spouštění.
- [ ] Data sources jsou konfigurované v databázi.
- [ ] Ingest běží automaticky.
- [ ] Deduplikace funguje.
- [ ] Entity matching funguje.
- [ ] Sentiment/risk scoring funguje alespoň základně.
- [ ] Trend snapshots vznikají automaticky.
- [ ] Alerty vznikají automaticky.
- [ ] Denní report vzniká automaticky.
- [ ] Chyby se ukládají do databáze.
- [ ] Logs jsou dostupné v Railway.
- [ ] Secrets jsou mimo repozitář.
- [ ] Náklady jsou pod kontrolou.
- [ ] Existuje první ukázkový report.
- [ ] Existuje seznam známých limitací.
- [ ] Existuje plán dalšího vývoje podle feedbacku.

---

## 34. Co zatím nedělat

- [ ] Nestavět plný SaaS dashboard jako první.
- [ ] Nedělat billing.
- [ ] Nedělat veřejnou registraci.
- [ ] Nedělat mobilní aplikaci.
- [ ] Nedělat podporu všech sociálních sítí najednou.
- [ ] Nedělat složitý graph propagation engine před základním trend detection.
- [ ] Nedělat vlastní ML modely před ověřením hodnoty.
- [ ] Nedělat enterprise role systém před prvním pilotem.
- [ ] Nedělat perfektní UI před automatickými reporty.

---

## 35. Doporučené pořadí práce

1. [ ] Stabilizovat repo, config a dokumentaci.
2. [ ] Nasadit databázové schéma do Supabase.
3. [ ] Vytvořit load/repository vrstvu.
4. [ ] Připravit Railway deployment.
5. [ ] Připravit produkční job entrypointy.
6. [ ] Nastavit Railway crony.
7. [ ] Implementovat RSS ingest.
8. [ ] Implementovat deduplikaci.
9. [ ] Implementovat základní processing dokumentů.
10. [ ] Implementovat entity alias matching.
11. [ ] Implementovat základní sentiment/risk scoring.
12. [ ] Implementovat trend snapshots.
13. [ ] Implementovat alert rules.
14. [ ] Implementovat denní report.
15. [ ] Spustit systém na prvním tenantovi.
16. [ ] Nechat běžet několik dní bez zásahu.
17. [ ] Vyhodnotit kvalitu dat a skórování.
18. [ ] Připravit ukázkový report.
19. [ ] Oslovit první PR agenturu nebo testovacího klienta.
20. [ ] Rozvíjet další funkce podle reálné zpětné vazby.
