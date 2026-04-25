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