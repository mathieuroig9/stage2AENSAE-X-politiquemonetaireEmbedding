6B.300d.bin : matrice A adaptée à glove.6B.300d.txt

cr_transform.rds : matrice A utilisée dans l'article original, 
non utilisée dans la suite car l'espace d'embedding de référence n'est plus le même

glove.6B.300d.txt : espace d'embedding de référence,
non chargé ici car poids de 1go, on le trouve sur https://www.kaggle.com/datasets/thanakomsn/glove6b300dtxt?resource=download

3 fichiers avec le même format :
    - immigration5stopEXCLU.csv
    - monetary_policy5stopEXCLU.csv
    - federal_reserve5stopEXCLU.csv
ce sont des dataframes avec les colonnes suivantes :
speech_id, mot_cible, contexte_complet, fichier, speakerid, lastname, firstname, chamber, state, gender, party, district, nonvoting, date
le format correspond à mot_cible-rayon-présence_des_stop_words,
i.e pour le premier fichier :
    - on recherche toutes les occurrences de immigration,
    - on prend une fenetre de 5 mots avant le mot cible et 5 mots après,
    - on a fait au préalable un nettoyage de tous les stop words, les mots dans la fenetre ne sont donc pas des stop words
ces 3 fichiers ont été obtenus avec le dataset de Stanford, qui présente de nombreuses fautes,
les fichiers avec "HVD" se lisent de la même façon, à la différence près qu'ils sont obtenus avec le dataset de Harvard, de meilleure qualité
