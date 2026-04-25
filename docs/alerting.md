# Alerting: SocialScanner

Tento dokument popisuje návrh alerting systému v projektu **SocialScanner**.

Alerting slouží k tomu, aby systém dokázal včas upozornit na důležité změny v online prostoru, zejména na vznikající reputační rizika, negativní trendy, nové narativy a rychle se šířící témata.

---

## Cíl alertingu

Alerting má odpovědět na otázku:

```text
Je aktuální situace natolik důležitá, že má být zákazník upozorněn?
```

Alerting nesmí být pouze mechanické posílání notifikací při každé změně.

Dobrý alerting musí:

- minimalizovat šum,
- upozorňovat pouze na relevantní situace,
- rozlišovat závažnost,
- deduplikovat podobné alerty,
- sledovat životní cyklus incidentu,
- ukládat důvody vzniku alertu,
- umožnit pozdější audit a vyhodnocení.

---

## Typy alertů

Doporučené hodnoty `alert_type`:

| Typ | Popis |
|---|---|
| `mention_spike` | Náhlý růst počtu zmínek |
| `negative_sentiment_spike` | Náhlý růst negativního sentimentu |
| `risk_score_spike` | Náhlý růst rizikového skóre |
| `new_topic` | Detekce nového tématu |
| `cross_platform_spread` | Šíření tématu přes více platforem |
| `news_pickup` | Převzetí tématu zpravodajskými weby |
| `high_engagement` | Vysoký engagement konkrétního obsahu |
| `manual` | Ručně vytvořený alert |
| `other` | Jiný typ alertu |

---

## Severity

Severity určuje závažnost alertu.

Doporučené hodnoty:

| Severity | Význam |
|---|---|
| `info` | Informační upozornění |
| `low` | Nízká důležitost |
| `medium` | Střední důležitost |
| `high` | Vysoká důležitost |
| `critical` | Kritická situace |

---

## Stav alertu

Doporučené hodnoty `status`:

| Stav | Význam |
|---|---|
| `open` | Alert je aktivní |
| `acknowledged` | Alert byl vzat na vědomí |
| `resolved` | Situace byla vyřešena nebo odezněla |
| `ignored` | Alert byl označen jako nerelevantní |

---

## Životní cyklus alertu

```text
open
  ↓
acknowledged
  ↓
resolved
```

Alternativně:

```text
open
  ↓
ignored
```

---

## Vznik alertu

Alert může vzniknout pouze tehdy, když je splněna alespoň jedna definovaná podmínka.

Příklad:

```text
trend_score >= 0.70
risk_score >= 0.70
anomaly_score >= 3.0
negative_ratio >= 0.60
cross_platform_score >= 0.60
```

Přesné prahy musí být laděny podle historických dat, typu zákazníka a citlivosti monitorované entity.

---

# Alert pravidla

## 1. Mention spike

Vzniká při neobvyklém růstu počtu zmínek.

Možné pravidlo:

```text
current_mentions >= baseline_mentions * 3
AND current_mentions >= minimum_mentions
```

Doporučené vstupy:

- aktuální počet zmínek,
- baseline,
- growth ratio,
- anomaly score,
- trend score.

---

## 2. Negative sentiment spike

Vzniká při rychlém růstu negativního sentimentu.

Možné pravidlo:

```text
negative_ratio >= 0.60
AND mention_count >= minimum_mentions
AND avg_sentiment_score <= -0.40
```

Doporučené vstupy:

- počet negativních zmínek,
- podíl negativních zmínek,
- průměrný sentiment,
- entity-level sentiment,
- trend score.

---

## 3. Risk score spike

Vzniká při vysokém rizikovém skóre.

Možné pravidlo:

```text
avg_risk_score >= 0.75
OR risk_score_delta >= 0.40
```

Doporučené vstupy:

- dokumentové risk score,
- entity-level risk score,
- trend-level risk score,
- toxicita,
- engagement,
- autorita zdroje.

---

## 4. New topic

Vzniká při objevení nového významného tématu.

Možné pravidlo:

```text
topic_is_new = true
AND topic_document_count >= minimum_documents
AND topic_relevance_score >= 0.70
```

Doporučené vstupy:

- počet dokumentů v topic clusteru,
- relevance tématu,
- novost tématu,
- vazba na sledovanou entitu,
- sentiment tématu.

---

## 5. Cross-platform spread

Vzniká, pokud se téma šíří přes více platforem.

Možné pravidlo:

```text
unique_source_count >= 3
AND time_between_platforms <= 6 hours
AND trend_score >= 0.60
```

Doporučené vstupy:

- počet platforem,
- čas prvního výskytu na každé platformě,
- rychlost šíření,
- engagement,
- podobnost obsahu.

---

## 6. News pickup

Vzniká, pokud se téma dostane do zpravodajských webů.

Možné pravidlo:

```text
previously_social_only = true
AND new_source_type = news
AND entity_is_tracked = true
```

Použití:

- krizové řízení,
- PR reakce,
- monitoring reputace.

---

## 7. High engagement

Vzniká při vysokém engagementu jednoho nebo více dokumentů.

Možné pravidlo:

```text
document_engagement >= baseline_engagement * 5
AND entity_is_tracked = true
```

Použití:

- virální příspěvky,
- vlivné účty,
- rychle rostoucí komentáře,
- potenciální mediální dopad.

---

# Severity model

Severity by měla být odvozena z kombinace signálů.

## Doporučený přístup

```text
severity_score =
    0.35 * risk_score +
    0.25 * trend_score +
    0.20 * anomaly_score_normalized +
    0.10 * cross_platform_score +
    0.10 * source_authority_score
```

Výsledné mapování:

| Score | Severity |
|---|---|
| `0.00 - 0.20` | `info` |
| `0.20 - 0.40` | `low` |
| `0.40 - 0.60` | `medium` |
| `0.60 - 0.80` | `high` |
| `0.80 - 1.00` | `critical` |

---

# Deduplikace alertů

Bez deduplikace by systém mohl vytvořit mnoho podobných alertů pro stejnou situaci.

## Alert identity

Doporučený klíč pro deduplikaci:

```text
tenant_id + alert_type + entity_id/topic_id + time_bucket
```

Příklad:

```text
tenant_123 + negative_sentiment_spike + entity_456 + 2026-01-01T10:00
```

---

## Kdy nevytvářet nový alert

Nový alert nevytvářet, pokud:

- existuje otevřený alert stejného typu,
- týká se stejné entity nebo tématu,
- vznikl v nedávném časovém okně,
- aktuální událost je pokračováním stejného trendu.

Místo toho aktualizovat existující alert.

---

## Aktualizace alertu

Existující alert aktualizovat, pokud:

- roste severity,
- roste risk score,
- přibývají nové platformy,
- téma přešlo do médií,
- počet zmínek výrazně narostl,
- změnila se doporučená reakce.

Aktualizovat pole:

- `last_updated_at`,
- `risk_score`,
- `trend_score`,
- `anomaly_score`,
- `severity`,
- `alert_payload`.

---

# Alert payload

`alert_payload` obsahuje detailní strojově čitelné vysvětlení alertu.

Příklad:

```json
{
  "reason": "Negative sentiment spike detected",
  "signals": {
    "mention_count": 124,
    "baseline_mentions": 18,
    "growth_ratio": 6.88,
    "negative_ratio": 0.72,
    "avg_sentiment_score": -0.61,
    "trend_score": 0.82,
    "risk_score": 0.79,
    "anomaly_score": 3.4
  },
  "top_terms": [
    "výpadek",
    "stížnost",
    "nefunguje"
  ],
  "top_sources": [
    "rss_news",
    "forum",
    "social"
  ],
  "sample_documents": [
    "document_id_1",
    "document_id_2"
  ]
}
```

---

# Doporučený obsah alertu pro uživatele

Každý alert by měl obsahovat:

- název,
- krátké shrnutí,
- typ alertu,
- severity,
- sledovanou entitu nebo téma,
- kdy byl poprvé detekován,
- proč vznikl,
- hlavní signály,
- ukázkové dokumenty,
- doporučenou další akci,
- odkaz do dashboardu.

---

## Příklad alertu

```text
Název:
Rychlý růst negativních zmínek o produktu X

Shrnutí:
Za poslední 3 hodiny vzrostl počet negativních zmínek o produktu X o 420 % oproti běžnému stavu. Téma se začalo šířit z diskusního fóra na sociální sítě.

Severity:
high

Důvod:
negative_sentiment_spike + cross_platform_spread

Doporučená akce:
Zkontrolovat hlavní zdroje, připravit reakci zákaznické podpory a ověřit, zda problém souvisí s reálným výpadkem služby.
```

---

# Kanály notifikací

Budoucí notifikační kanály:

- dashboard,
- e-mail,
- Slack,
- Microsoft Teams,
- webhook,
- interní API,
- denní report.

---

## E-mail alert

Vhodný pro:

- denní přehled,
- high a critical alerty,
- manažerské souhrny.

Nevhodný pro:

- příliš časté malé změny,
- debug notifikace,
- nízkou prioritu.

---

## Slack / Teams alert

Vhodný pro:

- operativní týmy,
- PR tým,
- crisis management,
- zákaznickou podporu.

---

## Webhook alert

Vhodný pro:

- integrace do externích systémů,
- vlastní dashboardy zákazníka,
- incident management nástroje.

---

# Rate limiting alertů

Alerting musí chránit uživatele před zahlcením.

Doporučená pravidla:

- neposílat stejný alert vícekrát během krátkého okna,
- aktualizovat existující alert místo vytváření nového,
- seskupovat podobné alerty,
- posílat low severity pouze do dashboardu,
- posílat high/critical přes aktivní kanály.

---

# Escalation model

Severity se může v čase změnit.

Příklad:

```text
10:00 low
10:30 medium
11:15 high
12:00 critical
```

K eskalaci může dojít, pokud:

- trend dále roste,
- přidávají se nové platformy,
- objevují se zpravodajské články,
- zvyšuje se engagement,
- sentiment se zhoršuje,
- téma zasahuje důležitou entitu.

---

# Auto-resolve pravidla

Alert lze automaticky uzavřít, pokud:

- trend odezněl,
- mention count se vrátil k baseline,
- risk score klesl pod práh,
- po určitou dobu nepřišly nové relevantní zmínky,
- uživatel alert ručně označil jako vyřešený.

Příklad:

```text
resolve if:
risk_score < 0.30
AND trend_score < 0.30
AND no_new_documents_for >= 24h
```

---

# Ignored alert

Alert označený jako `ignored` znamená, že nebyl relevantní.

Tato informace je důležitá pro budoucí ladění pravidel.

U ignored alertu je vhodné ukládat důvod:

- falešná shoda entity,
- známá plánovaná kampaň,
- nerelevantní zdroj,
- příliš nízký dopad,
- spam,
- špatný sentiment model.

---

# Audit alertů

Každý alert musí být zpětně vysvětlitelný.

Musí být možné dohledat:

- proč alert vznikl,
- jaká data ho způsobila,
- jaké metriky překročily práh,
- kdy byl alert aktualizován,
- kdo ho acknowledged,
- kdo ho resolved,
- zda byl ignorován.

---

# Databázové uložení

Alerty se ukládají do tabulky `alerts`.

Doporučená pole:

- `id`,
- `tenant_id`,
- `entity_id`,
- `topic_id`,
- `title`,
- `description`,
- `alert_type`,
- `severity`,
- `status`,
- `risk_score`,
- `trend_score`,
- `anomaly_score`,
- `first_detected_at`,
- `last_updated_at`,
- `acknowledged_at`,
- `resolved_at`,
- `alert_payload`,
- `created_at`.

---

# Minimální MVP alerting

Pro první verzi stačí implementovat:

- `mention_spike`,
- `negative_sentiment_spike`,
- `risk_score_spike`,
- základní severity,
- deduplikaci otevřených alertů,
- ukládání alertů do databáze,
- ruční změnu stavu alertu,
- denní souhrn alertů.

---

# Checklist alertingu

Před produkčním použitím ověřit:

- [ ] alerty mají jasně definované typy,
- [ ] severity je vysvětlitelná,
- [ ] existuje deduplikace,
- [ ] alerty se neodesílají příliš často,
- [ ] alert obsahuje důvod vzniku,
- [ ] alert obsahuje podpůrná data,
- [ ] alert lze acknowledged,
- [ ] alert lze resolved,
- [ ] alert lze ignored,
- [ ] ignored alerty lze použít pro ladění pravidel,
- [ ] high a critical alerty mají aktivní notifikaci,
- [ ] low alerty nezahltí uživatele.

---

# Budoucí rozšíření

Alerting lze rozšířit o:

- automatická doporučení reakce,
- generování krizového briefu,
- notifikace podle rolí,
- tiché hodiny,
- SLA pro reakci,
- incident timeline,
- propojení s ticketing systémem,
- ruční komentáře k alertu,
- model predikce eskalace,
- automatické porovnání s historickými incidenty.
