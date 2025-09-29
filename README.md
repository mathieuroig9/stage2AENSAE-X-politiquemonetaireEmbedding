# Note de synthèse - Stage de recherche au laboratoire d'économie de l'Ecole Polytechnique  
**Mathieu ROIG**  

## Sujet  
Étude de politique monétaire par utilisation d’embeddings sur les discours de la Fed et du Congrès.  

## Contexte  
Ce projet vise à restituer les travaux menés lors de mon stage de 2ᵉ année à l’ENSAE (juin – septembre 2025) au CREST, sous la supervision de M. Alessandro Riboni, professeur d’économie à l’École Polytechnique.  

Le stage s’est concentré sur l’étude de la politique monétaire à l’aide de méthodes de NLP appliquées aux discussions d’organes politiques majeurs comme la Banque Centrale des États-Unis (la Fed) et le Congrès.  
Ces discussions sont intégralement transcrites, mais représentent des volumes massifs de données difficilement exploitables manuellement. L’essor des techniques d’embeddings permet aujourd’hui de transformer les textes en vecteurs manipulables à grande échelle.  

## Projets menés  

### 1. Étude des réunions de la Fed  
Objectif : mesurer l’influence relative des membres de la Fed en s’appuyant uniquement sur les transcripts des réunions.  

- Définition retenue : un membre est dit **influent** s’il introduit des idées nouvelles qui deviennent ensuite des sujets de discussion.  
- Méthodologie : vectorisation des prises de parole, mesure de la nouveauté par rapport aux interventions précédentes (angle faible entre vecteurs), et de la reprise par les suivantes (angle fort).  
- Outils : embeddings récents, notamment **Transformers** (BERT, Mistral).  
- Article de référence : "Speech and Influence Dynamics in a Monetary Committee", l'auteur utilise une version alternative de TF-IDF, je poursuis l'étude avec l'utilisation de Transformers.

Résultat : ces techniques permettent bien d’identifier des signaux d’influence, mais les méthodes sont encore jeunes et nécessitent un regard critique.  

### 2. Étude des débats du Congrès  
Objectif : analyser l’appartenance partisane (Démocrates vs Républicains) dans leur rapport à la Fed.  

- Méthodologie : comparaison non plus entre interventions mais avec des concepts (ex. « Fed »), via des méthodes d’**embeddings statiques**.  
- Principe : chaque mot du vocabulaire possède un vecteur connu ; ce vecteur est ajusté pour refléter le sens particulier donné par chaque groupe politique.  
- Analyse : mesure de la distance entre les représentations de la Fed par les deux partis et de son évolution dans le temps.
- Article de référence : "Embedding Regression : Models for Context-Specific Description and Inference", l'auteur utilise la méthode ALC, je poursuis l'étude pour l'appliquer à des sujets davantage techniques comme la politique monétaire.

Résultat : les différences observées sont cohérentes avec des faits historiques. Cependant, la maîtrise des méthodes reste un enjeu sur de si grands volumes de données.  

## Conclusion  
Ces deux projets montrent que les méthodes de NLP, qu’elles soient avancées (Transformers) ou plus classiques (embeddings statiques), ouvrent de nouvelles perspectives pour analyser des données massives en économie et en science politique. Toutefois, la rigueur méthodologique reste essentielle, et des approches plus simples mais mieux maîtrisées conservent leur intérêt.
