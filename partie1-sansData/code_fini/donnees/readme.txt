FOCM_statements_characteristics_050525.csv : données brutes à utiliser dans partie 0

df_3dates.csv : 
-tableau réduit (Date, Speaker, Statement, Member) entre 2005-02-02 et 2005-05-03 avec toutes les interventions brutes 
-à utiliser dans partie 0

df_10dates : 
-tableau complet (Speaker, Statement, Date, Statement_no, Chair, Vice_chair,...) entre 2004-03-16 et 2005-05-03 avec toutes les interventions brutes 
-à utiliser dans partie 0

df_ENTIERrésuméMistral.csv : 
-tableau complet de 1976 à 2018 avec seulement la plus longue déclaration et où les déclarations > 512 tokens sont résumées par Mistral
-à utiliser dans partie 1 etape 2

df_doc2vec.csv : 
-tableau (Date, Speaker, Statement, embedding, influence, fs, bs) de 1976 à 2018 avec seulement la plus longue déclaration et l'embedding est réalisé par doc2vec 
-à utiliser dans partie 1 etape 3 pour faire l'embedding (le nommer df_compare pour pas avoir à changer la suite du code) 
-à utiliser dans partie 3 pour faire mesures économétriques

df_econometrie : 
-tableau (Date, Speaker, Statement, embedding, influence, fs, bs) de 1976 à 2018 avec seulement la plus longue déclaration et l'embedding est réalisé par allminilml6v2
-à utiliser dans partie 3 pour faire mesures économétriques

22juillet.dta : fichier stata utilisé pour régressions linéaires de la partie 2 et 3