# Entity model: SocialScanner

Tento dokument popisuje práci s entitami v projektu **SocialScanner**.

Entity jsou jeden ze základních konceptů systému. Umožňují sledovat značky, firmy, osoby, produkty, témata, hashtagy, instituce a další objekty, které se objevují ve veřejném online prostoru.

---

## Cíl entity modelu

Entity model má umožnit:

- sledování konkrétních zákaznických značek,
- sledování konkurence,
- vyhodnocení sentimentu vůči entitám,
- detekci reputačních rizik,
- trend detection,
- alerting,
- reporting,
- sémantické vyhledávání,
- práci s aliasy, překlepy a neoficiálními názvy.

---

## Co je entita

Entita je pojmenovaný objekt, který má význam pro analytiku.

Příklady entit:

- firma,
- značka,
- produkt,
- osoba,
- instituce,
- politická strana,
- událost,
- kampaň,
- hashtag,
- doména,
- lokace,
- obecné téma.

---

## Sledovaná vs. extrahovaná entita

V systému existují dva hlavní typy entit podle způsobu použití.

---

### Sledovaná entita

Sledovaná entita je entita, kterou zákazník aktivně monitoruje.

Příklady:

- vlastní značka zákazníka,
- produkt zákazníka,
- jméno CEO,
- konkurent,
- klíčová kampaň,
- důležité téma.

V databázi:

```text
is_tracked = true
```

Použití:

- dashboard,
- alerting,
- trend detection,
- reporting,
- reputační skóre.

---

### Extrahovaná entita

Extrahovaná entita je entita, která byla nalezena v textu, ale nemusí být aktivně sledovaná.

Příklady:

- město zmíněné v článku,
- vedlejší osoba,
- obecný hashtag,
- instituce v textu,
- produkt zmíněný okrajově.

V databázi:

```text
is_tracked = false
```

Použití:

- kontext,
- vyhledávání,
- topic modeling,
- vztahy mezi entitami,
- budoucí rozšíření sledování.

---

## Typy entit

Doporučené hodnoty `entity_type`:

| Typ | Popis |
|---|---|
| `brand` | Značka |
| `company` | Firma |
| `person` | Osoba |
| `product` | Produkt |
| `organization` | Organizace |
| `institution` | Veřejná nebo formální instituce |
| `political_party` | Politická strana nebo hnutí |
| `event` | Událost |
| `topic` | Obecné téma |
| `hashtag` | Hashtag |
| `domain` | Webová doména |
| `location` | Místo |
| `other` | Jiný typ |

---

## Základní struktura entity

Entita by měla obsahovat:

| Pole | Popis |
|---|---|
| `id` | Interní UUID entity |
| `tenant_id` | Tenant, kterému entita patří |
| `entity_name` | Zobrazovaný název |
| `normalized_name` | Normalizovaný název pro matching |
| `entity_type` | Typ entity |
| `description` | Volitelný popis |
| `is_tracked` | Zda je entita aktivně sledovaná |
| `is_active` | Zda je entita aktivní |
| `metadata` | Doplňující metadata |

---

## Normalizace názvu

Normalizace slouží ke stabilnímu porovnávání názvů.

Doporučené kroky:

- převod na lowercase,
- odstranění přebytečných mezer,
- sjednocení diakritiky podle pravidel projektu,
- odstranění prefixu `#` u hashtagů,
- odstranění běžných právních suffixů, pokud je to vhodné,
- sjednocení interpunkce,
- trim.

Příklad:

| Původní název | Normalizovaný název |
|---|---|
| `Škoda Auto` | `skoda auto` |
| `#Škoda` | `skoda` |
| `Česká Spořitelna` | `ceska sporitelna` |
| `Open AI` | `open ai` |
| `  ChatGPT  ` | `chatgpt` |

---

## Aliasy

Aliasy jsou alternativní názvy entity.

Příklady:

| Entita | Alias |
|---|---|
| `Škoda Auto` | `Škodovka` |
| `Škoda Auto` | `Skoda` |
| `Česká spořitelna` | `Spořka` |
| `Česká spořitelna` | `ČS` |
| `OpenAI` | `ChatGPT` |
| `OpenAI` | `GPT` |

---

## Typy aliasů

Doporučené hodnoty `alias_type`:

| Typ | Popis |
|---|---|
| `manual` | Ručně zadaný alias |
| `generated` | Automaticky vygenerovaný alias |
| `imported` | Importovaný alias |
| `detected` | Alias zjištěný z dat |

---

## Kdy alias přidat

Alias přidat, pokud:

- se název běžně používá,
- se často objevuje v datech,
- jde o zkratku,
- jde o název bez diakritiky,
- jde o slangový název,
- jde o překlep, který se opakuje,
- jde o hashtagovou variantu,
- jde o starý název značky.

---

## Kdy alias nepřidávat

Alias nepřidávat, pokud:

- je příliš obecný,
- způsobuje mnoho falešných shod,
- odpovídá více entitám,
- je příliš krátký bez kontextu,
- je jednorázový a analyticky nevýznamný.

Příklad rizikového aliasu:

```text
CS
```

Může znamenat:

- Česká spořitelna,
- Counter-Strike,
- computer science,
- zákaznický servis,
- jiné zkratky.

Takový alias by měl být použit pouze s kontextovým pravidlem.

---

# Matching strategie

Entity matching je proces přiřazení entity k dokumentu.

## 1. Exact match

Přímé hledání názvu entity v textu.

Výhody:

- jednoduché,
- rychlé,
- vysvětlitelné.

Nevýhody:

- nepozná skloňování,
- nepozná překlepy,
- nepozná neoficiální názvy,
- může vytvářet falešné shody.

---

## 2. Alias match

Hledání podle aliasů.

Výhody:

- zachytí běžné varianty,
- zachytí slang,
- zachytí zkratky,
- zachytí názvy bez diakritiky.

Nevýhody:

- riziko falešných shod,
- nutnost spravovat aliasy,
- některé aliasy vyžadují kontext.

---

## 3. Regex match

Vhodné pro složitější pravidla.

Použití:

- hashtagy,
- názvy s variantami,
- produktové kódy,
- domény,
- konkrétní fráze.

Příklad:

```regex
\b(skoda|škoda|skodovka|škodovka)\b
```

---

## 4. NER model

Named Entity Recognition model detekuje entity v textu automaticky.

Výhody:

- umí najít nové entity,
- nepotřebuje přesný seznam aliasů,
- vhodné pro osoby, organizace a lokace.

Nevýhody:

- může být nepřesný,
- potřebuje jazykovou podporu,
- horší pro slang a značky,
- výsledky je vhodné validovat.

---

## 5. LLM matching

LLM lze použít pro složitější případy.

Použití:

- kontextové rozpoznání entity,
- rozlišení nejednoznačných aliasů,
- detekce implicitních zmínek,
- sumarizace vztahu entity k textu,
- výpočet sentimentu vůči entitě.

Nevýhody:

- vyšší cena,
- latence,
- potřeba validace,
- riziko nekonzistentních výsledků.

---

## 6. Manual match

Ruční přiřazení entity.

Použití:

- opravy,
- trénovací data,
- validace modelů,
- důležité incidenty.

---

# Vazba dokumentu na entitu

Vazba se ukládá do `document_entities`.

Doporučená pole:

| Pole | Popis |
|---|---|
| `data_id` | Dokument |
| `entity_id` | Entita |
| `tenant_id` | Tenant |
| `sentiment_score` | Sentiment vůči entitě |
| `relevance_score` | Relevance entity v dokumentu |
| `risk_score` | Riziko v kontextu entity |
| `occurrence_count` | Počet výskytů |
| `detection_method` | Metoda detekce |
| `matched_text` | Nalezený text |
| `context_snippet` | Krátký kontext |

---

## Relevance score

Relevance score určuje, jak důležitá je entita v dokumentu.

Doporučený rozsah:

```text
0.0 až 1.0
```

Příklady:

| Situace | Relevance |
|---|---|
| Entita je hlavním tématem článku | `0.9 - 1.0` |
| Entita je zmíněna opakovaně | `0.6 - 0.8` |
| Entita je zmíněna pouze okrajově | `0.2 - 0.4` |
| Entita je nejistá shoda | `0.0 - 0.2` |

---

## Entity-level sentiment

Entity-level sentiment se liší od celkového sentimentu dokumentu.

Příklad:

Text může být celkově negativní, ale vůči jedné konkrétní entitě neutrální.

Proto se ukládá:

- `raw_social_data.sentiment_score` pro celý dokument,
- `document_entities.sentiment_score` pro konkrétní entitu.

Doporučený rozsah:

```text
-1.0 až 1.0
```

---

## Entity-level risk score

Risk score vyjadřuje riziko spojené s danou entitou v konkrétním dokumentu.

Signály:

- negativní sentiment,
- toxicita,
- výskyt krizových slov,
- kontext stížnosti,
- engagement,
- typ zdroje,
- autorita zdroje,
- napojení na trend,
- opakování ve více zdrojích.

Doporučený rozsah:

```text
0.0 až 1.0
```

---

# Konflikty a nejednoznačnost

Některé názvy mohou odpovídat více entitám.

Příklad:

```text
Apple
```

Může znamenat:

- technologickou firmu,
- ovoce,
- produktový brand,
- součást názvu jiného subjektu.

## Řešení

Používat kontextové signály:

- okolní slova,
- typ zdroje,
- jazyk,
- související entity,
- doména,
- hashtagy,
- kategorie dokumentu,
- LLM ověření.

---

# Doporučený proces přidání sledované entity

1. Vytvořit záznam v `entities`.
2. Nastavit `is_tracked = true`.
3. Nastavit správný `entity_type`.
4. Doplnit popis.
5. Přidat hlavní aliasy.
6. Přidat varianty bez diakritiky.
7. Přidat běžné zkratky.
8. Přidat hashtagy.
9. Otestovat matching na historických datech.
10. Zkontrolovat falešné shody.
11. Nastavit alerting pravidla.
12. Přidat entitu do dashboardu.

---

# Příklad entity

```json
{
  "entity_name": "Škoda Auto",
  "normalized_name": "skoda auto",
  "entity_type": "company",
  "is_tracked": true,
  "is_active": true,
  "metadata": {
    "country": "CZ",
    "industry": "automotive"
  }
}
```

Aliasy:

```json
[
  {
    "alias": "Škodovka",
    "normalized_alias": "skodovka",
    "alias_type": "manual"
  },
  {
    "alias": "Skoda",
    "normalized_alias": "skoda",
    "alias_type": "manual"
  },
  {
    "alias": "#skoda",
    "normalized_alias": "skoda",
    "alias_type": "manual"
  }
]
```

---

# Checklist entity modelu

Před aktivním sledováním entity ověřit:

- [ ] entita má správný typ,
- [ ] entita má normalizovaný název,
- [ ] entita má hlavní aliasy,
- [ ] aliasy nejsou příliš obecné,
- [ ] aliasy byly otestovány na vzorku dat,
- [ ] falešné shody jsou přijatelné,
- [ ] je možné počítat entity-level sentiment,
- [ ] je možné počítat entity-level risk score,
- [ ] entita je napojena na trend detection,
- [ ] entita je napojena na alerting.

---

# Budoucí rozšíření

Entity model lze rozšířit o:

- hierarchii entit,
- vztahy mezi entitami,
- vlastnictví značek,
- konkurenty,
- automatické návrhy aliasů,
- automatickou detekci nových entit,
- ruční schvalování entit,
- entity knowledge graph,
- zákaznické skupiny entit,
- export entit do reportů.
