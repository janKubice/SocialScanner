# Trend Detection: SocialScanner

Tento dokument popisuje návrh detekce trendů v projektu **SocialScanner**.

Trend detection je analytická vrstva, která sleduje změny v online zmínkách, sentimentu, riziku a šíření témat. Jejím cílem je rozlišit běžný šum od situace, která může být důležitá pro zákazníka.

---

## Cíl trend detection

Trend detection má odpovídat na otázky:

- Zvyšuje se počet zmínek o entitě?
- Roste negativní sentiment?
- Vzniká nové téma?
- Šíří se obsah mezi platformami?
- Je růst neobvyklý oproti historickému baseline?
- Jde o běžný šum, nebo potenciální problém?
- Má vzniknout alert?
- Jak silný je trend?
- Jak rychle trend roste?
- Jaké zdroje trend zesilují?

---

## Co je trend

Trend je významná změna v datech oproti běžnému chování.

Trend může být založen na:

- objemu zmínek,
- rychlosti růstu,
- sentimentu,
- rizikovém skóre,
- engagementu,
- počtu unikátních zdrojů,
- počtu unikátních autorů,
- přesunu mezi platformami,
- výskytu nových frází,
- výskytu v médiích,
- vzniku nového tématu.

---

## Typy trendů

### 1. Mention spike

Náhlý růst počtu zmínek.

Příklad:

```text
Běžný stav: 5 zmínek za hodinu
Aktuální stav: 80 zmínek za hodinu
```

---

### 2. Negative sentiment spike

Náhlý růst negativních zmínek.

Příklad:

```text
Běžný podíl negativních zmínek: 15 %
Aktuální podíl negativních zmínek: 65 %
```

---

### 3. Risk score spike

Náhlý růst reputačního rizika.

Příklad:

```text
Běžný risk score: 0.20
Aktuální risk score: 0.82
```

---

### 4. New topic

Objeví se nové téma, které předtím nebylo v datech významně přítomné.

Příklad:

- nová stížnost na produkt,
- nová kauza,
- nový hashtag,
- nové viralizované tvrzení,
- nový narativ.

---

### 5. Cross-platform spread

Téma se začne šířit mezi více platformami.

Příklad:

```text
Fáze 1: diskusní fórum
Fáze 2: sociální síť
Fáze 3: zpravodajský web
```

---

### 6. News pickup

Téma se dostane do zpravodajských médií.

Příklad:

```text
Původně: sociální sítě
Nově: článek na zpravodajském webu
```

---

### 7. High engagement trend

Téma nemá extrémně mnoho zmínek, ale získává vysoký engagement.

Příklad:

- jeden příspěvek s vysokým počtem sdílení,
- článek s vysokým dosahem,
- video s rychlým růstem komentářů.

---

## Časová okna

Trend detection by měla pracovat s více časovými okny.

| Okno | Použití |
|---|---|
| `1h` | Live monitoring |
| `3h` | Krátkodobý vývoj |
| `6h` | Rychle vznikající trendy |
| `24h` | Denní přehled |
| `7d` | Krátkodobý baseline |
| `30d` | Stabilnější baseline |
| `90d` | Dlouhodobé chování |

---

## Základní metriky

### Mention count

Počet zmínek v daném časovém okně.

```text
mention_count
```

---

### Negative count

Počet negativních zmínek v daném časovém okně.

```text
negative_count
```

---

### Negative ratio

Podíl negativních zmínek.

```text
negative_ratio = negative_count / mention_count
```

---

### Average sentiment

Průměrný sentiment.

```text
avg_sentiment_score
```

Rozsah:

```text
-1.0 až 1.0
```

---

### Average risk

Průměrné riziko.

```text
avg_risk_score
```

Rozsah:

```text
0.0 až 1.0
```

---

### Unique authors

Počet unikátních autorů.

```text
unique_author_count
```

---

### Unique sources

Počet unikátních zdrojů nebo platforem.

```text
unique_source_count
```

---

### Engagement

Souhrnná metrika engagementu.

Může zahrnovat:

- likes,
- shares,
- comments,
- views,
- reposts,
- reactions.

```text
total_engagement
```

---

## Baseline

Baseline je očekávané normální chování.

Příklad:

```text
Entita má běžně 10–20 zmínek denně.
```

Pokud najednou získá 300 zmínek za den, jde pravděpodobně o trend.

---

## Typy baseline

### 1. Rolling average

Klouzavý průměr za poslední období.

Příklad:

```text
baseline_7d = průměr zmínek za posledních 7 dní
baseline_30d = průměr zmínek za posledních 30 dní
```

---

### 2. Median baseline

Medián je robustnější vůči extrémům.

Příklad:

```text
baseline = medián denních zmínek za posledních 30 dní
```

---

### 3. Platform-specific baseline

Každá platforma může mít jiné normální chování.

Příklad:

```text
Zpravodajské weby: 2 zmínky denně
Sociální sítě: 50 zmínek denně
Diskusní fóra: 10 zmínek denně
```

---

### 4. Entity-specific baseline

Každá entita má vlastní normální chování.

Velká značka může mít stovky zmínek denně. Malá značka může mít běžně nula zmínek.

---

## Velocity

Velocity vyjadřuje rychlost růstu.

```text
velocity = current_count - previous_count
```

Příklad:

```text
Předchozí hodina: 10 zmínek
Aktuální hodina: 50 zmínek
Velocity: +40
```

---

## Growth ratio

Growth ratio porovnává aktuální stav s baseline.

```text
growth_ratio = current_count / baseline_count
```

Příklad:

```text
current_count = 100
baseline_count = 20
growth_ratio = 5.0
```

---

## Acceleration

Acceleration měří změnu rychlosti růstu.

```text
acceleration = current_velocity - previous_velocity
```

Použití:

- detekce viralizace,
- odlišení stabilního růstu od prudkého nástupu,
- včasné zachycení krizové vlny.

---

## Anomaly score

Anomaly score vyjadřuje, jak moc je aktuální stav neobvyklý.

Doporučený rozsah:

```text
0.0 až neomezeně
```

Příklad interpretace:

| Hodnota | Význam |
|---|---|
| `0.0 - 1.0` | běžný stav |
| `1.0 - 2.0` | mírná odchylka |
| `2.0 - 3.0` | výrazná odchylka |
| `3.0+` | silná anomálie |

---

## Trend score

Trend score převádí více signálů na jednu hodnotu.

Doporučený rozsah:

```text
0.0 až 1.0
```

Možné signály:

- mention growth,
- velocity,
- acceleration,
- engagement growth,
- unique author growth,
- unique source growth,
- cross-platform spread,
- novelty.

Příklad interpretace:

| Trend score | Význam |
|---|---|
| `0.0 - 0.2` | bez trendu |
| `0.2 - 0.4` | slabý trend |
| `0.4 - 0.6` | viditelný trend |
| `0.6 - 0.8` | silný trend |
| `0.8 - 1.0` | velmi silný trend |

---

## Risk score

Risk score vyjadřuje potenciální škodu nebo důležitost trendu.

Doporučený rozsah:

```text
0.0 až 1.0
```

Možné signály:

- negativní sentiment,
- toxicita,
- výskyt krizových slov,
- spojení se sledovanou entitou,
- rychlost šíření,
- autorita zdrojů,
- engagement,
- výskyt v médiích,
- historická podobnost s krizemi.

Příklad interpretace:

| Risk score | Význam |
|---|---|
| `0.0 - 0.2` | nízké riziko |
| `0.2 - 0.4` | mírné riziko |
| `0.4 - 0.6` | střední riziko |
| `0.6 - 0.8` | vysoké riziko |
| `0.8 - 1.0` | kritické riziko |

---

## Doporučený výpočet pro MVP

Pro první verzi lze použít jednoduchý scoring.

### Mention growth score

```text
mention_growth_score = min(current_count / max(baseline_count, 1), 10) / 10
```

### Negative ratio score

```text
negative_ratio_score = negative_count / max(mention_count, 1)
```

### Engagement score

```text
engagement_score = min(current_engagement / max(baseline_engagement, 1), 10) / 10
```

### Cross-platform score

```text
cross_platform_score = min(unique_source_count / 5, 1)
```

### Trend score

```text
trend_score =
    0.40 * mention_growth_score +
    0.25 * engagement_score +
    0.20 * cross_platform_score +
    0.15 * novelty_score
```

### Risk score

```text
risk_score =
    0.40 * negative_ratio_score +
    0.25 * avg_toxicity_score +
    0.20 * trend_score +
    0.15 * source_authority_score
```

Tyto vzorce jsou pouze počáteční návrh a měly by být upraveny podle reálných dat.

---

## Trend snapshot

Agregované výsledky se ukládají do `trend_snapshots`.

Doporučená pole:

- `tenant_id`,
- `entity_id`,
- `topic_id`,
- `window_start`,
- `window_end`,
- `window_granularity`,
- `mention_count`,
- `positive_count`,
- `neutral_count`,
- `negative_count`,
- `unique_author_count`,
- `unique_source_count`,
- `total_engagement`,
- `avg_sentiment_score`,
- `avg_risk_score`,
- `trend_score`,
- `anomaly_score`,
- `top_terms`,
- `top_sources`.

---

# Detekce nového tématu

Nové téma lze detekovat pomocí:

- keyword burst,
- embedding clustering,
- LLM sumarizace,
- neobvykle častých frází,
- podobnosti dokumentů,
- výskytu nových hashtagů.

## Příklad procesu

1. Vybrat nové dokumenty za poslední okno.
2. Vytvořit embeddingy.
3. Seskupit podobné dokumenty.
4. Z clusterů extrahovat reprezentativní fráze.
5. Porovnat s existujícími tématy.
6. Pokud je téma nové a dostatečně silné, vytvořit záznam v `topics`.
7. Přiřadit dokumenty do `document_topics`.

---

# Cross-platform spread

Cross-platform spread sleduje, zda se téma přesouvá mezi různými typy zdrojů.

Příklad:

```text
0:00 Fórum
1:30 X / sociální síť
3:00 Telegram
5:00 Zpravodajský web
```

Signály:

- počet platforem,
- čas mezi prvními výskyty,
- autorita platformy,
- růst engagementu,
- opakující se URL nebo fráze.

---

# Propagation model

Pro mapování šíření lze využít `document_relations`.

Doporučené vztahy:

- `same_url`,
- `links_to`,
- `repost_of`,
- `quote_of`,
- `reply_to`,
- `near_duplicate`,
- `semantic_similarity`,
- `same_topic`.

Cílem není absolutně dokázat původ trendu, ale určit:

- první zachycený výskyt,
- pravděpodobné akcelerátory,
- hlavní zdroje šíření,
- platformy, přes které se téma přesouvalo.

---

# Minimální pravidla pro alerting

Trend by měl být kandidátem na alert, pokud splňuje některou z podmínek:

```text
trend_score >= 0.70
risk_score >= 0.70
anomaly_score >= 3.0
negative_ratio >= 0.60 AND mention_count >= minimální práh
cross_platform_score >= 0.60
```

Přesné prahy musí být laděny podle reálných dat.

---

# Falešné pozitivní signály

Trend detection musí počítat s falešnými pozitivy.

Příklady:

- pravidelná marketingová kampaň,
- plánovaná tisková zpráva,
- sezónní téma,
- sportovní nebo kulturní událost,
- spam,
- bot aktivita,
- jednorázový virální příspěvek bez relevance,
- obecné slovo shodné s názvem entity.

---

# Checklist trend detection

Před nasazením ověřit:

- [ ] existují historická data pro baseline,
- [ ] entity mají dostatečně kvalitní aliasy,
- [ ] zmínky jsou deduplikované,
- [ ] sentiment není počítán pouze na úrovni dokumentu,
- [ ] trend score je vysvětlitelné,
- [ ] risk score je vysvětlitelné,
- [ ] alerty nejsou příliš časté,
- [ ] existuje možnost ručního označení falešného alertu,
- [ ] existuje možnost zpětně vyhodnotit přesnost.

---

# Budoucí rozšíření

Trend detection lze rozšířit o:

- detekci koordinovaného šíření,
- graph-based propagation,
- historickou podobnost krizí,
- automatické doporučení reakce,
- sezónní baseline,
- oddělené baseline podle platformy,
- oddělené baseline podle pracovních dnů a víkendů,
- model pro predikci eskalace,
- LLM vysvětlení trendu,
- simulaci možného dalšího vývoje.
