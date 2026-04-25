# Dokumentace databáze: SocialScanner

Tento dokument popisuje doporučený databázový model projektu **SocialScanner**.

Databáze je navržena pro ukládání, normalizaci, vyhledávání a analytické zpracování veřejně dostupných online zmínek ze sociálních sítí, zpravodajských webů, RSS kanálů, diskusních platforem a dalších externích zdrojů.

Cílem databázového modelu je podporovat:

- multi-tenant režim pro více zákazníků,
- ukládání surových i zpracovaných dat,
- sledování konkrétních entit,
- extrakci entit z textu,
- sentiment a reputační skórování,
- detekci trendů a anomálií,
- vektorové vyhledávání přes embeddingy,
- auditovatelné zpracování dat,
- budoucí alerting, reporting a dashboardy.

---

## Základní principy návrhu

### 1. Multi-tenant izolace

Každý zákazník je reprezentován jako samostatný tenant.

Většina hlavních tabulek obsahuje sloupec `tenant_id`, který zajišťuje logické oddělení dat mezi zákazníky.

To umožňuje:

- více firemních zákazníků,
- PR agentury s více klienty,
- interní týmy,
- různé úrovně přístupových práv,
- rozdílné sledované entity pro každého zákazníka.

---

### 2. Oddělení surových a zpracovaných dat

Systém uchovává původní stažený obsah i jeho zpracovanou podobu.

To umožňuje:

- opakované zpracování novějšími modely,
- audit zpracování,
- ladění NLP pipeline,
- zpětné dohledání původního zdroje,
- validaci chyb a duplicit.

---

### 3. Flexibilita přes `jsonb`

Každá platforma poskytuje jiná metadata.

Proto databáze používá sloupce typu `jsonb`, zejména:

- `metrics`,
- `raw_metadata`,
- `processing_metadata`,
- `alert_payload`,
- `metadata`.

---

### 4. Připravenost na vektorové vyhledávání

Textový obsah může být převáděn na embeddingy a ukládán pomocí rozšíření `pgvector`.

To umožňuje:

- sémantické vyhledávání,
- hledání podobných článků a příspěvků,
- deduplikaci podobného obsahu,
- clusterování témat,
- RAG scénáře,
- hledání historicky podobných reputačních situací.

---

### 5. Auditovatelné zpracování

Důležité části pipeline ukládají stav zpracování, chyby a časové údaje.

Díky tomu lze dohledat:

- kdy byl obsah stažen,
- odkud byl stažen,
- v jakém běhu pipeline vznikl,
- zda se zpracování povedlo,
- proč záznam skončil chybou,
- jaká verze modelu nebo pipeline byla použita.

---

## Logická architektura databáze

```text
tenants
    ↓
tenant_members

tenants
    ↓
data_sources
    ↓
collection_runs
    ↓
raw_social_data
    ↓
document_entities
    ↓
entities
    ↓
entity_aliases

raw_social_data
    ↓
document_topics
    ↓
topics

raw_social_data
    ↓
document_relations

entities / topics
    ↓
trend_snapshots
    ↓
alerts
```

---

## Hlavní datový tok

```text
Externí zdroj
    ↓
data_sources
    ↓
collection_runs
    ↓
raw_social_data
    ↓
transformace / NLP / embeddingy
    ↓
entities + document_entities
    ↓
topics + document_topics
    ↓
trend_snapshots
    ↓
alerts / reports / dashboardy
```

---

## Přehled tabulek

| Tabulka | Účel |
|---|---|
| `tenants` | Zákazníci, organizace nebo pracovní prostory |
| `tenant_members` | Uživatelé přiřazení k tenantům |
| `data_sources` | Konfigurace zdrojů dat |
| `collection_runs` | Jednotlivá spuštění sběru dat |
| `raw_social_data` | Hlavní tabulka článků, příspěvků a komentářů |
| `entities` | Slovník extrahovaných a sledovaných entit |
| `entity_aliases` | Alternativní názvy entit |
| `document_entities` | Vazba mezi dokumenty a entitami |
| `topics` | Automaticky nebo ručně identifikovaná témata |
| `document_topics` | Vazba mezi dokumenty a tématy |
| `document_relations` | Vazby mezi dokumenty, například sdílení, citace, odpovědi nebo podobnost |
| `trend_snapshots` | Agregované časové snímky trendů |
| `alerts` | Upozornění na rizikové události |
| `processing_events` | Auditní log zpracování |

---

# Core tabulky

## 1. `tenants`

Tabulka reprezentuje zákazníka, organizaci, tým nebo pracovní prostor.

Každý tenant má vlastní zdroje, sledované entity, data, trendy a alerty.

Použití:

- oddělení dat zákazníků,
- multi-tenant SaaS režim,
- agenturní režim pro více klientů,
- budoucí billing a plánování tarifů.

---

## 2. `tenant_members`

Vazební tabulka mezi uživateli ze Supabase Auth a tenanty.

Jeden uživatel může být členem více tenantů a v každém může mít jinou roli.

Doporučené role:

- `owner`,
- `admin`,
- `analyst`,
- `viewer`.

---

## 3. `data_sources`

Tabulka definuje zdroje, ze kterých systém sbírá data.

Zdroj může být například:

- RSS feed,
- konkrétní zpravodajský web,
- Apify actor,
- veřejný Telegram kanál,
- YouTube kanál,
- subreddit,
- konkrétní API endpoint,
- interně definovaný crawler.

Použití:

- správa aktivních zdrojů,
- vypínání a zapínání zdrojů,
- konfigurace frekvence sběru,
- ukládání parametrů zdroje,
- audit původu dat.

---

## 4. `collection_runs`

Tabulka ukládá jednotlivá spuštění sběru dat.

Každý běh je navázán na konkrétní `data_source`.

Použití:

- sledování úspěšnosti ingest pipeline,
- měření počtu stažených záznamů,
- měření počtu nových záznamů,
- měření počtu duplicit,
- ukládání chyb z externích zdrojů,
- ladění crawlerů a API integrací.

---

## 5. `raw_social_data`

Hlavní tabulka pro ukládání článků, příspěvků, komentářů a dalších textových jednotek.

Název tabulky je ponechán jako `raw_social_data`, ale tabulka nemusí obsahovat pouze sociální sítě. Může obsahovat také články, RSS položky, diskusní komentáře nebo jiné veřejné textové záznamy.

Hlavní vlastnosti:

- ukládá surový i částečně normalizovaný obsah,
- obsahuje původní URL,
- obsahuje autora nebo zdroj,
- podporuje deduplikaci,
- podporuje embeddingy,
- obsahuje stav zpracování,
- obsahuje platformní metriky,
- je napojena na tenanty, zdroje a collection runs.

Doporučené hodnoty `content_type`:

- `article`,
- `post`,
- `comment`,
- `reply`,
- `video`,
- `short_video`,
- `podcast`,
- `rss_item`,
- `forum_thread`,
- `forum_comment`,
- `other`.

Doporučené hodnoty `processing_status`:

- `pending`,
- `processing`,
- `processed`,
- `error`,
- `ignored`,
- `duplicate`.

---

## 6. `entities`

Tabulka obsahuje entity, které systém rozpoznává nebo aktivně sleduje.

Entitou může být:

- firma,
- značka,
- produkt,
- osoba,
- politická strana,
- instituce,
- kampaň,
- téma,
- událost,
- konkurent,
- hashtag,
- URL doména.

Doporučené hodnoty `entity_type`:

- `brand`,
- `company`,
- `person`,
- `product`,
- `organization`,
- `institution`,
- `political_party`,
- `event`,
- `topic`,
- `hashtag`,
- `domain`,
- `location`,
- `other`.

---

## 7. `entity_aliases`

Tabulka obsahuje alternativní názvy entit.

Příklad:

| Entita | Aliasy |
|---|---|
| `Škoda Auto` | `Škodovka`, `Skoda`, `Škoda`, `Skoda Auto` |
| `Česká spořitelna` | `ČS`, `Ceska sporitelna`, `Spořka` |
| `OpenAI` | `ChatGPT`, `GPT`, `Open AI` |

Použití:

- lepší matching entit,
- zachycení překlepů,
- zachycení neoficiálních názvů,
- práce s diakritikou,
- práce se slangem,
- sjednocení zmínek pod jednu entitu.

---

## 8. `document_entities`

Vazební tabulka mezi dokumenty a entitami.

Jedna entita se může objevit v mnoha dokumentech a jeden dokument může obsahovat mnoho entit.

Ukládá:

- sentiment entity v kontextu konkrétního dokumentu,
- počet výskytů,
- relevanci entity v textu,
- způsob detekce,
- rizikové skóre v daném kontextu.

Doporučené hodnoty `detection_method`:

- `exact_match`,
- `alias_match`,
- `regex`,
- `ner_model`,
- `llm`,
- `manual`,
- `unknown`.

---

# Analytické tabulky

## 9. `topics`

Tabulka obsahuje témata nebo narativy identifikované v datech.

Téma může vzniknout:

- ručně,
- automatickým clusterováním,
- LLM analýzou,
- pravidlem,
- kombinací více signálů.

Příklad témat:

- `zdražování energií`,
- `kritika zákaznické podpory`,
- `negativní zkušenosti s produktem`,
- `výpadek služby`,
- `politická kauza`,
- `dezinformační narativ`,
- `virální meme`.

---

## 10. `document_topics`

Vazební tabulka mezi dokumenty a tématy.

Používá se pro:

- clusterování podobného obsahu,
- sledování vývoje tématu v čase,
- měření sentimentu tématu,
- detekci náhlých nárůstů,
- porovnávání témat mezi zdroji.

---

## 11. `document_relations`

Tabulka ukládá vztahy mezi dokumenty.

Je důležitá pro mapování šíření obsahu.

Doporučené hodnoty `relation_type`:

- `reply_to`,
- `repost_of`,
- `quote_of`,
- `links_to`,
- `same_url`,
- `near_duplicate`,
- `semantic_similarity`,
- `same_thread`,
- `same_topic`,
- `manual`.

---

## 12. `trend_snapshots`

Tabulka ukládá agregované časové snímky trendů.

Každý záznam reprezentuje stav entity nebo tématu v konkrétním časovém okně.

Použití:

- dashboardy,
- časové grafy,
- detekce anomálií,
- reputační skóre,
- detekce růstu negativních zmínek,
- porovnání aktuálního stavu s historickým baseline.

---

## 13. `alerts`

Tabulka ukládá upozornění generovaná systémem.

Alert může vzniknout například při:

- náhlém růstu počtu zmínek,
- růstu negativního sentimentu,
- výskytu rizikového tématu,
- překročení reputačního skóre,
- šíření obsahu přes více platforem,
- vstupu tématu do zpravodajských webů,
- výskytu sledované entity v rizikovém kontextu.

Doporučené hodnoty `severity`:

- `info`,
- `low`,
- `medium`,
- `high`,
- `critical`.

Doporučené hodnoty `status`:

- `open`,
- `acknowledged`,
- `resolved`,
- `ignored`.

---

## 14. `processing_events`

Auditní tabulka pro ukládání událostí z pipeline.

Používá se pro:

- logování chyb,
- sledování pipeline,
- audit zpracování,
- debugging,
- historické vyhodnocení stability systému.

---

# Doporučené konvence

## Časové údaje

Všechny časové údaje používat jako:

```sql
timestamptz
```

---

## Názvy sloupců

Používat `snake_case`.

Příklad:

```text
published_at
source_platform
processing_status
sentiment_score
```

---

## Primární klíče

Používat UUID:

```sql
id uuid DEFAULT gen_random_uuid() PRIMARY KEY
```

---

## Sentiment score

Doporučený rozsah:

```text
-1.0 až 1.0
```

| Hodnota | Význam |
|---|---|
| `-1.0` | Velmi negativní |
| `0.0` | Neutrální |
| `1.0` | Velmi pozitivní |

---

## Risk score

Doporučený rozsah:

```text
0.0 až 1.0
```

| Hodnota | Význam |
|---|---|
| `0.0` | Bez rizika |
| `0.5` | Střední riziko |
| `1.0` | Kritické riziko |

---

## Trend score

Doporučený rozsah:

```text
0.0 až 1.0
```

| Hodnota | Význam |
|---|---|
| `0.0` | Bez trendu |
| `0.5` | Viditelný růst |
| `1.0` | Silný virální trend |

---

# DDL schéma

```sql
-- ============================================================
-- SocialScanner Database Schema
-- PostgreSQL / Supabase
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

-- ------------------------------------------------------------
-- Tenants
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS tenants (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    name text NOT NULL,
    slug text NOT NULL UNIQUE,
    plan text DEFAULT 'free',
    status text DEFAULT 'active',
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_tenants_status
        CHECK (status IN ('active', 'inactive', 'suspended', 'deleted'))
);

-- ------------------------------------------------------------
-- Tenant members
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS tenant_members (
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role text DEFAULT 'viewer' NOT NULL,
    created_at timestamptz DEFAULT now() NOT NULL,
    PRIMARY KEY (tenant_id, user_id),
    CONSTRAINT chk_tenant_members_role
        CHECK (role IN ('owner', 'admin', 'analyst', 'viewer'))
);

-- ------------------------------------------------------------
-- Data sources
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS data_sources (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name text NOT NULL,
    source_type text NOT NULL,
    source_platform text NOT NULL,
    base_url text,
    config jsonb DEFAULT '{}'::jsonb,
    is_active boolean DEFAULT true NOT NULL,
    last_collected_at timestamptz,
    next_collection_at timestamptz,
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT chk_data_sources_source_type
        CHECK (source_type IN ('rss', 'api', 'apify', 'crawler', 'webhook', 'manual', 'other')),
    UNIQUE (tenant_id, name)
);

-- ------------------------------------------------------------
-- Collection runs
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS collection_runs (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_id uuid REFERENCES data_sources(id) ON DELETE SET NULL,
    status text DEFAULT 'running' NOT NULL,
    started_at timestamptz DEFAULT now() NOT NULL,
    finished_at timestamptz,
    fetched_count integer DEFAULT 0 NOT NULL,
    inserted_count integer DEFAULT 0 NOT NULL,
    duplicate_count integer DEFAULT 0 NOT NULL,
    error_count integer DEFAULT 0 NOT NULL,
    error_message text,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_collection_runs_status
        CHECK (status IN ('running', 'success', 'partial_success', 'error', 'cancelled'))
);

-- ------------------------------------------------------------
-- Raw social data
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS raw_social_data (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_id uuid REFERENCES data_sources(id) ON DELETE SET NULL,
    collection_run_id uuid REFERENCES collection_runs(id) ON DELETE SET NULL,
    external_id text,
    external_parent_id text,
    external_thread_id text,
    source_url text,
    canonical_url text,
    source_platform text NOT NULL,
    content_type text DEFAULT 'post' NOT NULL,
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL,
    collected_at timestamptz DEFAULT now() NOT NULL,
    published_at timestamptz,
    author_id text,
    author_handle text,
    author_display_name text,
    author_url text,
    title text,
    content text NOT NULL,
    content_hash text,
    language_code varchar(10),
    metrics jsonb DEFAULT '{}'::jsonb,
    raw_metadata jsonb DEFAULT '{}'::jsonb,
    processing_metadata jsonb DEFAULT '{}'::jsonb,
    embedding vector(1536),
    sentiment_score numeric,
    risk_score numeric,
    toxicity_score numeric,
    processing_status text DEFAULT 'pending' NOT NULL,
    processing_error text,
    is_deleted boolean DEFAULT false NOT NULL,
    is_duplicate boolean DEFAULT false NOT NULL,
    CONSTRAINT chk_raw_social_data_content_type
        CHECK (content_type IN ('article', 'post', 'comment', 'reply', 'video', 'short_video', 'podcast', 'rss_item', 'forum_thread', 'forum_comment', 'other')),
    CONSTRAINT chk_raw_social_data_processing_status
        CHECK (processing_status IN ('pending', 'processing', 'processed', 'error', 'ignored', 'duplicate')),
    CONSTRAINT chk_raw_social_data_sentiment_score
        CHECK (sentiment_score IS NULL OR sentiment_score BETWEEN -1 AND 1),
    CONSTRAINT chk_raw_social_data_risk_score
        CHECK (risk_score IS NULL OR risk_score BETWEEN 0 AND 1),
    CONSTRAINT chk_raw_social_data_toxicity_score
        CHECK (toxicity_score IS NULL OR toxicity_score BETWEEN 0 AND 1)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_raw_social_external
ON raw_social_data (tenant_id, source_platform, external_id)
WHERE external_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_raw_social_canonical_url
ON raw_social_data (tenant_id, canonical_url)
WHERE canonical_url IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_raw_social_content_hash
ON raw_social_data (tenant_id, source_platform, content_hash)
WHERE content_hash IS NOT NULL;

-- ------------------------------------------------------------
-- Entities
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS entities (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    entity_name text NOT NULL,
    normalized_name text NOT NULL,
    entity_type text DEFAULT 'other' NOT NULL,
    description text,
    is_tracked boolean DEFAULT false NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_entities_entity_type
        CHECK (entity_type IN ('brand', 'company', 'person', 'product', 'organization', 'institution', 'political_party', 'event', 'topic', 'hashtag', 'domain', 'location', 'other')),
    UNIQUE (tenant_id, normalized_name, entity_type)
);

-- ------------------------------------------------------------
-- Entity aliases
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS entity_aliases (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    entity_id uuid NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    alias text NOT NULL,
    normalized_alias text NOT NULL,
    alias_type text DEFAULT 'manual' NOT NULL,
    created_at timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT chk_entity_aliases_alias_type
        CHECK (alias_type IN ('manual', 'generated', 'imported', 'detected')),
    UNIQUE (tenant_id, entity_id, normalized_alias)
);

-- ------------------------------------------------------------
-- Document entities
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS document_entities (
    data_id uuid NOT NULL REFERENCES raw_social_data(id) ON DELETE CASCADE,
    entity_id uuid NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    sentiment_score numeric,
    relevance_score numeric,
    risk_score numeric,
    occurrence_count integer DEFAULT 1 NOT NULL,
    detection_method text DEFAULT 'unknown' NOT NULL,
    matched_text text,
    context_snippet text,
    created_at timestamptz DEFAULT now() NOT NULL,
    PRIMARY KEY (data_id, entity_id),
    CONSTRAINT chk_document_entities_sentiment_score
        CHECK (sentiment_score IS NULL OR sentiment_score BETWEEN -1 AND 1),
    CONSTRAINT chk_document_entities_relevance_score
        CHECK (relevance_score IS NULL OR relevance_score BETWEEN 0 AND 1),
    CONSTRAINT chk_document_entities_risk_score
        CHECK (risk_score IS NULL OR risk_score BETWEEN 0 AND 1),
    CONSTRAINT chk_document_entities_detection_method
        CHECK (detection_method IN ('exact_match', 'alias_match', 'regex', 'ner_model', 'llm', 'manual', 'unknown'))
);

-- ------------------------------------------------------------
-- Topics
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS topics (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    topic_name text NOT NULL,
    normalized_name text NOT NULL,
    description text,
    topic_type text DEFAULT 'detected' NOT NULL,
    is_tracked boolean DEFAULT false NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamptz DEFAULT now() NOT NULL,
    updated_at timestamptz DEFAULT now() NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT chk_topics_topic_type
        CHECK (topic_type IN ('manual', 'detected', 'cluster', 'narrative', 'campaign', 'incident', 'other')),
    UNIQUE (tenant_id, normalized_name)
);

-- ------------------------------------------------------------
-- Document topics
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS document_topics (
    data_id uuid NOT NULL REFERENCES raw_social_data(id) ON DELETE CASCADE,
    topic_id uuid NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    relevance_score numeric,
    sentiment_score numeric,
    risk_score numeric,
    detection_method text DEFAULT 'unknown' NOT NULL,
    created_at timestamptz DEFAULT now() NOT NULL,
    PRIMARY KEY (data_id, topic_id),
    CONSTRAINT chk_document_topics_relevance_score
        CHECK (relevance_score IS NULL OR relevance_score BETWEEN 0 AND 1),
    CONSTRAINT chk_document_topics_sentiment_score
        CHECK (sentiment_score IS NULL OR sentiment_score BETWEEN -1 AND 1),
    CONSTRAINT chk_document_topics_risk_score
        CHECK (risk_score IS NULL OR risk_score BETWEEN 0 AND 1),
    CONSTRAINT chk_document_topics_detection_method
        CHECK (detection_method IN ('keyword', 'embedding_cluster', 'llm', 'manual', 'rule', 'unknown'))
);

-- ------------------------------------------------------------
-- Document relations
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS document_relations (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_data_id uuid NOT NULL REFERENCES raw_social_data(id) ON DELETE CASCADE,
    target_data_id uuid NOT NULL REFERENCES raw_social_data(id) ON DELETE CASCADE,
    relation_type text NOT NULL,
    confidence_score numeric,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT chk_document_relations_relation_type
        CHECK (relation_type IN ('reply_to', 'repost_of', 'quote_of', 'links_to', 'same_url', 'near_duplicate', 'semantic_similarity', 'same_thread', 'same_topic', 'manual')),
    CONSTRAINT chk_document_relations_confidence_score
        CHECK (confidence_score IS NULL OR confidence_score BETWEEN 0 AND 1),
    CONSTRAINT chk_document_relations_not_self
        CHECK (source_data_id <> target_data_id),
    UNIQUE (tenant_id, source_data_id, target_data_id, relation_type)
);

-- ------------------------------------------------------------
-- Trend snapshots
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS trend_snapshots (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    entity_id uuid REFERENCES entities(id) ON DELETE CASCADE,
    topic_id uuid REFERENCES topics(id) ON DELETE CASCADE,
    window_start timestamptz NOT NULL,
    window_end timestamptz NOT NULL,
    window_granularity text NOT NULL,
    mention_count integer DEFAULT 0 NOT NULL,
    positive_count integer DEFAULT 0 NOT NULL,
    neutral_count integer DEFAULT 0 NOT NULL,
    negative_count integer DEFAULT 0 NOT NULL,
    unique_author_count integer DEFAULT 0 NOT NULL,
    unique_source_count integer DEFAULT 0 NOT NULL,
    total_engagement numeric DEFAULT 0 NOT NULL,
    avg_sentiment_score numeric,
    avg_risk_score numeric,
    trend_score numeric,
    anomaly_score numeric,
    top_terms jsonb DEFAULT '[]'::jsonb,
    top_sources jsonb DEFAULT '[]'::jsonb,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT chk_trend_snapshots_entity_or_topic
        CHECK (entity_id IS NOT NULL OR topic_id IS NOT NULL),
    CONSTRAINT chk_trend_snapshots_window
        CHECK (window_end > window_start),
    CONSTRAINT chk_trend_snapshots_granularity
        CHECK (window_granularity IN ('hour', 'day', 'week', 'month')),
    CONSTRAINT chk_trend_snapshots_avg_sentiment_score
        CHECK (avg_sentiment_score IS NULL OR avg_sentiment_score BETWEEN -1 AND 1),
    CONSTRAINT chk_trend_snapshots_avg_risk_score
        CHECK (avg_risk_score IS NULL OR avg_risk_score BETWEEN 0 AND 1),
    CONSTRAINT chk_trend_snapshots_trend_score
        CHECK (trend_score IS NULL OR trend_score BETWEEN 0 AND 1),
    CONSTRAINT chk_trend_snapshots_anomaly_score
        CHECK (anomaly_score IS NULL OR anomaly_score >= 0)
);

-- ------------------------------------------------------------
-- Alerts
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS alerts (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    entity_id uuid REFERENCES entities(id) ON DELETE SET NULL,
    topic_id uuid REFERENCES topics(id) ON DELETE SET NULL,
    title text NOT NULL,
    description text,
    alert_type text NOT NULL,
    severity text DEFAULT 'medium' NOT NULL,
    status text DEFAULT 'open' NOT NULL,
    risk_score numeric,
    trend_score numeric,
    anomaly_score numeric,
    first_detected_at timestamptz DEFAULT now() NOT NULL,
    last_updated_at timestamptz DEFAULT now() NOT NULL,
    acknowledged_at timestamptz,
    resolved_at timestamptz,
    alert_payload jsonb DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT chk_alerts_entity_or_topic
        CHECK (entity_id IS NOT NULL OR topic_id IS NOT NULL),
    CONSTRAINT chk_alerts_alert_type
        CHECK (alert_type IN ('mention_spike', 'negative_sentiment_spike', 'risk_score_spike', 'new_topic', 'cross_platform_spread', 'news_pickup', 'high_engagement', 'manual', 'other')),
    CONSTRAINT chk_alerts_severity
        CHECK (severity IN ('info', 'low', 'medium', 'high', 'critical')),
    CONSTRAINT chk_alerts_status
        CHECK (status IN ('open', 'acknowledged', 'resolved', 'ignored')),
    CONSTRAINT chk_alerts_risk_score
        CHECK (risk_score IS NULL OR risk_score BETWEEN 0 AND 1),
    CONSTRAINT chk_alerts_trend_score
        CHECK (trend_score IS NULL OR trend_score BETWEEN 0 AND 1),
    CONSTRAINT chk_alerts_anomaly_score
        CHECK (anomaly_score IS NULL OR anomaly_score >= 0)
);

-- ------------------------------------------------------------
-- Processing events
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS processing_events (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id uuid REFERENCES tenants(id) ON DELETE CASCADE,
    data_id uuid REFERENCES raw_social_data(id) ON DELETE CASCADE,
    collection_run_id uuid REFERENCES collection_runs(id) ON DELETE SET NULL,
    event_type text NOT NULL,
    event_level text DEFAULT 'info' NOT NULL,
    message text,
    details jsonb DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT chk_processing_events_event_level
        CHECK (event_level IN ('debug', 'info', 'warning', 'error', 'critical'))
);

-- ============================================================
-- Indexes
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_tenant_members_user
ON tenant_members (user_id);

CREATE INDEX IF NOT EXISTS idx_data_sources_tenant
ON data_sources (tenant_id);

CREATE INDEX IF NOT EXISTS idx_data_sources_active
ON data_sources (tenant_id, is_active);

CREATE INDEX IF NOT EXISTS idx_collection_runs_tenant_started
ON collection_runs (tenant_id, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_raw_social_tenant_published
ON raw_social_data (tenant_id, published_at DESC);

CREATE INDEX IF NOT EXISTS idx_raw_social_tenant_collected
ON raw_social_data (tenant_id, collected_at DESC);

CREATE INDEX IF NOT EXISTS idx_raw_social_platform
ON raw_social_data (tenant_id, source_platform);

CREATE INDEX IF NOT EXISTS idx_raw_social_processing_status
ON raw_social_data (tenant_id, processing_status);

CREATE INDEX IF NOT EXISTS idx_raw_social_metrics_gin
ON raw_social_data USING gin (metrics);

CREATE INDEX IF NOT EXISTS idx_raw_social_metadata_gin
ON raw_social_data USING gin (raw_metadata);

CREATE INDEX IF NOT EXISTS idx_raw_social_content_fts
ON raw_social_data
USING gin (to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(content, '')));

CREATE INDEX IF NOT EXISTS idx_raw_social_embedding_ivfflat
ON raw_social_data
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100)
WHERE embedding IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_entities_tenant_type
ON entities (tenant_id, entity_type);

CREATE INDEX IF NOT EXISTS idx_entities_tracked
ON entities (tenant_id, is_tracked)
WHERE is_tracked = true;

CREATE INDEX IF NOT EXISTS idx_entity_aliases_tenant_alias
ON entity_aliases (tenant_id, normalized_alias);

CREATE INDEX IF NOT EXISTS idx_document_entities_entity
ON document_entities (entity_id);

CREATE INDEX IF NOT EXISTS idx_document_entities_tenant_entity
ON document_entities (tenant_id, entity_id);

CREATE INDEX IF NOT EXISTS idx_topics_tenant_type
ON topics (tenant_id, topic_type);

CREATE INDEX IF NOT EXISTS idx_document_topics_topic
ON document_topics (topic_id);

CREATE INDEX IF NOT EXISTS idx_document_relations_source
ON document_relations (source_data_id);

CREATE INDEX IF NOT EXISTS idx_document_relations_target
ON document_relations (target_data_id);

CREATE INDEX IF NOT EXISTS idx_trend_snapshots_tenant_window
ON trend_snapshots (tenant_id, window_start DESC, window_end DESC);

CREATE INDEX IF NOT EXISTS idx_trend_snapshots_entity_window
ON trend_snapshots (entity_id, window_start DESC)
WHERE entity_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_trend_snapshots_topic_window
ON trend_snapshots (topic_id, window_start DESC)
WHERE topic_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_alerts_tenant_status
ON alerts (tenant_id, status);

CREATE INDEX IF NOT EXISTS idx_alerts_tenant_severity
ON alerts (tenant_id, severity);

CREATE INDEX IF NOT EXISTS idx_alerts_detected
ON alerts (tenant_id, first_detected_at DESC);

CREATE INDEX IF NOT EXISTS idx_processing_events_data
ON processing_events (data_id);

CREATE INDEX IF NOT EXISTS idx_processing_events_collection_run
ON processing_events (collection_run_id);

CREATE INDEX IF NOT EXISTS idx_processing_events_created
ON processing_events (created_at DESC);

-- ============================================================
-- updated_at helper
-- ============================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_tenants_updated_at ON tenants;
CREATE TRIGGER trg_tenants_updated_at
BEFORE UPDATE ON tenants
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_data_sources_updated_at ON data_sources;
CREATE TRIGGER trg_data_sources_updated_at
BEFORE UPDATE ON data_sources
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_raw_social_data_updated_at ON raw_social_data;
CREATE TRIGGER trg_raw_social_data_updated_at
BEFORE UPDATE ON raw_social_data
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_entities_updated_at ON entities;
CREATE TRIGGER trg_entities_updated_at
BEFORE UPDATE ON entities
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_topics_updated_at ON topics;
CREATE TRIGGER trg_topics_updated_at
BEFORE UPDATE ON topics
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- Row Level Security preparation
-- ============================================================

ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE collection_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE raw_social_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE entity_aliases ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_relations ENABLE ROW LEVEL SECURITY;
ALTER TABLE trend_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_events ENABLE ROW LEVEL SECURITY;
```

---

# Doporučené RLS pravidlo pro budoucí frontend

Pokud bude frontend přistupovat přímo do Supabase, je vhodné použít RLS policies založené na členství uživatele v tenantovi.

```sql
CREATE OR REPLACE FUNCTION is_tenant_member(target_tenant_id uuid)
RETURNS boolean AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM tenant_members tm
        WHERE tm.tenant_id = target_tenant_id
          AND tm.user_id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

Příklad policy pro čtení dat:

```sql
CREATE POLICY "Tenant members can read raw social data"
ON raw_social_data
FOR SELECT
USING (is_tenant_member(tenant_id));
```

---

# Minimální produkční verze

Pokud není potřeba nasadit celé schéma hned, minimální doporučené jádro je:

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

Tabulky pro budoucí analytiku lze přidat později:

```text
topics
document_topics
document_relations
trend_snapshots
alerts
```
