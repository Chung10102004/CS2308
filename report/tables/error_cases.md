# Ca tốt / ca không tốt (so với BM25, nDCG@10 từng truy vấn)

## trec-covid — R1 LambdaMART: hơn BM25 ở 33 truy vấn, kém ở 17, bằng ở 0

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | will SARS-CoV2 infected people develop immunity? Is cross protection p | +56.2 | ✓ Cytokine Storm in COVID-19 patients transforms to a Cytokine | ✓ Cross-immunity between respiratory coronaviruses may limit C |
| tốt | what types of rapid testing for Covid-19 have been developed? | +54.1 | ✗ Coronavirus disease 2019 in children: Surprising findings in | ✓ Types of Assays for SARS-CoV-2 Testing: A Review. |
| tốt | Does SARS-CoV-2 have any subtypes, and if so what are they? | +38.5 | ✗ Masking the general population might attenuate COVID-19 outb | ✓ Genetic Grouping of SARS-CoV-2 Coronavirus Sequences using I |
| không tốt | what type of hand sanitizer is needed to destroy Covid-19? | -26.0 | ✓ Hand Sanitizers: A Review of Ingredients, Mechanisms of Acti | ✓ Hand Sanitizers: A Review on Formulation Aspects, Adverse Ef |
| không tốt | what drugs have been active against SARS-CoV or SARS-CoV-2 in animal s | -23.2 | ✓ Remdesivir, the antiviral hope against SARS-CoV-2/ Remdesivi | ✗ Current global vaccine and drug efforts against COVID-19: Pr |
| không tốt | are patients taking Angiotensin-converting enzyme inhibitors (ACE) at  | -12.1 | ✓ ACE2 (Angiotensin-Converting Enzyme 2), COVID-19, and ACE In | ✓ Association of Angiotensin-Converting Enzyme Inhibitors and  |

## nfcorpus — R1 LambdaMART: hơn BM25 ở 129 truy vấn, kém ở 54, bằng ở 140

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | low-carb diets | +40.1 | ? Effects of very-low-carbohydrate (horsemeat- or beef-based)  | ? Effects of very-low-carbohydrate (horsemeat- or beef-based)  |
| tốt | Alcohol Risks vs. Benefits | +39.9 | ? Effect of potentially modifiable risk factors associated wit | ✓ Who benefits most from the cardioprotective properties of al |
| tốt | Vitamin D: Shedding some light on the new recommendations | +38.7 | ? Safety considerations and potential interactions of vitamins | ✓ Towards prevention of vitamin D deficiency and beyond: knowl |
| không tốt | factory farming practices | -32.9 | ✓ Prevalence of Yersinia enterocolitica in market weight hogs  | ? Organic foods: health and environmental advantages and disad |
| không tốt | Vitamin C-Enriched Bacon | -28.9 | ? Airborne mutagens produced by frying beef, pork and a soy-ba | ? Supplementation with vitamin C and N-acetyl-cysteine increas |
| không tốt | Convergence of Evidence | -19.3 | ✓ The longer-term impacts of Western diet on human cognition a | ? Shared signals and the potential for phylogenetic espionage  |

## scifact — R1 LambdaMART: hơn BM25 ở 99 truy vấn, kém ở 23, bằng ở 178

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | p16INK4A accumulation is  linked to an abnormal wound response caused  | +100.0 | ? Asymptomatic spinal cord lesions predict disease progression | ✓ Monitoring Tumorigenesis and Senescence In Vivo with a p16IN |
| tốt | Low expression of miR7a does represses target genes and exerts a biolo | +81.0 | ? The polycomb group protein L3mbtl2 assembles an atypical PRC | ✓ Assessing the ceRNA hypothesis with quantitative measurement |
| tốt | Cellular aging closely links to an older appearance. | +75.4 | ? The intersection between aging and cardiovascular disease. | ? The intersection between aging and cardiovascular disease. |
| không tốt | Lack of clpC does not affect sporulation efficiency in Bacillus subtil | -54.6 | ✓ High-Throughput Genetic Screens Identify a Large and Diverse | ? The first gene of the Bacillus subtilis clpC operon, ctsR, e |
| không tốt | Input from  mental and physical health care professionals is effective | -45.6 | ✓ Mental health problems of homeless children and families: lo | ? Evaluation of a mental health outreach service for homeless  |
| không tốt | Mitochondria are uninvolved in apoptosis. | -45.6 | ✓ Mitochondria: Dynamic Organelles in Disease, Aging, and Deve | ? Bioenergetic aspects of apoptosis, necrosis and mitoptosis |

✓ = bài có nhãn liên quan, ✗ = có nhãn không liên quan, ? = chưa có nhãn.