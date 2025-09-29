df_3dates.csv : 
-tableau réduit (Date, Speaker, Statement, Member) entre 2005-02-02 et 2005-05-03 avec toutes les interventions brutes 

df_10dates : 
-tableau complet (Speaker, Statement, Date, Statement_no, Chair, Vice_chair,...) entre 2004-03-16 et 2005-05-03 avec toutes les interventions brutes 

df_ENTIERrésuméMistral.csv : 
-tableau complet de 1976 à 2018 avec seulement la plus longue déclaration et où les déclarations > 512 tokens sont résumées par Mistral

df_doc2vec.csv : 
-tableau (Date, Speaker, Statement, embedding, influence, fs, bs) de 1976 à 2018 avec seulement la plus longue déclaration et l'embedding est réalisé par doc2vec 

df_econometrie : 
-tableau (Date, Speaker, Statement, embedding, influence, fs, bs) de 1976 à 2018 avec seulement la plus longue déclaration et l'embedding est réalisé par allminilml6v2

22juillet.dta : fichier stata utilisé pour régressions linéaires de la partie 2 et 3

finstsb_to_dev et finstsb_to_test : datasets importés depuis https://huggingface.co/datasets/syang687/FinSTS
