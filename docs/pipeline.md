# Data Pipeline: SocialScanner

Tento dokument popisuje datovou pipeline projektu **SocialScanner**.

Pipeline zajišťuje celý životní cyklus dat od jejich získání z externího zdroje až po analytické výstupy, alerty a reporty.

---

## Cíl pipeline

Cílem pipeline je převést surový externí obsah na strukturovaná, vyhledatelná a analyticky použitelná data.

Pipeline musí umět:

- získat data z externích zdrojů,
- zachovat původní metadata,
- normalizovat obsah,
- detekovat duplicity,
- uložit data do databáze,
- extrahovat entity,
- detekovat témata,
- počítat sentiment a riziko,
- vytvářet embeddingy,
- připravit data pro trend detection,
- spouštět alerting.

---

## Základní tok

```text
Data Source
    ↓
Collection Run
    ↓
Ingest
    ↓
Validation
    ↓
Normalization
    ↓
Deduplication
    ↓
Load Raw Document
    ↓
NLP / Enrichment
    ↓
Entity Matching
    ↓
Topic Detection
    ↓
Trend Aggregation
    ↓
Alert Evaluation
    ↓
Reports / Dashboardy
```

---

## Fáze pipeline

## 1. Collection run

Každé spuštění sběru dat začíná vytvořením záznamu v `collection_runs`.

Záznam obsahuje:

- `tenant_id`,
- `source_id`,
- `status`,
- `started_at`,
- `finished_at`,
- `fetched_count`,
- `inserted_count`,
- `duplicate_count`,
- `error_count`,
- `error_message`,
- `metadata`.

### Doporučené stavy

```text
running
success
partial_success
error
cancelled
```

### Pravidla

- Každý běh musí mít vlastní `collection_run_id`.
- I neúspěšný běh musí být uložen.
- Chyby musí být dohledatelné.
- Počet duplicit musí být měřen.
- Počet vložených záznamů musí být měřen.

---

## 2. Ingest

Ingest fáze získává data ze zdroje.

Typické zdroje:

- RSS,
- API,
- Apify,
- crawler,
- webhook,
- ruční import.

### Vstup

- konfigurace zdroje,
- tenant,
- čas spuštění,
- případné parametry.

### Výstup

Kolekce surových záznamů v co nejbližší podobě původnímu zdroji.

### Pravidla

Ingest vrstva nesmí:

- provádět hlubokou NLP analýzu,
- počítat trendy,
- vytvářet alerty,
- přímo rozhodovat o business významu záznamu.

Ingest vrstva smí:

- ověřit dostupnost zdroje,
- načíst data,
- uložit původní payload do paměti nebo předat dále,
- provést minimální technickou validaci.

---

## 3. Validace

Validace ověřuje, zda je záznam dostatečně použitelný pro další zpracování.

### Minimální povinná pole

Každý dokument by měl mít alespoň:

- `source_platform`,
- `content` nebo jiný textový obsah,
- `source_url` nebo `external_id`,
- `tenant_id`.

### Volitelná, ale doporučená pole

- `published_at`,
- `author_handle`,
- `title`,
- `metrics`,
- `raw_metadata`.

### Nevalidní záznamy

Nevalidní záznam může být:

- ignorován,
- uložen s `processing_status = 'error'`,
- zalogován do `processing_events`,
- uložen do dead-letter mechanismu v budoucí verzi.

---

## 4. Normalizace

Normalizace převádí platformně specifická data na interní strukturu.

### Normalizovaná pole

| Interní pole | Popis |
|---|---|
| `external_id` | Externí ID z platformy |
| `source_url` | Původní URL |
| `canonical_url` | Normalizovaná URL |
| `source_platform` | Platforma nebo typ zdroje |
| `content_type` | Typ obsahu |
| `published_at` | Čas publikace |
| `author_handle` | Autor |
| `title` | Titulek |
| `content` | Hlavní text |
| `language_code` | Jazyk |
| `metrics` | Metriky |
| `raw_metadata` | Původní objekt |

---

## 5. Čištění textu

Textový obsah se čistí před NLP zpracováním.

Typické kroky:

- odstranění přebytečných whitespace znaků,
- sjednocení odřádkování,
- odstranění HTML tagů,
- dekódování HTML entit,
- odstranění navigačních částí webu,
- odstranění opakujících se boilerplate textů,
- normalizace uvozovek a speciálních znaků.

### Pravidla

Čištění nesmí zničit význam textu.

Původní raw payload musí zůstat zachován v `raw_metadata`.

---

## 6. Normalizace URL

URL se normalizuje pro účely deduplikace.

Typické kroky:

- odstranění tracking parametrů,
- odstranění fragmentu,
- sjednocení trailing slash,
- převod domény na lowercase,
- případné rozbalení redirectů,
- uložení jako `canonical_url`.

### Tracking parametry

Typické parametry k odstranění:

```text
utm_source
utm_medium
utm_campaign
utm_term
utm_content
fbclid
gclid
```

---

## 7. Deduplikace

Deduplikace zabraňuje opakovanému ukládání stejného obsahu.

### Úrovně deduplikace

#### 1. Externí ID

Nejspolehlivější varianta, pokud platforma poskytuje stabilní ID.

```text
tenant_id + source_platform + external_id
```

#### 2. Canonical URL

Vhodné pro články a webový obsah.

```text
tenant_id + canonical_url
```

#### 3. Hash obsahu

Vhodné pro zdroje bez ID a bez stabilní URL.

```text
tenant_id + source_platform + content_hash
```

#### 4. Sémantická podobnost

Budoucí rozšíření pro near-duplicate detekci.

Vhodné pro:

- převzaté články,
- copy-paste příspěvky,
- mírně upravené texty,
- zrcadlený obsah.

---

## 8. Uložení dokumentu

Po validaci, normalizaci a deduplikaci se dokument uloží do `raw_social_data`.

### Výchozí stav

Nově uložený dokument by měl mít:

```text
processing_status = pending
```

Po úspěšném obohacení:

```text
processing_status = processed
```

Při chybě:

```text
processing_status = error
```

---

## 9. Detekce jazyka

Detekce jazyka slouží pro:

- výběr NLP modelu,
- filtrování dashboardů,
- výběr sentiment modelu,
- reporting,
- analytiku podle regionu.

### Výstup

```text
language_code = cs / sk / en / de / other
```

### Pravidla

- Pokud jazyk nelze určit, použít `unknown`.
- Krátké texty mohou mít nízkou spolehlivost.
- Jazyk z platformy lze použít jako pomocný signál, nikoli jako jediný zdroj pravdy.

---

## 10. Extrakce entit

Extrakce entit hledá v dokumentu relevantní objekty.

Typy entit:

- značka,
- firma,
- osoba,
- produkt,
- organizace,
- instituce,
- hashtag,
- doména,
- lokace,
- téma.

### Metody detekce

- exact match,
- alias match,
- regex,
- NER model,
- LLM,
- manual.

### Výstup

Výsledky se ukládají do:

- `entities`,
- `entity_aliases`,
- `document_entities`.

---

## 11. Sentiment analýza

Sentiment lze počítat na dvou úrovních.

### 1. Document-level sentiment

Celkový sentiment dokumentu.

Ukládá se do:

```text
raw_social_data.sentiment_score
```

### 2. Entity-level sentiment

Sentiment vůči konkrétní entitě v dokumentu.

Ukládá se do:

```text
document_entities.sentiment_score
```

### Doporučený rozsah

```text
-1.0 až 1.0
```

---

## 12. Risk scoring

Risk score vyjadřuje potenciální reputační nebo krizové riziko.

### Signály pro risk score

- negativní sentiment,
- toxicita,
- rychlost šíření,
- autorita zdroje,
- engagement,
- výskyt v médiích,
- vazba na sledovanou entitu,
- přítomnost krizových slov,
- počet zdrojů,
- opakování tématu.

### Doporučený rozsah

```text
0.0 až 1.0
```

---

## 13. Embeddingy

Embeddingy slouží pro:

- sémantické vyhledávání,
- hledání podobných dokumentů,
- clusterování,
- near-duplicate detection,
- RAG,
- historické porovnání krizí.

### Pravidla

- Embedding se počítá ze stabilní zpracované verze textu.
- Pro velmi dlouhé texty je nutné použít chunking nebo shrnutí.
- Je vhodné ukládat informaci o modelu do `processing_metadata`.

Příklad:

```json
{
  "embedding_model": "text-embedding-model",
  "embedding_created_at": "2026-01-01T10:00:00Z"
}
```

---

## 14. Topic detection

Topic detection přiřazuje dokumenty k tématům.

Metody:

- keyword pravidla,
- embedding clustering,
- LLM klasifikace,
- ruční označení,
- kombinace více metod.

Výstup:

- `topics`,
- `document_topics`.

---

## 15. Document relations

Document relations pomáhají mapovat šíření obsahu.

Typické vztahy:

- `reply_to`,
- `repost_of`,
- `quote_of`,
- `links_to`,
- `same_url`,
- `near_duplicate`,
- `semantic_similarity`,
- `same_thread`,
- `same_topic`.

Výstup:

```text
document_relations
```

---

## 16. Trend aggregation

Trend aggregation vytváří časová okna pro entity a témata.

Typická okna:

- 1 hodina,
- 24 hodin,
- 7 dní,
- 30 dní.

Výstup:

```text
trend_snapshots
```

Metriky:

- počet zmínek,
- počet pozitivních zmínek,
- počet neutrálních zmínek,
- počet negativních zmínek,
- unikátní autoři,
- unikátní zdroje,
- engagement,
- průměrný sentiment,
- průměrné riziko,
- trend score,
- anomaly score.

---

## 17. Alert evaluation

Alert evaluation vyhodnocuje, zda aktuální trend vyžaduje upozornění.

Typické alerty:

- mention spike,
- negative sentiment spike,
- risk score spike,
- new topic,
- cross-platform spread,
- news pickup,
- high engagement.

Výstup:

```text
alerts
```

---

# Stavový model dokumentu

## `pending`

Dokument čeká na zpracování.

## `processing`

Dokument se právě zpracovává.

## `processed`

Dokument byl úspěšně zpracován.

## `error`

Dokument skončil chybou.

## `ignored`

Dokument byl záměrně ignorován.

## `duplicate`

Dokument byl označen jako duplicita.

---

# Retry strategie

## Kdy opakovat

Retry je vhodný u:

- dočasného výpadku API,
- timeoutu,
- HTTP 429,
- HTTP 500,
- výpadku LLM služby,
- dočasného problému databáze.

## Kdy neopakovat

Retry není vhodný u:

- nevalidního payloadu,
- chybějícího povinného obsahu,
- HTTP 401,
- HTTP 403,
- trvale neexistujícího zdroje,
- porušení validačních pravidel.

## Doporučený model

```text
max_retries = 3
backoff = exponential
jitter = true
```

---

# Logging

Každý důležitý krok pipeline by měl logovat:

- `tenant_id`,
- `source_id`,
- `collection_run_id`,
- `data_id`,
- typ operace,
- stav,
- chybu,
- délku běhu.

Logy nesmí obsahovat:

- API klíče,
- tokeny,
- service role key,
- zbytečně velké raw payloady,
- citlivé osobní údaje bez legitimního důvodu.

---

# Error handling

Chyby by měly být ukládány do:

```text
processing_events
```

Doporučená struktura chyby:

```json
{
  "event_type": "document_transform_failed",
  "event_level": "error",
  "message": "Failed to parse published_at",
  "details": {
    "source_field": "pubDate",
    "value": "invalid-date"
  }
}
```

---

# Minimální MVP pipeline

Pro první verzi stačí:

```text
RSS ingest
    ↓
normalizace
    ↓
deduplikace podle URL/hash
    ↓
uložení raw_social_data
    ↓
jednoduché entity matching
    ↓
sentiment
    ↓
základní trend aggregation
```

---

# Budoucí rozšíření

Pipeline je možné rozšířit o:

- message queue,
- dead-letter queue,
- paralelní zpracování,
- prioritizaci zdrojů,
- LLM batch processing,
- automatické reprocessing joby,
- versioning modelů,
- historické přepočty trendů,
- propagation graph,
- report generation.
