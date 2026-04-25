# Datové zdroje: SocialScanner

Tento dokument slouží jako šablona pro evidenci datových zdrojů v projektu **SocialScanner**.

Dokument má být průběžně doplňován podle toho, jak budou přibývat konkrétní zdroje dat.

Cílem dokumentace datových zdrojů je udržet přehled o tom:

- odkud systém získává data,
- jakým způsobem se data sbírají,
- jak často se sběr spouští,
- jaká metadata zdroj poskytuje,
- jaká jsou technická omezení,
- jaká jsou právní a provozní rizika,
- jak se data mapují do interního modelu.

---

## Zásady pro práci s datovými zdroji

Každý datový zdroj musí být před zařazením do produkční pipeline zdokumentován.

U každého zdroje je nutné znát:

- typ zdroje,
- vlastnictví nebo provozovatele zdroje,
- způsob přístupu,
- limity,
- stabilitu,
- očekávaný objem dat,
- povolené použití,
- strukturu odpovědi,
- transformační pravidla,
- chyby, které může zdroj vracet.

---

## Typy zdrojů

SocialScanner může v budoucnu pracovat s několika typy zdrojů.

### 1. RSS zdroje

Typické použití:

- zpravodajské weby,
- blogy,
- tiskové zprávy,
- firemní aktuality,
- tematické weby.

Výhody:

- jednoduchá integrace,
- nízká technická složitost,
- dobrá stabilita,
- vhodné pro MVP.

Nevýhody:

- často neobsahují celý text článku,
- mohou obsahovat pouze anotaci,
- ne vždy obsahují autora,
- někdy chybí jednoznačné ID.

---

### 2. Veřejná API

Typické použití:

- platformy s oficiálním API,
- datové služby,
- mediální databáze,
- interní partnerské zdroje.

Výhody:

- strukturovaná data,
- jasné limity,
- větší stabilita,
- lepší právní opora.

Nevýhody:

- nutnost API klíčů,
- rate limiting,
- placené tarify,
- změny API verzí.

---

### 3. Apify actors

Typické použití:

- crawling veřejných webů,
- scraping strukturovaných stránek,
- experimentální zdroje,
- rychlý prototyp ingest procesu.

Výhody:

- rychlé spuštění,
- méně vlastního scraping kódu,
- možnost škálování,
- existující actors pro mnoho scénářů.

Nevýhody:

- cena podle provozu,
- závislost na actoru,
- nutnost hlídat stabilitu výstupu,
- nutnost ověřit podmínky použití zdroje.

---

### 4. Vlastní crawler

Typické použití:

- specifické weby,
- zdroje bez RSS,
- zdroje se stabilní strukturou,
- kontrolovaný scraping veřejných dat.

Výhody:

- plná kontrola nad logikou,
- možnost přesně upravit parser,
- možnost optimalizovat výkon.

Nevýhody:

- vyšší údržba,
- riziko změny HTML struktury,
- právní a provozní omezení,
- nutnost řešit rate limiting a blokace.

---

### 5. Webhooky

Typické použití:

- externí služba posílá nová data do SocialScanneru,
- integrace s partnerským systémem,
- interní importy,
- notifikační zdroje.

Výhody:

- data přicházejí okamžitě,
- není nutné pravidelné polling volání,
- vhodné pro real-time scénáře.

Nevýhody:

- nutnost validace podpisu,
- nutnost chránit endpoint,
- riziko duplicit,
- potřeba robustního retry mechanismu.

---

### 6. Ruční importy

Typické použití:

- CSV soubory,
- JSON exporty,
- historická data,
- testovací datasety,
- zákaznické exporty.

Výhody:

- jednoduchý start,
- dobré pro testování,
- možnost nahrát historická data.

Nevýhody:

- neautomatické,
- riziko nekonzistentní struktury,
- nutnost validace dat.

---

## Stav zdroje

Každý zdroj by měl mít stav.

Doporučené hodnoty:

| Stav | Význam |
|---|---|
| `planned` | Zdroj je plánovaný, ale ještě není implementovaný |
| `experimental` | Zdroj je ve zkušebním režimu |
| `active` | Zdroj je aktivní a používá se |
| `paused` | Zdroj je dočasně vypnutý |
| `deprecated` | Zdroj se již nemá používat |
| `blocked` | Zdroj nelze používat kvůli technickému nebo právnímu omezení |

---

## Frekvence sběru

Doporučené hodnoty:

| Frekvence | Použití |
|---|---|
| `realtime` | Webhooky nebo zdroje s okamžitým doručením |
| `5m` | Vysoce prioritní zdroje |
| `15m` | Aktivní monitoring |
| `1h` | Standardní zdroje |
| `6h` | Méně důležité zdroje |
| `1d` | Denní souhrnné zdroje |
| `manual` | Ruční importy |

---

## Obecná šablona zdroje

Níže uvedenou šablonu kopírovat pro každý nový zdroj.

```markdown
## Název zdroje: [DOPLNIT]

### Základní informace

| Pole | Hodnota |
|---|---|
| Interní název | `[DOPLNIT]` |
| Typ zdroje | `[rss / api / apify / crawler / webhook / manual / other]` |
| Platforma | `[DOPLNIT]` |
| Stav | `[planned / experimental / active / paused / deprecated / blocked]` |
| Priorita | `[low / medium / high / critical]` |
| Vlastník implementace | `[DOPLNIT]` |
| Datum přidání | `[DOPLNIT]` |
| Poslední revize | `[DOPLNIT]` |

### Účel zdroje

[DOPLNIT]

Popište, proč se tento zdroj používá a jakou hodnotu přináší.

Příklad:

- sledování zpravodajských článků,
- sledování diskusí,
- sledování konkrétního tématu,
- sledování zmínek o entitách,
- historická data pro trénování nebo validaci trend detection.

### Přístup ke zdroji

| Pole | Hodnota |
|---|---|
| URL / endpoint | `[DOPLNIT]` |
| Autentizace | `[none / api_key / oauth / token / other]` |
| Potřebné secrets | `[DOPLNIT]` |
| Rate limit | `[DOPLNIT]` |
| Paginace | `[ano / ne / typ]` |
| Formát odpovědi | `[json / xml / html / csv / other]` |

### Frekvence sběru

| Pole | Hodnota |
|---|---|
| Doporučená frekvence | `[DOPLNIT]` |
| Minimální bezpečný interval | `[DOPLNIT]` |
| Maximální očekávaný objem za den | `[DOPLNIT]` |
| Očekávaný počet nových záznamů za běh | `[DOPLNIT]` |

### Mapování na interní model

| Zdrojové pole | Interní pole | Poznámka |
|---|---|---|
| `[DOPLNIT]` | `external_id` | `[DOPLNIT]` |
| `[DOPLNIT]` | `source_url` | `[DOPLNIT]` |
| `[DOPLNIT]` | `canonical_url` | `[DOPLNIT]` |
| `[DOPLNIT]` | `published_at` | `[DOPLNIT]` |
| `[DOPLNIT]` | `author_handle` | `[DOPLNIT]` |
| `[DOPLNIT]` | `title` | `[DOPLNIT]` |
| `[DOPLNIT]` | `content` | `[DOPLNIT]` |
| `[DOPLNIT]` | `metrics` | `[DOPLNIT]` |
| `[DOPLNIT]` | `raw_metadata` | `[DOPLNIT]` |

### Deduplikace

Deduplikace probíhá podle:

- `[external_id]`,
- `[canonical_url]`,
- `[content_hash]`,
- `[jiné pravidlo]`.

Poznámky:

[DOPLNIT]

### Chybové stavy

| Chyba | Doporučená reakce |
|---|---|
| HTTP 429 | zpomalit / retry později |
| HTTP 403 | zkontrolovat oprávnění |
| HTTP 404 | označit záznam jako nedostupný |
| timeout | retry |
| nevalidní payload | uložit do processing_events |
| změna struktury | označit zdroj jako experimental nebo paused |

### Právní a provozní poznámky

[DOPLNIT]

Nutné ověřit:

- podmínky použití,
- možnost ukládání dat,
- možnost další analýzy dat,
- limity API,
- pravidla pro scraping,
- požadavky na atribuci,
- retenci dat.

### Testovací příklady

Ukázková URL nebo payload:

```json
{
  "example": "DOPLNIT"
}
```

### Poznámky k implementaci

[DOPLNIT]

### Stav implementace

- [ ] zdroj zdokumentován,
- [ ] ověřeny podmínky použití,
- [ ] vytvořen ingest modul,
- [ ] vytvořeny testy,
- [ ] otestována deduplikace,
- [ ] otestováno mapování polí,
- [ ] přidán monitoring chyb,
- [ ] připraveno pro produkční použití.
```

---

## Šablona pro RSS zdroj

```markdown
## RSS zdroj: [DOPLNIT]

### Základní informace

| Pole | Hodnota |
|---|---|
| Název | `[DOPLNIT]` |
| RSS URL | `[DOPLNIT]` |
| Web | `[DOPLNIT]` |
| Stav | `planned` |
| Frekvence | `1h` |
| Jazyk | `[cs / sk / en / other]` |

### Očekávaná pole

| RSS pole | Interní pole |
|---|---|
| `guid` | `external_id` |
| `link` | `source_url` |
| `title` | `title` |
| `description` | `content` nebo `raw_metadata.description` |
| `pubDate` | `published_at` |
| `author` | `author_handle` |

### Poznámky

[DOPLNIT]
```

---

## Šablona pro API zdroj

```markdown
## API zdroj: [DOPLNIT]

### Základní informace

| Pole | Hodnota |
|---|---|
| Název | `[DOPLNIT]` |
| API endpoint | `[DOPLNIT]` |
| Autentizace | `[DOPLNIT]` |
| Rate limit | `[DOPLNIT]` |
| Stav | `planned` |
| Frekvence | `[DOPLNIT]` |

### Povinné secrets

```text
[DOPLNIT]
```

### Paginace

[DOPLNIT]

### Ukázkový request

```http
GET [DOPLNIT]
Authorization: Bearer [TOKEN]
```

### Ukázkový response

```json
{
  "items": []
}
```

### Mapování

| API pole | Interní pole |
|---|---|
| `[DOPLNIT]` | `external_id` |
| `[DOPLNIT]` | `source_url` |
| `[DOPLNIT]` | `published_at` |
| `[DOPLNIT]` | `content` |

### Poznámky

[DOPLNIT]
```

---

## Šablona pro Apify zdroj

```markdown
## Apify zdroj: [DOPLNIT]

### Základní informace

| Pole | Hodnota |
|---|---|
| Actor | `[DOPLNIT]` |
| Dataset | `[DOPLNIT]` |
| Stav | `planned` |
| Frekvence | `[DOPLNIT]` |
| Očekávaný objem | `[DOPLNIT]` |

### Input konfigurace

```json
{
  "example": "DOPLNIT"
}
```

### Output struktura

```json
{
  "example": "DOPLNIT"
}
```

### Mapování

| Apify pole | Interní pole |
|---|---|
| `[DOPLNIT]` | `external_id` |
| `[DOPLNIT]` | `source_url` |
| `[DOPLNIT]` | `published_at` |
| `[DOPLNIT]` | `content` |
| `[DOPLNIT]` | `metrics` |
| celý objekt | `raw_metadata` |

### Poznámky

[DOPLNIT]
```

---

## Šablona pro ruční import

```markdown
## Ruční import: [DOPLNIT]

### Základní informace

| Pole | Hodnota |
|---|---|
| Formát | `[csv / json / jsonl]` |
| Zdroj dat | `[DOPLNIT]` |
| Stav | `planned` |
| Účel | `[DOPLNIT]` |

### Požadovaná struktura

| Pole | Povinné | Poznámka |
|---|---|---|
| `external_id` | ne | doporučeno |
| `source_url` | ne | doporučeno |
| `published_at` | ne | doporučeno |
| `title` | ne | volitelné |
| `content` | ano | hlavní text |
| `author_handle` | ne | volitelné |
| `source_platform` | ano | typ zdroje |

### Poznámky

[DOPLNIT]
```

---

## Evidenční tabulka zdrojů

Tuto tabulku doplňovat postupně.

| Název | Typ | Platforma | Stav | Frekvence | Priorita | Poznámka |
|---|---|---|---|---|---|---|
| `[DOPLNIT]` | `[DOPLNIT]` | `[DOPLNIT]` | `planned` | `[DOPLNIT]` | `[DOPLNIT]` | `[DOPLNIT]` |

---

## Checklist pro přidání nového zdroje

Před přidáním nového zdroje do produkční pipeline musí být splněno:

- [ ] zdroj má jasný účel,
- [ ] je znám typ zdroje,
- [ ] je znám způsob přístupu,
- [ ] jsou ověřeny technické limity,
- [ ] jsou ověřeny základní právní a provozní podmínky,
- [ ] je definována frekvence sběru,
- [ ] je definováno mapování na interní model,
- [ ] je definována deduplikace,
- [ ] jsou ošetřeny chybové stavy,
- [ ] existuje testovací payload,
- [ ] existuje ingest modul,
- [ ] existují základní testy,
- [ ] chyby se ukládají do `processing_events`,
- [ ] běhy se ukládají do `collection_runs`.

---

## Doporučené minimum pro MVP

Pro první verzi systému je vhodné začít s jednoduchými a stabilními zdroji:

- RSS zpravodajských webů,
- ruční JSON/CSV import,
- jeden jednoduchý API zdroj,
- jeden experimentální Apify zdroj.

Až po stabilizaci pipeline přidávat složitější zdroje.
