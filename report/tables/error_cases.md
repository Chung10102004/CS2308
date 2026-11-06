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

## trec-covid — R2 BiLSTM-ESIM: hơn BM25 ở 19 truy vấn, kém ở 31, bằng ở 0

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | what types of rapid testing for Covid-19 have been developed? | +33.8 | ✗ Coronavirus disease 2019 in children: Surprising findings in | ✓ Development of a rapid test kit for SARS-CoV-2: an example o |
| tốt | How much impact do masks have on preventing the spread of the COVID-19 | +29.0 | ✓ Impact of self-imposed prevention measures and short-term go | ✓ Understanding the Impact of Face Mask Usage Through Epidemic |
| tốt | what are the best masks for preventing infection by Covid-19? | +26.6 | ✗ Is wearing a face mask safe for people with epilepsy? | ✓ COVID‐19: Face masks and human‐to‐human transmission |
| không tốt | What are the impacts of COVID-19 among African-Americans that differ f | -47.9 | ✓ The impact of COVID-19 on African American communities in th | ? Disparities in premature deaths from heart disease--50 State |
| không tốt | what are the health outcomes for children who contract COVID-19? | -37.8 | ✓ Coronavirus (COVID-19) infection in children at a specialist | ✓ SARS-CoV-2 testing and outcomes in the first 30 days after t |
| không tốt | What is the mechanism of inflammatory response and pathogenesis of COV | -34.5 | ✓ Targeting lymphocyte Kv1.3-channels to suppress cytokine sto | ? Expression of inflammation-related genes in the lung of BALB |

## trec-covid — R3 MedCPT Cross-Encoder: hơn BM25 ở 32 truy vấn, kém ở 16, bằng ở 2

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | what types of rapid testing for Covid-19 have been developed? | +65.2 | ✗ Coronavirus disease 2019 in children: Surprising findings in | ✓ Types of Assays for SARS-CoV-2 Testing: A Review |
| tốt | will SARS-CoV2 infected people develop immunity? Is cross protection p | +52.4 | ✓ Cytokine Storm in COVID-19 patients transforms to a Cytokine | ✓ A systematic review of antibody mediated immunity to coronav |
| tốt | what is known about an mRNA vaccine for the SARS-CoV-2 virus? | +44.4 | ✓ An Evidence Based Perspective on mRNA-SARS-CoV-2 Vaccine Dev | ✓ An Evidence Based Perspective on mRNA-SARS-CoV-2 Vaccine Dev |
| không tốt | what are the initial symptoms of Covid-19? | -52.2 | ✓ Command Suicidal Hallucination as Initial Presentation of Co | ✗ Rethinking antiviral effects for COVID-19 in clinical studie |
| không tốt | what type of hand sanitizer is needed to destroy Covid-19? | -44.8 | ✓ Hand Sanitizers: A Review of Ingredients, Mechanisms of Acti | ✗ A Review of Current Interventions for COVID-19 Prevention |
| không tốt | what drugs have been active against SARS-CoV or SARS-CoV-2 in animal s | -33.1 | ✓ Remdesivir, the antiviral hope against SARS-CoV-2/ Remdesivi | ✗ Search for SARS-CoV-2 inhibitors in currently approved drugs |

## trec-covid — R4 bge-reranker-v2-m3: hơn BM25 ở 40 truy vấn, kém ở 7, bằng ở 3

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | will SARS-CoV2 infected people develop immunity? Is cross protection p | +59.7 | ✓ Cytokine Storm in COVID-19 patients transforms to a Cytokine | ✓ SARS-CoV-2 Antibody Testing – Questions to be asked |
| tốt | what is known about an mRNA vaccine for the SARS-CoV-2 virus? | +52.4 | ✓ An Evidence Based Perspective on mRNA-SARS-CoV-2 Vaccine Dev | ✓ Designing a novel mRNA vaccine against SARS-CoV-2: An immuno |
| tốt | what evidence is there for dexamethasone as a treatment for COVID-19? | +49.5 | ✗ Multiple Myeloma in the Time of COVID-19 | ✓ The use of dexamethasone in the treatment of COVID-19 |
| không tốt | what evidence is there related to COVID-19 super spreaders | -14.1 | ✓ Super-Spreader Businesses and Risk of COVID-19 Transmission | ✗ Comparison of transmissibility of coronavirus between sympto |
| không tốt | what drugs have been active against SARS-CoV or SARS-CoV-2 in animal s | -10.2 | ✓ Remdesivir, the antiviral hope against SARS-CoV-2/ Remdesivi | ✓ Identification of antiviral drug candidates against SARS-CoV |
| không tốt | what type of hand sanitizer is needed to destroy Covid-19? | -7.8 | ✓ Hand Sanitizers: A Review of Ingredients, Mechanisms of Acti | ✓ Hand Sanitizers: A Review of Ingredients, Mechanisms of Acti |

## trec-covid — X1 bge-reranker-base: hơn BM25 ở 35 truy vấn, kém ở 13, bằng ở 2

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | what types of rapid testing for Covid-19 have been developed? | +65.2 | ✗ Coronavirus disease 2019 in children: Surprising findings in | ✓ Covid-19 rapid test by combining a random forest based web s |
| tốt | Does SARS-CoV-2 have any subtypes, and if so what are they? | +47.5 | ✗ Masking the general population might attenuate COVID-19 outb | ✓ Global Spread of SARS-CoV-2 Subtype with Spike Protein Mutat |
| tốt | what evidence is there for dexamethasone as a treatment for COVID-19? | +42.1 | ✗ Multiple Myeloma in the Time of COVID-19 | ✓ Short-Term Corticosteroids in SARS-CoV2 Patients: Hospitalis |
| không tốt | what are the benefits and risks of re-opening schools in the midst of  | -46.7 | ✓ COVID-19 Related School Closings and Risk of Weight Gain Amo | ? Reorganization of Medical Oncology Departments during COVID- |
| không tốt | what type of hand sanitizer is needed to destroy Covid-19? | -43.3 | ✓ Hand Sanitizers: A Review of Ingredients, Mechanisms of Acti | ✗ European Task Force on Contact Dermatitis statement on coron |
| không tốt | what drugs have been active against SARS-CoV or SARS-CoV-2 in animal s | -31.4 | ✓ Remdesivir, the antiviral hope against SARS-CoV-2/ Remdesivi | ? Montelukast drug activity and potential against SARS-CoV-2 |

## trec-covid — X2 bge-reranker-large: hơn BM25 ở 36 truy vấn, kém ở 12, bằng ở 2

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | what types of rapid testing for Covid-19 have been developed? | +58.3 | ✗ Coronavirus disease 2019 in children: Surprising findings in | ✓ Current and emerging diagnostic tests available for the nove |
| tốt | will SARS-CoV2 infected people develop immunity? Is cross protection p | +49.1 | ✓ Cytokine Storm in COVID-19 patients transforms to a Cytokine | ✓ SARS-CoV-2 Antibody Testing – Questions to be asked |
| tốt | Does SARS-CoV-2 have any subtypes, and if so what are they? | +47.5 | ✗ Masking the general population might attenuate COVID-19 outb | ✓ The global population of SARS-CoV-2 is composed of six major |
| không tốt | what type of hand sanitizer is needed to destroy Covid-19? | -40.4 | ✓ Hand Sanitizers: A Review of Ingredients, Mechanisms of Acti | ✗ European Task Force on Contact Dermatitis statement on coron |
| không tốt | what evidence is there related to COVID-19 super spreaders | -32.9 | ✓ Super-Spreader Businesses and Risk of COVID-19 Transmission | ✗ Comparison of transmissibility of coronavirus between sympto |
| không tốt | What new public datasets are available related to COVID-19? | -26.4 | ✗ Does Non-COVID19 Lung Lesion Help? Investigating Transferabi | ✗ Comparative Global Epidemiological Investigation of SARS-CoV |

## trec-covid — X3 mxbai-rerank-base: hơn BM25 ở 41 truy vấn, kém ở 6, bằng ở 3

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | what types of rapid testing for Covid-19 have been developed? | +65.2 | ✗ Coronavirus disease 2019 in children: Surprising findings in | ✓ Current and emerging diagnostic tests available for the nove |
| tốt | Does SARS-CoV-2 have any subtypes, and if so what are they? | +61.6 | ✗ Masking the general population might attenuate COVID-19 outb | ✓ The global population of SARS-CoV-2 is composed of six major |
| tốt | How does the coronavirus differ from seasonal flu? | +57.6 | ✗ Experience of a screening centre for influenza A/H1N1: the f | ✓ Relative disease burdens of COVID-19 and seasonal influenza  |
| không tốt | what are the mortality rates overall and in specific populations | -12.4 | ✓ Estimating Lower Bounds for COVID-19 Mortality from Northern | ✓ Global, regional, and national under-5 mortality, adult mort |
| không tốt | what type of hand sanitizer is needed to destroy Covid-19? | -10.3 | ✓ Hand Sanitizers: A Review of Ingredients, Mechanisms of Acti | ✓ Hand Sanitizers: A Review on Formulation Aspects, Adverse Ef |
| không tốt | what kinds of complications related to COVID-19 are associated with di | -6.6 | ✓ Diabetes and COVID‐19: psychosocial consequences of the COVI | ✓ Diabetes is a risk factor for the progression and prognosis  |

## trec-covid — X4 MonoT5-base: hơn BM25 ở 34 truy vấn, kém ở 14, bằng ở 2

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | will SARS-CoV2 infected people develop immunity? Is cross protection p | +56.5 | ✓ Cytokine Storm in COVID-19 patients transforms to a Cytokine | ✓ Antibody Dependent Enhancement Due to Original Antigenic Sin |
| tốt | what types of rapid testing for Covid-19 have been developed? | +54.2 | ✗ Coronavirus disease 2019 in children: Surprising findings in | ✓ A Molecularly Imprinted Polymer-Based Technology for Rapid T |
| tốt | Does SARS-CoV-2 have any subtypes, and if so what are they? | +50.0 | ✗ Masking the general population might attenuate COVID-19 outb | ✓ A Novel Synonymous Mutation of SARS-CoV-2: Is This Possible  |
| không tốt | which SARS-CoV-2 proteins-human proteins interactions indicate potenti | -29.4 | ✓ Network-based drug repurposing for novel coronavirus 2019-nC | ✓ Drug repurposing against SARS-CoV-2 using E-pharmacophore ba |
| không tốt | what evidence is there related to COVID-19 super spreaders | -27.6 | ✓ Super-Spreader Businesses and Risk of COVID-19 Transmission | ? Excess mortality during the Covid-19 pandemic: Early evidenc |
| không tốt | What vaccine candidates are being tested for Covid-19? | -25.8 | ✓ SARS-CoV-2 vaccines: 'Warp Speed' needs mind melds not warpe | ✗ An overview on COVID-19: reality and expectation |

## nfcorpus — R1 LambdaMART: hơn BM25 ở 129 truy vấn, kém ở 54, bằng ở 140

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | low-carb diets | +40.1 | ? Effects of very-low-carbohydrate (horsemeat- or beef-based)  | ? Effects of very-low-carbohydrate (horsemeat- or beef-based)  |
| tốt | Alcohol Risks vs. Benefits | +39.9 | ? Effect of potentially modifiable risk factors associated wit | ✓ Who benefits most from the cardioprotective properties of al |
| tốt | Vitamin D: Shedding some light on the new recommendations | +38.7 | ? Safety considerations and potential interactions of vitamins | ✓ Towards prevention of vitamin D deficiency and beyond: knowl |
| không tốt | factory farming practices | -32.9 | ✓ Prevalence of Yersinia enterocolitica in market weight hogs  | ? Organic foods: health and environmental advantages and disad |
| không tốt | Vitamin C-Enriched Bacon | -28.9 | ? Airborne mutagens produced by frying beef, pork and a soy-ba | ? Supplementation with vitamin C and N-acetyl-cysteine increas |
| không tốt | Convergence of Evidence | -19.3 | ✓ The longer-term impacts of Western diet on human cognition a | ? Shared signals and the potential for phylogenetic espionage  |

## nfcorpus — R2 BiLSTM-ESIM: hơn BM25 ở 71 truy vấn, kém ở 143, bằng ở 109

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | Too Much Iodine Can Be as Bad as Too Little | +45.7 | ? Preventing and arresting coronary atherosclerosis. | ✓ Iodine Status and Thyroid Function of Boston-Area Vegetarian |
| tốt | Breast Cancer & Alcohol: How Much is Safe? | +37.2 | ? Acrylamide exposure and incidence of breast cancer among pos | ✓ Salivary acetaldehyde increase due to alcohol-containing mou |
| tốt | Treating an Enlarged Prostate With Diet | +35.0 | ✓ Benign prostatic hyperplasia in primary care: what you need  | ✓ Epidemiological survey of benign prostatic hyperplasia and p |
| không tốt | shelf life | -100.0 | ✓ Oxidative stability and shelf-life evaluation of selected cu | ? Acute rhabdomyolysis caused by Spirulina (Arthrospira platen |
| không tốt | IGF-1 | -83.8 | ✓ Long-term effects of calorie or protein restriction on serum | ? Attained height of lacto-ovo vegetarian children and adolesc |
| không tốt | adenovirus 36 | -80.8 | ✓ Human adenovirus-36 antibody status is associated with obesi | ? The use of placebo interventions in medical practice--a nati |

## nfcorpus — R3 MedCPT Cross-Encoder: hơn BM25 ở 113 truy vấn, kém ở 63, bằng ở 147

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | The Saturated Fat Studies: Buttering Up the Public | +58.4 | ? Cheese intake in large amounts lowers LDL-cholesterol concen | ✓ Recommended dietary reference intakes, nutritional goals and |
| tốt | Anti-Angiogenesis: Cutting Off Tumor Supply Lines | +54.8 | ? Anti-angiogenic activity of inositol hexaphosphate (IP6). | ✓ Tumor Angiogenesis as a Target for Dietary Cancer Prevention |
| tốt | Too Much Iodine Can Be as Bad as Too Little | +54.4 | ? Preventing and arresting coronary atherosclerosis. | ? Some subgroups of reproductive age women in the United State |
| không tốt | factory farming practices | -41.7 | ✓ Prevalence of Yersinia enterocolitica in market weight hogs  | ? Organic foods: health and environmental advantages and disad |
| không tốt | shelf life | -36.9 | ✓ Oxidative stability and shelf-life evaluation of selected cu | ? The effect of blood removal on oxidation and shelf life of b |
| không tốt | The Actual Benefit of Diet vs. Drugs | -35.5 | ✓ Are preventive drugs preventive enough? A study of patients' | ? Definitions and potential health benefits of the Mediterrane |

## nfcorpus — R4 bge-reranker-v2-m3: hơn BM25 ở 103 truy vấn, kém ở 85, bằng ở 135

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | Are Multivitamins Good For You? | +49.6 | ? Vitamin and mineral supplements in the primary prevention of | ✓ Who uses multivitamins? A cross-sectional study in the Physi |
| tốt | Are Artificial Colors Bad for You? | +48.4 | ? You Are What You Eat: Within-Subject Increases in Fruit and  | ✓ Food additives and hyperactive behaviour in 3-year-old and 8 |
| tốt | milk | +48.0 | ? Effect of two types of soy milk and dairy milk on plasma lip | ✓ Skim milk, whey, and casein increase body weight and whey an |
| không tốt | Chronic Headaches and Pork Parasites | -40.4 | ✓ Neurocysticercosis in pregnancy: not just another headache. | ? Galactose-α-1,3-galactose and Delayed Anaphylaxis, Angioedem |
| không tốt | liver disease | -39.5 | ✓ The association of coffee intake with liver cancer incidence | ? Saturated free fatty acid sodium palmitate-induced lipoapopt |
| không tốt | factory farming practices | -35.6 | ✓ Prevalence of Yersinia enterocolitica in market weight hogs  | ? Occupation and risk of lymphoma: a multicentre prospective c |

## nfcorpus — X1 bge-reranker-base: hơn BM25 ở 88 truy vấn, kém ở 88, bằng ở 147

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | Too Much Iodine Can Be as Bad as Too Little | +61.0 | ? Preventing and arresting coronary atherosclerosis. | ✓ Variability of iodine content in common commercially availab |
| tốt | milk | +50.1 | ? Effect of two types of soy milk and dairy milk on plasma lip | ✓ Milk is not just food but most likely a genetic transfection |
| tốt | Are Artificial Colors Bad for You? | +47.7 | ? You Are What You Eat: Within-Subject Increases in Fruit and  | ✓ Food additives and hyperactive behaviour in 3-year-old and 8 |
| không tốt | How to Help Prevent Abdominal Aortic Aneurysms | -68.5 | ✓ Analysis of risk factors for abdominal aortic aneurysm in a  | ? Bulking agents, antispasmodics and antidepressants for the t |
| không tốt | Is Coconut Milk Good For You? | -59.8 | ✓ The cholesterol-lowering effect of coconut flakes in humans  | ? A systematic review and meta-analysis of the effects of past |
| không tốt | Phytates for the Treatment of Cancer | -55.7 | ✓ Phytate levels and bone parameters: a retrospective pilot cl | ? Mechanisms of primary cancer prevention by butyrate and othe |

## nfcorpus — X2 bge-reranker-large: hơn BM25 ở 105 truy vấn, kém ở 75, bằng ở 143

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | Anti-Angiogenesis: Cutting Off Tumor Supply Lines | +48.0 | ? Anti-angiogenic activity of inositol hexaphosphate (IP6). | ✓ Tumor Angiogenesis as a Target for Dietary Cancer Prevention |
| tốt | crib death | +46.9 | ? The Preventable Causes of Death in the United States: Compar | ✓ Relation of beta-casomorphin to apnea in sudden infant death |
| tốt | milk | +43.2 | ? Effect of two types of soy milk and dairy milk on plasma lip | ✓ Milk is not just food but most likely a genetic transfection |
| không tốt | Is apple cider vinegar good for you? | -58.9 | ✓ Esophageal injury by apple cider vinegar tablets and subsequ | ? International multidimensional authenticity specification (I |
| không tốt | Is Coconut Milk Good For You? | -44.2 | ✓ The cholesterol-lowering effect of coconut flakes in humans  | ? Acne, dairy and cancer |
| không tốt | How to Reduce Exposure to Alkylphenols Through Your Diet | -42.5 | ✓ Xeno-estrogenic compounds in precipitation. | ? Reducing exposure to dioxins and related compounds through f |

## nfcorpus — X3 mxbai-rerank-base: hơn BM25 ở 119 truy vấn, kém ở 65, bằng ở 139

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | Too Much Iodine Can Be as Bad as Too Little | +82.7 | ? Preventing and arresting coronary atherosclerosis. | ✓ Iodine-induced neonatal hypothyroidism secondary to maternal |
| tốt | Vitamin C-Enriched Bacon | +71.1 | ? Airborne mutagens produced by frying beef, pork and a soy-ba | ✓ Effects of vitamins C and E on N-nitroso compound formation, |
| tốt | milk | +57.4 | ? Effect of two types of soy milk and dairy milk on plasma lip | ✓ Milk intake and risk of hip fracture in men and women: a met |
| không tốt | shelf life | -50.0 | ✓ Oxidative stability and shelf-life evaluation of selected cu | ? Fruit and Soil Quality of Organic and Conventional Strawberr |
| không tốt | The Actual Benefit of Diet vs. Drugs | -48.7 | ✓ Are preventive drugs preventive enough? A study of patients' | ? Reductions in Cardiovascular Disease Projected from Modest R |
| không tốt | Phytates for the Treatment of Cancer | -43.8 | ✓ Phytate levels and bone parameters: a retrospective pilot cl | ? Phytochemicals for breast cancer prevention by targeting aro |

## nfcorpus — X4 MonoT5-base: hơn BM25 ở 110 truy vấn, kém ở 73, bằng ở 140

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | Too Much Iodine Can Be as Bad as Too Little | +64.2 | ? Preventing and arresting coronary atherosclerosis. | ✓ Iodine-induced neonatal hypothyroidism secondary to maternal |
| tốt | low-carb diets | +55.4 | ? Effects of very-low-carbohydrate (horsemeat- or beef-based)  | ✓ Low-carbohydrate diets and all-cause and cause-specific mort |
| tốt | Are Artificial Colors Bad for You? | +45.9 | ? You Are What You Eat: Within-Subject Increases in Fruit and  | ✓ Synthetic Food Colors and Neurobehavioral Hazards: The View  |
| không tốt | Phytates for the Treatment of Cancer | -36.0 | ✓ Phytate levels and bone parameters: a retrospective pilot cl | ? Phytochemicals for breast cancer prevention by targeting aro |
| không tốt | Flaxseeds & Breast Cancer Survival: Clinical Evidence | -34.8 | ✓ Do phytoestrogens reduce the risk of breast cancer and breas | ? Flax and Breast Cancer: A Systematic Review. |
| không tốt | Fish Fog | -29.4 | ✓ Which Fish Should I Eat? Perspectives Influencing Fish Consu | ? Fish odour syndrome |

## scifact — R1 LambdaMART: hơn BM25 ở 99 truy vấn, kém ở 23, bằng ở 178

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | p16INK4A accumulation is  linked to an abnormal wound response caused  | +100.0 | ? Asymptomatic spinal cord lesions predict disease progression | ✓ Monitoring Tumorigenesis and Senescence In Vivo with a p16IN |
| tốt | Low expression of miR7a does represses target genes and exerts a biolo | +81.0 | ? The polycomb group protein L3mbtl2 assembles an atypical PRC | ✓ Assessing the ceRNA hypothesis with quantitative measurement |
| tốt | Cellular aging closely links to an older appearance. | +75.4 | ? The intersection between aging and cardiovascular disease. | ? The intersection between aging and cardiovascular disease. |
| không tốt | Lack of clpC does not affect sporulation efficiency in Bacillus subtil | -54.6 | ✓ High-Throughput Genetic Screens Identify a Large and Diverse | ? The first gene of the Bacillus subtilis clpC operon, ctsR, e |
| không tốt | Input from  mental and physical health care professionals is effective | -45.6 | ✓ Mental health problems of homeless children and families: lo | ? Evaluation of a mental health outreach service for homeless  |
| không tốt | Mitochondria are uninvolved in apoptosis. | -45.6 | ✓ Mitochondria: Dynamic Organelles in Disease, Aging, and Deve | ? Bioenergetic aspects of apoptosis, necrosis and mitoptosis |

## scifact — R2 BiLSTM-ESIM: hơn BM25 ở 98 truy vấn, kém ở 65, bằng ở 137

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | PPAR-RXRs can be activated by PPAR ligands. | +100.0 | ? Pharmacological correction of a defect in PPARγ signaling am | ✓ Unique response pathways are established by allosteric inter |
| tốt | PPAR-RXRs are inhibited by PPAR ligands. | +100.0 | ? Pharmacological correction of a defect in PPARγ signaling am | ✓ Unique response pathways are established by allosteric inter |
| tốt | Low expression of miR7a does represses target genes and exerts a biolo | +100.0 | ? The polycomb group protein L3mbtl2 assembles an atypical PRC | ✓ Assessing the ceRNA hypothesis with quantitative measurement |
| không tốt | Crossover hot spots are not found within gene promoters in Saccharomyc | -100.0 | ✓ Mapping Meiotic Single-Strand DNA Reveals a New Landscape of | ? Single-RNA counting reveals alternative modes of gene expres |
| không tốt | Golli-deficient T-cells prefer to differentiate into an anergic phenot | -89.5 | ✓ Golli protein negatively regulates store depletion-induced c | ? Mitochondria as sensors and regulators of calcium signalling |
| không tốt | Albendazole is used to treat lymphatic filariasis. | -71.5 | ✓ “Rapid-Impact Interventions”: How a Policy of Integrated Con | ? Combining indoor residual spraying and insecticide-treated n |

## scifact — R3 MedCPT Cross-Encoder: hơn BM25 ở 93 truy vấn, kém ở 19, bằng ở 188

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | NOX2-independent pathways can generate peroxynitrite by reacting with  | +100.0 | ? Lung Carcinogenesis by Diesel Exhaust Particles and the Carc | ✓ Altered recognition of antigen is a mechanism of CD8+ T cell |
| tốt | Modifying the epigenome in the brain affects the normal human aging pr | +100.0 | ? The Aging Epigenome. | ✓ Epigenetic mechanisms in neurological disease |
| tốt | Less than 10% of the gabonese children with Schimmelpenning-Feuerstein | +100.0 | ? Increased Microerythrocyte Count in Homozygous α+-Thalassaem | ✓ Assessment of Volume Depletion in Children with Malaria |
| không tốt | Venules have a thinner or absent smooth layer compared to arterioles. | -69.9 | ✓ Scaffold-based three-dimensional human fibroblast culture pr | ? Vascular heterogeneity and specialization in development and |
| không tốt | Input from  mental and physical health care professionals is effective | -61.3 | ✓ Mental health problems of homeless children and families: lo | ? Homelessness and health. |
| không tốt | In adult tissue, most T cells are memory T cells. | -56.9 | ✓ Early life compartmentalization of human T cell differentiat | ? Tissue-resident memory T cells: local specialists in immune  |

## scifact — R4 bge-reranker-v2-m3: hơn BM25 ở 71 truy vấn, kém ở 31, bằng ở 198

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | Less than 10% of the gabonese children with Schimmelpenning-Feuerstein | +100.0 | ? Increased Microerythrocyte Count in Homozygous α+-Thalassaem | ✓ Assessment of Volume Depletion in Children with Malaria |
| tốt | p16INK4A accumulation is  linked to an abnormal wound response caused  | +100.0 | ? Asymptomatic spinal cord lesions predict disease progression | ✓ Monitoring Tumorigenesis and Senescence In Vivo with a p16IN |
| tốt | Silencing of Bcl2 is important for the maintenance and progression of  | +100.0 | ? DNMT1 Inhibition Reprograms Pancreatic Cancer Stem Cells via | ✓ Antiapoptotic BCL-2 is required for maintenance of a model l |
| không tốt | Microarray results from culture-amplified mixtures of serotypes correl | -100.0 | ✓ The PneuCarriage Project: A Multi-Centre Comparative Study t | ? Empirical Bayesian models for analysing molecular serotyping |
| không tốt | In domesticated populations of Saccharomyces cerevisiae, whole chromos | -56.9 | ✓ Domestication and Divergence of Saccharomyces cerevisiae Bee | ? S-phase-promoting cyclin-dependent kinases prevent re-replic |
| không tốt | The combination of H3K4me3 and H3K79me2 is found in quiescent hair fol | -50.0 | ✓ Genome-wide maps of histone modifications unwind in vivo chr | ? Chromatin modifying enzymes as modulators of reprogramming |

## scifact — X1 bge-reranker-base: hơn BM25 ở 66 truy vấn, kém ở 32, bằng ở 202

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | Modifying the epigenome in the brain affects the normal human aging pr | +100.0 | ? The Aging Epigenome. | ✓ Epigenetic mechanisms in neurological disease |
| tốt | The treatment of cancer patients with co-IR blockade precipitates adve | +100.0 | ? In vitro characterization of the anti-PD-1 antibody nivoluma | ✓ Is autoimmunity the Achilles' heel of cancer immunotherapy? |
| tốt | Silencing of Bcl2 is important for the maintenance and progression of  | +100.0 | ? DNMT1 Inhibition Reprograms Pancreatic Cancer Stem Cells via | ✓ Antiapoptotic BCL-2 is required for maintenance of a model l |
| không tốt | Crossover hot spots are not found within gene promoters in Saccharomyc | -100.0 | ✓ Mapping Meiotic Single-Strand DNA Reveals a New Landscape of | ? RAS genes in Saccharomyces cerevisiae: signal transduction i |
| không tốt | High cardiopulmonary fitness causes increased mortality rate. | -63.1 | ? Acute respiratory failure in patients with severe community- | ? Cardiorespiratory fitness and body mass index as predictors  |
| không tốt | High-sensitivity cardiac troponin T (HSCT-T) dosage may not be diagnos | -61.3 | ✓ Diagnostic accuracy of single baseline measurement of Elecsy | ? Troponin concentrations for stratification of patients with  |

## scifact — X2 bge-reranker-large: hơn BM25 ở 71 truy vấn, kém ở 29, bằng ở 200

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | Modifying the epigenome in the brain affects the normal human aging pr | +100.0 | ? The Aging Epigenome. | ✓ Epigenetic mechanisms in neurological disease |
| tốt | Less than 10% of the gabonese children with Schimmelpenning-Feuerstein | +100.0 | ? Increased Microerythrocyte Count in Homozygous α+-Thalassaem | ✓ Assessment of Volume Depletion in Children with Malaria |
| tốt | Silencing of Bcl2 is important for the maintenance and progression of  | +100.0 | ? DNMT1 Inhibition Reprograms Pancreatic Cancer Stem Cells via | ✓ Antiapoptotic BCL-2 is required for maintenance of a model l |
| không tốt | The combination of H3K4me3 and H3K79me2 is found in quiescent hair fol | -64.4 | ✓ Genome-wide maps of histone modifications unwind in vivo chr | ? Chromatin modifying enzymes as modulators of reprogramming |
| không tốt | Cytosolic proteins bind to iron-responsive elements on mRNAs coding fo | -63.1 | ? Multiple RNA surveillance pathways limit aberrant expression | ? Multiple RNA surveillance pathways limit aberrant expression |
| không tốt | Input from  mental and physical health care professionals is effective | -56.9 | ✓ Mental health problems of homeless children and families: lo | ? Evaluation of a mental health outreach service for homeless  |

## scifact — X3 mxbai-rerank-base: hơn BM25 ở 75 truy vấn, kém ở 45, bằng ở 180

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | Modifying the epigenome in the brain affects the normal human aging pr | +100.0 | ? The Aging Epigenome. | ✓ Epigenetic mechanisms in neurological disease |
| tốt | Less than 10% of the gabonese children with Schimmelpenning-Feuerstein | +100.0 | ? Increased Microerythrocyte Count in Homozygous α+-Thalassaem | ✓ Assessment of Volume Depletion in Children with Malaria |
| tốt | CR is associated with higher methylation age. | +100.0 | ? Yeast sirtuins and the regulation of aging. | ✓ Caloric restriction delays age-related methylation drift |
| không tốt | Venules have a thinner or absent smooth layer compared to arterioles. | -100.0 | ✓ Scaffold-based three-dimensional human fibroblast culture pr | ? Exercise training-induced adaptations in the coronary circul |
| không tốt | Mitochondria are uninvolved in apoptosis. | -100.0 | ✓ Mitochondria: Dynamic Organelles in Disease, Aging, and Deve | ? At the gates of death. |
| không tốt | Leukemia associated Rho guanine nucleotide-exchange factor represses R | -69.9 | ✓ The Rho GEFs LARG and GEF-H1 regulate the mechanical respons | ? Role of RhoA-specific guanine exchange factors in regulation |

## scifact — X4 MonoT5-base: hơn BM25 ở 70 truy vấn, kém ở 31, bằng ở 199

| Loại | Truy vấn | Δ nDCG@10 | Bài đầu của BM25 | Bài đầu của reranker |
|---|---|---:|---|---|
| tốt | Less than 10% of the gabonese children with Schimmelpenning-Feuerstein | +100.0 | ? Increased Microerythrocyte Count in Homozygous α+-Thalassaem | ✓ Assessment of Volume Depletion in Children with Malaria |
| tốt | p16INK4A accumulation is  linked to an abnormal wound response caused  | +100.0 | ? Asymptomatic spinal cord lesions predict disease progression | ✓ Monitoring Tumorigenesis and Senescence In Vivo with a p16IN |
| tốt | The treatment of cancer patients with co-IR blockade precipitates adve | +100.0 | ? In vitro characterization of the anti-PD-1 antibody nivoluma | ✓ Is autoimmunity the Achilles' heel of cancer immunotherapy? |
| không tốt | Microarray results from culture-amplified mixtures of serotypes correl | -100.0 | ✓ The PneuCarriage Project: A Multi-Centre Comparative Study t | ? Empirical Bayesian models for analysing molecular serotyping |
| không tốt | The risk of breast cancer among parous women increases with placental  | -64.4 | ✓ Pregnancy characteristics and maternal risk of breast cancer | ? Timing of menarche and first full-term birth in relation to  |
| không tốt | Tirasemtiv has no effect on fast-twitch muscle. | -63.1 | ? The Combination of Exercise and Respiratory Training Improve | ? Role of common hypnotics on the phenotypic causes of obstruc |

✓ = bài có nhãn liên quan, ✗ = có nhãn không liên quan, ? = chưa có nhãn.