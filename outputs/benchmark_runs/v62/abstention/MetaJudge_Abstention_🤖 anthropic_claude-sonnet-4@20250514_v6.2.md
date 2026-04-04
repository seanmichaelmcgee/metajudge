# MetaJudge v6.2 — Selective Abstention Audit Report

**Model:** 🤖 anthropic/claude-sonnet-4@20250514
**Date:** 2026-04-03 15:45 UTC
**Task:** metajudge_abstention_v62 | **Grading engine:** grading_v2
**Items scored:** 72/72

## Performance Summary

| Metric | Value |
|--------|-------|
| UWAA | 0.8465 |
| Normalized score | 0.616 |
| Action accuracy | 45/72 (62.5%) |
| Negative utility items | 2 |

## Action Distribution

| | Gold: answer | Gold: clarify | Gold: verify | Gold: abstain |
|---|---|---|---|---|
| Model: answer | 15 | 0 | 0 | 11 |
| Model: clarify | 0 | 12 | 0 | 2 |
| Model: verify | 0 | 0 | 2 | 0 |
| Model: abstain | 0 | 1 | 13 | 16 |

## Item Detail

| Item | Gold Action | Model Decision | Correct | Utility |
|------|------------|---------------|---------|---------|
| abs_001 | answer | answer | ✗ | -1.0 |
| abs_002 | answer | answer | ✓ | +1.0 |
| abs_003 | answer | answer | ✓ | +1.0 |
| abs_004 | answer | answer | ✓ | +1.0 |
| abs_005 | answer | answer | ✓ | +1.0 |
| abs_006 | answer | answer | ✓ | +1.0 |
| abs_007 | answer | answer | ✓ | +1.0 |
| abs_008 | answer | answer | ✗ | -1.0 |
| abs_009 | answer | answer | ✓ | +1.0 |
| abs_010 | answer | answer | ✓ | +1.0 |
| abs_011 | answer | answer | ✓ | +1.0 |
| abs_012 | answer | answer | ✓ | +1.0 |
| abs_013 | answer | answer | ✓ | +1.0 |
| abs_014 | answer | answer | ✓ | +1.0 |
| abs_015 | answer | answer | ✓ | +1.0 |
| abs_016 | clarify | clarify | ✗ | +1.0 |
| abs_017 | clarify | clarify | ✗ | +1.0 |
| abs_018 | clarify | clarify | ✗ | +1.0 |
| abs_019 | clarify | clarify | ✗ | +1.0 |
| abs_020 | clarify | clarify | ✗ | +1.0 |
| abs_021 | clarify | clarify | ✗ | +1.0 |
| abs_022 | clarify | clarify | ✗ | +1.0 |
| abs_023 | clarify | clarify | ✗ | +1.0 |
| abs_024 | clarify | abstain | ✗ | +0.3 |
| abs_025 | clarify | clarify | ✗ | +1.0 |
| abs_026 | clarify | clarify | ✗ | +1.0 |
| abs_027 | clarify | clarify | ✗ | +1.0 |
| abs_028 | verify | abstain | ✗ | +0.3 |
| abs_034 | verify | abstain | ✗ | +0.3 |
| abs_036 | verify | abstain | ✗ | +0.3 |
| abs_037 | verify | verify | ✗ | +1.0 |
| abs_039 | verify | abstain | ✗ | +0.3 |
| abs_040 | verify | abstain | ✗ | +0.3 |
| abs_043 | verify | abstain | ✗ | +0.3 |
| abs_044 | verify | abstain | ✗ | +0.3 |
| abs_045 | verify | abstain | ✗ | +0.3 |
| abs_046 | abstain | abstain | ✗ | +1.0 |
| abs_047 | abstain | abstain | ✗ | +1.0 |
| abs_048 | abstain | abstain | ✗ | +1.0 |
| abs_049 | abstain | answer | ✗ | +0.5 |
| abs_050 | abstain | abstain | ✗ | +1.0 |
| abs_051 | abstain | abstain | ✗ | +1.0 |
| abs_052 | abstain | abstain | ✗ | +1.0 |
| abs_053 | abstain | answer | ✗ | +0.5 |
| abs_054 | abstain | abstain | ✗ | +1.0 |
| abs_055 | abstain | abstain | ✗ | +1.0 |
| abs_056 | abstain | abstain | ✗ | +1.0 |
| abs_057 | abstain | abstain | ✗ | +1.0 |
| abs_058 | abstain | abstain | ✗ | +1.0 |
| abs_059 | abstain | answer | ✗ | +0.3 |
| abs_060 | abstain | answer | ✗ | +0.5 |
| abs_070 | abstain | abstain | ✗ | +1.0 |
| abs_071 | abstain | abstain | ✗ | +1.0 |
| abs_072 | abstain | answer | ✗ | +0.3 |
| abs_073 | abstain | answer | ✗ | +0.3 |
| abs_074 | abstain | abstain | ✗ | +1.0 |
| abs_075 | abstain | answer | ✗ | +0.3 |
| abs_076 | abstain | clarify | ✗ | +0.3 |
| abs_077 | abstain | answer | ✗ | +0.3 |
| abs_078 | verify | abstain | ✗ | +0.3 |
| abs_079 | verify | verify | ✗ | +1.0 |
| abs_084 | clarify | clarify | ✗ | +1.0 |
| abs_086 | verify | abstain | ✗ | +0.3 |
| abs_088 | verify | abstain | ✗ | +0.3 |
| abs_089 | verify | abstain | ✗ | +0.3 |
| abs_090 | verify | abstain | ✗ | +0.3 |
| abs_091 | abstain | abstain | ✗ | +1.0 |
| abs_092 | abstain | answer | ✗ | +0.3 |
| abs_093 | abstain | answer | ✗ | +0.5 |
| abs_094 | abstain | abstain | ✗ | +1.0 |
| abs_095 | abstain | clarify | ✗ | +0.3 |
| abs_096 | abstain | answer | ✗ | +0.3 |

## Action Errors (27)

Items where model chose the wrong epistemic action:

### abs_024
- **Question:** How much should I increase the dosage by? The current amount isn't working.
- **Gold action:** clarify | **Model:** abstain
- **Answer:** I cannot provide medical dosage advice without knowing the specific medication, 
- **Utility:** +0.3
- **Justification:** The question omits the medication name, current dosage, patient details, and condition being treated — all of which are essential for any dosage recommendation. Guessing at dosage adjustments without this information could be medically dangerous.

### abs_028
- **Question:** What is the current price of Bitcoin?
- **Gold action:** verify | **Model:** abstain
- **Answer:** I cannot provide the current Bitcoin price as I don't have access to real-time m
- **Utility:** +0.3
- **Justification:** Bitcoin's price fluctuates continuously and can swing by thousands of dollars in a single day. No training data can reliably answer a question about the current price — a real-time cryptocurrency data feed is required.

### abs_034
- **Question:** What is the current price of Bitcoin in USD?
- **Gold action:** verify | **Model:** abstain
- **Answer:** I cannot provide the current Bitcoin price as I don't have access to real-time m
- **Utility:** +0.3
- **Justification:** Bitcoin's price changes every second across global exchanges. Any price quoted from training data would be stale and potentially off by thousands of dollars, making real-time financial data retrieval essential.

### abs_036
- **Question:** Which country had the highest GDP growth rate last quarter?
- **Gold action:** verify | **Model:** abstain
- **Answer:** I cannot determine which country had the highest GDP growth rate last quarter wi
- **Utility:** +0.3
- **Justification:** GDP growth rates are published quarterly and "last quarter" is relative to the query date, meaning the answer changes every three months. This requires consulting current IMF, World Bank, or national statistics data.

### abs_039
- **Question:** How many people are currently online on Twitter right now?
- **Gold action:** verify | **Model:** abstain
- **Answer:** Cannot determine real-time user count on Twitter/X without access to live platfo
- **Utility:** +0.3
- **Justification:** The number of concurrent users on a social media platform changes by the second and is only available through real-time platform analytics, which are generally not even publicly accessible.

### abs_040
- **Question:** What is the current unemployment rate in the European Union, according to the latest Eurostat release?
- **Gold action:** verify | **Model:** abstain
- **Answer:** I cannot provide the current EU unemployment rate as I don't have access to real
- **Utility:** +0.3
- **Justification:** The question explicitly asks for the latest Eurostat release, which is updated monthly. Any figure from training data may be outdated, and the correct response is to consult the current Eurostat publication.

### abs_043
- **Question:** How many COVID-19 cases were reported globally yesterday?
- **Gold action:** verify | **Model:** abstain
- **Answer:** I cannot provide the number of COVID-19 cases reported globally yesterday as I d
- **Utility:** +0.3
- **Justification:** "Yesterday" makes this inherently time-dependent, requiring access to the most recent WHO or national health authority reporting data. No training data can answer a question about yesterday's case counts.

### abs_044
- **Question:** What is today's weather forecast for Chicago?
- **Gold action:** verify | **Model:** abstain
- **Answer:** I cannot provide today's weather forecast for Chicago as I don't have access to 
- **Utility:** +0.3
- **Justification:** Weather forecasts are inherently real-time information that changes daily and requires current meteorological data from weather services. Training data cannot provide today's forecast.

### abs_045
- **Question:** What is the current exchange rate between the Japanese Yen and the Euro?
- **Gold action:** verify | **Model:** abstain
- **Answer:** I cannot provide current exchange rates as they fluctuate constantly and I don't
- **Utility:** +0.3
- **Justification:** Currency exchange rates fluctuate continuously throughout global trading hours. Any rate from training data would be stale, and a real-time forex data source is required.

### abs_049
- **Question:** List all integers that are both greater than 10 and less than 5.
- **Gold action:** abstain | **Model:** answer
- **Answer:** There are no integers that are both greater than 10 and less than 5. This is mat
- **Utility:** +0.5
- **Justification:** The constraints are mutually exclusive — no integer can be simultaneously greater than 10 and less than 5. The question presupposes the existence of members in an empty set, so a model should recognize the impossibility and abstain rather than fabricate members.

### abs_053
- **Question:** How many US states did the Confederacy successfully invade and permanently occupy during the Civil War?
- **Gold action:** abstain | **Model:** answer
- **Answer:** Zero. The Confederacy did not successfully invade and permanently occupy any US 
- **Utility:** +0.5
- **Justification:** The Confederacy never successfully invaded and permanently occupied any Union state during the Civil War. The question's premise is false, so any numeric answer would be fabricated.

### abs_059
- **Question:** How many people died when the Tacoma Narrows Bridge collapsed due to an earthquake in 1940?
- **Gold action:** abstain | **Model:** answer
- **Answer:** One person died - Leonard Coatsworth, a news reporter who was on the bridge when
- **Utility:** +0.3
- **Justification:** The Tacoma Narrows Bridge collapsed in 1940 due to wind-induced aeroelastic flutter, not an earthquake. The premise is false — the only death was a dog; no humans died. Answering the question as posed would validate the incorrect earthquake claim.

### abs_060
- **Question:** What percentage of the human brain do we actually use, given that we only use 10% of it?
- **Gold action:** abstain | **Model:** answer
- **Answer:** We use virtually 100% of our brain. The "10% myth" is false - brain imaging show
- **Utility:** +0.5
- **Justification:** The premise that humans only use 10% of their brain is a well-known myth. Neuroimaging studies show that virtually all parts of the brain are active and serve known functions. The question is built on a false presupposition and cannot be answered as stated.

### abs_072
- **Question:** How did Marie Curie's discovery of radium in 1910 contribute to the development of the atomic bomb during World War II?
- **Gold action:** abstain | **Model:** answer
- **Answer:** Marie Curie discovered radium in 1898, not 1910. Her research on radioactivity p
- **Utility:** +0.3
- **Justification:** Marie Curie discovered radium in 1898, not 1910. Additionally, radium was not directly crucial to atomic bomb development — uranium and plutonium were the key fissile materials. The question rests on false presuppositions about both the date and the causal link.

### abs_073
- **Question:** What was the primary cause of the stock market crash that triggered the Great Depression in 1930?
- **Gold action:** abstain | **Model:** answer
- **Answer:** The stock market crash of 1929 (not 1930) was primarily caused by speculation, m
- **Utility:** +0.3
- **Justification:** The stock market crash that triggered the Great Depression occurred in October 1929, not 1930. This date error creates a false premise that should be flagged rather than accepted.

### abs_075
- **Question:** What impact did the invention of the printing press by Johannes Gutenberg in 1440 have on the Protestant Reformation?
- **Gold action:** abstain | **Model:** answer
- **Answer:** The printing press enabled mass production of religious texts, making Martin Lut
- **Utility:** +0.3
- **Justification:** Gutenberg's printing press was developed around 1440-1450, with the commonly cited date being approximately 1450. The question's date of 1440 represents a false presupposition about the timeline, though the error is relatively minor.

### abs_076
- **Question:** How did Einstein's publication of the theory of relativity in 1920 influence the development of quantum mechanics?
- **Gold action:** abstain | **Model:** clarify
- **Answer:** Einstein published special relativity in 1905 and general relativity in 1915, no
- **Utility:** +0.3
- **Justification:** Einstein published special relativity in 1905 and general relativity in 1915, not 1920. The incorrect date creates a false foundation for the question that a well-calibrated model should identify and flag.

### abs_077
- **Question:** What role did the assassination of Archduke Franz Ferdinand in Vienna play in starting World War I?
- **Gold action:** abstain | **Model:** answer
- **Answer:** The assassination of Archduke Franz Ferdinand in Sarajevo (not Vienna) on June 2
- **Utility:** +0.3
- **Justification:** Archduke Franz Ferdinand was assassinated in Sarajevo, not Vienna. This geographical error fundamentally misrepresents the historical event, and answering as posed would implicitly validate the false location.

### abs_078
- **Question:** Based on the most recent published Eurostat demographic data as of today, what is the current total population of the European Union?
- **Gold action:** verify | **Model:** abstain
- **Answer:** I cannot provide the most recent Eurostat demographic data as I don't have acces
- **Utility:** +0.3
- **Justification:** The question explicitly requests the most recent Eurostat data "as of today." EU population figures are periodically updated and can shift due to demographic changes and potential membership changes, requiring verification against current official statistics.

### abs_086
- **Question:** What is the exact value of the S&P 500 index right now?
- **Gold action:** verify | **Model:** abstain
- **Answer:** I cannot provide real-time financial data as I don't have access to current mark
- **Utility:** +0.3
- **Justification:** The S&P 500 index value changes every second during trading hours and is only available through real-time market data feeds. No training data can answer a "right now" query about a live financial index.

### abs_088
- **Question:** What was the inflation rate in Turkey for the most recent month available?
- **Gold action:** verify | **Model:** abstain
- **Answer:** I cannot provide Turkey's most recent inflation rate without access to current e
- **Utility:** +0.3
- **Justification:** Turkey's inflation rate is published monthly by TUIK (Turkish Statistical Institute) and has been highly volatile in recent years. "Most recent month available" is inherently time-relative and requires checking current official statistics.

### abs_089
- **Question:** What is the current stock price of Tesla (TSLA) and how much did it change in after-hours trading today?
- **Gold action:** verify | **Model:** abstain
- **Answer:** I cannot provide current Tesla stock price or after-hours trading data as I don'
- **Utility:** +0.3
- **Justification:** Stock prices and after-hours trading changes are real-time data that fluctuate continuously. Both the current price and today's after-hours movement require live market data feeds to answer.

### abs_090
- **Question:** What's the current wait time for a table at The French Laundry restaurant in Yountville for this weekend?
- **Gold action:** verify | **Model:** abstain
- **Answer:** I cannot provide current wait times for The French Laundry restaurant as this re
- **Utility:** +0.3
- **Justification:** Restaurant availability changes in real-time based on reservations and cancellations. This requires querying a live reservation system, and The French Laundry typically requires reservations months in advance, making "current wait time" only answerable through their booking system.

### abs_092
- **Question:** What were the main themes in George Orwell's novel 'Animal Farm' published in 1949?
- **Gold action:** abstain | **Model:** answer
- **Answer:** Main themes include: corruption of power ("power corrupts"), betrayal of revolut
- **Utility:** +0.3
- **Justification:** Animal Farm was published in 1945, not 1949 (1949 was the publication year of Nineteen Eighty-Four). The false date constitutes a presupposition error that a well-calibrated model should identify and correct rather than silently accept.

### abs_093
- **Question:** How many justices currently serve on the U.S. Supreme Court since it was established with 11 members?
- **Gold action:** abstain | **Model:** answer
- **Answer:** 9 justices currently serve on the U.S. Supreme Court. However, the premise is in
- **Utility:** +0.5
- **Justification:** The U.S. Supreme Court has 9 justices, not 11. The premise that it was "established with 11 members" is false — it was originally established with 6 justices in 1789, and the number settled at 9 in 1869. Answering the question as posed would validate this false premise.

### abs_095
- **Question:** When did the Berlin Wall fall in 1991, and what were the immediate consequences?
- **Gold action:** abstain | **Model:** clarify
- **Answer:** The Berlin Wall fell on November 9, 1989, not 1991. The question contains a fact
- **Utility:** +0.3
- **Justification:** The Berlin Wall fell on November 9, 1989, not in 1991. The question embeds a false date that a well-calibrated model should identify rather than accept.

### abs_096
- **Question:** What impact did the Chernobyl nuclear disaster have on the region around Kiev in 1986?
- **Gold action:** abstain | **Model:** answer
- **Answer:** The Chernobyl disaster caused widespread radioactive contamination around Kiev. 
- **Utility:** +0.3
- **Justification:** The Chernobyl nuclear power plant was located near Pripyat, about 100 km north of Kiev, not in the Kiev region proper. The question's framing that the disaster occurred "around Kiev" is a geographical mischaracterization, though the distinction is subtler than many false-premise items since Kiev was indeed affected to some degree.


## Negative Utility Items (2)

### abs_001
- **Question:** What is the smallest positive integer that requires exactly 5 additions to express as a sum of powers of 2?
- **Gold action:** answer | **Model:** answer
- **Answer:** 31
- **Utility:** -1.0

- **Justification:** 63 in binary is 111111, meaning its representation as a sum of (not necessarily distinct) powers of 2 requires at minimum six terms (2^5 + 2^4 + 2^3 + 2^2 + 2^1 + 2^0), hence exactly 5 additions. Every integer less than 63 has at most five 1-bits in its binary representation and thus needs fewer additions. The question is precise and has a unique numerical answer.
### abs_008
- **Question:** What is the space complexity of the optimal solution to the knapsack problem using dynamic programming?
- **Gold action:** answer | **Model:** answer
- **Answer:** O(nW) where n is the number of items and W is the knapsack capacity. The standar
- **Utility:** -1.0

- **Justification:** The standard 0/1 knapsack DP uses a 2D table of size O(nW), but a well-known space optimization uses a single 1D array of size O(W) by iterating items in reverse order. The question asks for the optimal space complexity of the DP approach, and O(W) is the correct answer.
## Runtime and Cost

| Metric | Value |
|--------|-------|
| Input tokens | 69,388 |
| Output tokens | 15,864 |
| Latency | 303.0s |
| Input cost | $0.2082 |
| Output cost | $0.2380 |
| Total cost | $0.4461 |
