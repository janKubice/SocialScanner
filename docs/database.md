# Dokumentace databáze: SocialScanner

Tento dokument popisuje relační datový model a strukturu tabulek pro ukládání surových dat ze sociálních sítí, zpravodajských webů a extrahovaných entit.

## Architektura databáze

Návrh odpovídá celkové architektuře pipeline. Data jsou po stažení (přes Apify, API, nebo RSS) a průchodu přes Message Queue zpracována do dvou hlavních větví:
1. **Zpracování obsahu:** Ukládá se do hlavní tabulky `raw_social_data`.
2. **Extrahování entit:** Identifikované entity (firmy, osoby, témata) se ukládají do tabulky `entities` a následně se propojují s konkrétním článkem přes vazební tabulku `document_entities`.

*(Pokud máte diagram uložený ve složce docs, můžete jej zobrazit odkomentováním řádku níže)*
---

## 1. Tabulka: `raw_social_data` (Články/příspěvky/komentáře)

Hlavní tabulka uchovávající veškerý textový obsah z různých zdrojů. Je navržena tak, aby bezpečně oddělovala data jednotlivých uživatelů (tenantů) a zamezovala duplicitám.

**Klíčové vlastnosti:**
* **Zamezení duplicit:** Unikátní constraint na kombinaci `tenant_id`, `external_id` a `source_platform` zajišťuje, že stejný tweet nebo článek nestáhneme dvakrát.
* **Vektorové vyhledávání:** Sloupec `embedding` (typ `vector(1536)`) je připraven pro sémantické vyhledávání a RAG pomocí OpenAI modelů.
* **Flexibilita:** Sloupce `metrics` a `raw_metadata` (typu `jsonb`) umožňují ukládat proměnlivá data specifická pro danou platformu bez nutnosti měnit schéma.

## 2. Tabulka: `entities` (Entity)

Slovník všech unikátních entit napříč systémem pro daného tenanta. Každá entita je uložena pouze jednou.

## 3. Tabulka: `document_entities` (Článek_Entita)

Vazební (M:N) tabulka propojující články/příspěvky s nalezenými entitami. 

**Klíčové vlastnosti:**
* Nese dodatečnou informaci o **sentimentu** (`sentiment_score`) dané entity v kontextu konkrétního článku.
* Uchovává počet výskytů (`occurrence_count`) pro vážení důležitosti entity v textu.
* Díky `ON DELETE CASCADE` se při smazání článku automaticky smažou i jeho vazby na entity.

---

## Definice DDL (SQL Skript)

Níže je kompletní SQL skript pro inicializaci databázového schématu (určeno pro PostgreSQL s případným `pgvector` rozšířením):

```sql
CREATE TABLE raw_social_data (
    -- Identifikátory
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    external_id text, -- Unikátní ID z platformy (např. tweet ID), brání duplicitám
    tenant_id uuid REFERENCES auth.users NOT NULL,
    
    -- Časové údaje
    created_at timestamptz DEFAULT now(), -- Kdy bylo uloženo do DB
    published_at timestamptz, -- Kdy byl příspěvek skutečně publikován
    
    -- Zdroj a autor
    source_platform text NOT NULL, -- apify, web_api, rss
    source_url text, -- Přímý odkaz na příspěvek
    author_handle text, -- Uživatelské jméno autora
    title text, -- Titulek nebo krátké shrnutí
    
    -- Obsah
    content text NOT NULL,
    language_code varchar(5), -- Důležité pro výběr modelu NLP
    
    -- Flexibilní data a AI
    metrics jsonb, -- Počty lajků, sdílení, zobrazení
    raw_metadata jsonb, -- Kompletní původní objekt z Apify/API
    embedding vector(1536), 
    
    -- Stav zpracování
    processing_status text DEFAULT 'pending', -- pending, processed, error
    
    -- Constraint pro zamezení duplicitních záznamů ze stejného zdroje pro jednoho tenanta
    UNIQUE(tenant_id, external_id, source_platform)
);

-- Indexy pro zrychlení vyhledávání a filtrování dashboardů
CREATE INDEX idx_social_tenant_published ON raw_social_data (tenant_id, published_at DESC);
CREATE INDEX idx_social_platform ON raw_social_data (source_platform);

CREATE TABLE entities (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id uuid REFERENCES auth.users NOT NULL,
    entity_name text NOT NULL,
    entity_type text,
    UNIQUE(tenant_id, entity_name)
);

CREATE TABLE document_entities (
    data_id uuid REFERENCES raw_social_data(id) ON DELETE CASCADE,
    entity_id uuid REFERENCES entities(id) ON DELETE CASCADE,
    sentiment_score numeric,
    occurrence_count int DEFAULT 1,
    PRIMARY KEY (data_id, entity_id) -- Zajišťuje, že jedna entita je k jednomu článku přiřazena jen jednou
);