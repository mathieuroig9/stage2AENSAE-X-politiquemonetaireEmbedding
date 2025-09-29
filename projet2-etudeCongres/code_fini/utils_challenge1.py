import os, re, numpy as np, pandas as pd, math
from collections import Counter
from tqdm import tqdm
from typing import List, Tuple, Dict


#on importe spacy pour une liste de stopwords plus complète qu'avec nltk
import spacy
nlp = spacy.load("en_core_web_sm")
stop_words_spacy = nlp.Defaults.stop_words

# Dossier contenant les fichiers
chemin_dossier = "datasetStanford/"

# Charger stopwords anglais
STOPWORDS = set(stop_words_spacy)

##FONCTIONS POUR CHARGER LES DONNEES
#on commence par extraire_contexte_mot pour récupérer les contextes autour du mot cible
#on utilise ensuite match_tableaux qui va merge des colonnes supplémentaires de métadonnées (date,...)

def extraire_contexte_mot(mot_cible, rayon=10, multi_mot=False, pattern_match=False, supprimer_stopwords=False):
    """
    Parcourt speeches_97..114 et renvoie un DF [speech_id, mot_cible, contexte_complet, fichier]
    - Minuscule + tokenisation \b\w+\b (ponctuation retirée via regex)
    - Si supprimer_stopwords=True : stopwords retirés AVANT sélection de la fenêtre,
      rayon = nb de mots avant/après le mot cible qui ne sont PAS des stopwords
    - multi_mot=False : match exact ou match début si pattern_match=True
    - multi_mot=True  : traite `mot_cible` comme une expression multi-mots
    """
    assert isinstance(rayon, int) and rayon >= 1, "rayon doit être un entier >= 1"

    mot_cible_lc = str(mot_cible).lower()
    expr_tokens = mot_cible_lc.replace("_", " ").split()
    n_expr = len(expr_tokens)

    rows = []

    for i in range(97, 115):
        nom_fichier = f"speeches_{i}.txt"
        chemin_fichier = os.path.join(chemin_dossier, nom_fichier)
        try:
            df = pd.read_csv(
                chemin_fichier,
                sep="|",
                names=["speech_id", "speech"],
                dtype=str,
                engine="python",
                encoding="latin1",
                on_bad_lines="skip",
            )
        except Exception as e:
            print(f"[WARN] lecture {nom_fichier}: {e}")
            continue

        for _, r in df.iterrows():
            speech = (r.get("speech") or "")
            speech_id = str(r.get("speech_id") or "")

            tokens = re.findall(r"\b\w+\b", speech.lower())
            if not tokens:
                continue

            # Si on supprime les stopwords AVANT recherche
            if supprimer_stopwords:
                # On garde quand même le mot cible même s'il est dans les stopwords
                tokens_filtered = [
                    tok for tok in tokens if (tok not in STOPWORDS or tok == mot_cible_lc)
                ]
                tokens = tokens_filtered

            if not multi_mot:
                # --- Single word match ---
                if pattern_match:
                    indices = [k for k, tok in enumerate(tokens) if tok.startswith(mot_cible_lc)]
                else:
                    indices = [k for k, tok in enumerate(tokens) if tok == mot_cible_lc]

                for pos in indices:
                    # Si stopwords supprimés : rayon en nb de tokens filtrés
                    debut = max(0, pos - rayon)
                    fin = min(len(tokens), pos + rayon + 1)
                    fenetre_tokens = tokens[debut:fin]
                    rows.append(
                        {
                            "speech_id": speech_id,
                            "mot_cible": mot_cible,
                            "contexte_complet": " ".join(fenetre_tokens),
                            "fichier": nom_fichier,
                        }
                    )

            else:
                # --- Multi-word match ---
                if n_expr == 0:
                    continue
                indices = []
                for pos in range(len(tokens) - n_expr + 1):
                    if pattern_match:
                        if tokens[pos].startswith(expr_tokens[0]) and tokens[pos+1:pos+n_expr] == expr_tokens[1:]:
                            indices.append(pos)
                    else:
                        if tokens[pos:pos+n_expr] == expr_tokens:
                            indices.append(pos)

                for pos in indices:
                    debut = max(0, pos - rayon)
                    fin = min(len(tokens), pos + n_expr + rayon)
                    fenetre_tokens = tokens[debut:fin]
                    rows.append(
                        {
                            "speech_id": speech_id,
                            "mot_cible": mot_cible,
                            "contexte_complet": " ".join(fenetre_tokens),
                            "fichier": nom_fichier,
                        }
                    )

    return pd.DataFrame(rows)



def match_tableaux(df_contexte):
    """
    Enrichit df_contexte via SpeakerMap et descr par 'speech_id'.
    Retourne df avec toutes les colonnes d'origine + speaker vars + date.
    """
    # -------- SpeakerMap --------
    cols_speaker = [
        "speakerid", "speech_id", "lastname", "firstname",
        "chamber", "state", "gender", "party", "district", "nonvoting",
    ]
    speaker_frames = []
    for i in range(97, 115):
        p = os.path.join(chemin_dossier, f"{i}_SpeakerMap.txt")
        try:
            tmp = pd.read_csv(p, sep="|", names=cols_speaker, dtype=str,
                              engine="python", encoding="latin1", on_bad_lines="skip")
            speaker_frames.append(tmp)
        except Exception as e:
            print(f"[WARN] SpeakerMap {i}: {e}")
    df_speaker = pd.concat(speaker_frames, ignore_index=True) if speaker_frames else pd.DataFrame(columns=cols_speaker)

    # (optionnel) dédoublonner par speech_id si besoin :
    # df_speaker = df_speaker.drop_duplicates(subset=["speech_id"], keep="first")

    # -------- descr (date) --------
    cols_descr = [
        "speech_id", "chamber", "date", "number_within_file", "speaker",
        "first_name", "last_name", "state", "gender",
        "line_start", "line_end", "file", "char_count", "word_count",
    ]
    descr_frames = []
    for i in range(97, 115):
        p = os.path.join(chemin_dossier, f"descr_{i}.txt")
        try:
            tmp = pd.read_csv(p, sep="|", names=cols_descr, dtype=str,
                              engine="python", encoding="latin1", on_bad_lines="skip")
            descr_frames.append(tmp[["speech_id", "date"]])
        except Exception as e:
            print(f"[WARN] descr {i}: {e}")
    df_descr = pd.concat(descr_frames, ignore_index=True) if descr_frames else pd.DataFrame(columns=["speech_id", "date"])

    # -------- types + merge --------
    out = df_contexte.copy()
    out["speech_id"] = out["speech_id"].astype(str)
    if not df_speaker.empty:
        df_speaker["speech_id"] = df_speaker["speech_id"].astype(str)
        out = out.merge(df_speaker, on="speech_id", how="left")

    if not df_descr.empty:
        df_descr["speech_id"] = df_descr["speech_id"].astype(str)
        out = out.merge(df_descr, on="speech_id", how="left")
        out["date"] = pd.to_datetime(out["date"], format="%Y%m%d", errors="coerce")

    return out

##FONCTION POUR CALCULER LES EMBEDDINGS
#on utilise reconstruire_embeddings sur notre dataframe qui a déjà eu le process (df -> extraire_contexte_mot -> match_tableaux)
#on a alors les différents embeddings des mots_cibles en fonction du contexte avec la méthode ALC
#on ajoute en plus une pondération TF-IDF supplémentaire optionnelle

_word_re_alpha = re.compile(r"[A-Za-z]+")
_word_re_basic = re.compile(r"\b\w+\b")

def _is_valid_token(w: str, stop_words=None, min_len: int = 3) -> bool:
    if not isinstance(w, str):
        return False
    if len(w) < min_len:
        return False
    if _word_re_alpha.fullmatch(w) is None:
        return False
    if stop_words and (w in stop_words):
        return False
    return True

def _tokenize_basic(text: str):
    """Tokenisation simple en minuscules (mots alphanumériques)."""
    return re.findall(r"\b\w+\b", str(text).lower())

def _build_idf(texts, stop_words=None):
    """
    Calcule un score IDF par token sur une collection de textes.
    IDF = log((N + 1) / (df(t) + 1)) + 1
    - texts: iterable de documents (str)
    - stop_words: set de mots à ignorer dans l'IDF (facultatif)
    """
    if stop_words is None:
        stop_words = set()

    N = len(texts)
    df_counts = Counter()

    for txt in texts:
        toks = set(_tokenize_basic(txt))
        toks = [t for t in toks if t not in stop_words]
        df_counts.update(toks)

    idf = {tok: math.log((N + 1) / (df_counts[tok] + 1)) + 1.0 for tok in df_counts}
    return idf

def reconstruire_embeddings(
    df: pd.DataFrame,
    glove: dict,
    matrice_A: np.ndarray,
    *,
    use_idf: bool = False,          # active la pondération IDF
    idf_stop_words: set = None,     # stopwords à ignorer dans l'IDF
    use_distance: bool = False      # active la pondération par distance 1/(1+dist)
):
    """
    Construit df['embedding'] à partir du contexte:
      - enlève le mot_cible du contexte
      - moyenne (pondérée) des vecteurs GloVe des tokens restants
      - applique la transformation linéaire A (emb = A @ moyenne)

    Paramètres:
      - use_idf: si True, pondère par IDF (calculé sur df['contexte_complet'])
      - idf_stop_words: set optionnel de stop words à exclure du calcul IDF
      - use_distance: si True, pondère chaque token par 1/(1 + distance(token, mot_cible))

    Hypothèses:
      - df a les colonnes: ["mot_cible", "contexte_complet"]
      - glove: dict {token: np.ndarray(dim_glove)}
      - matrice_A: np.ndarray shape (d_out, dim_glove)
    """
    d_in = matrice_A.shape[1]

    # Prépare l'IDF une seule fois si demandé
    idf = _build_idf(df["contexte_complet"], stop_words=idf_stop_words) if use_idf else {}

    out = []
    for _, row in df.iterrows():
        mot_cible = str(row.get("mot_cible", "")).lower()
        tokens = _tokenize_basic(row.get("contexte_complet", ""))

        # Position de référence pour la distance
        if use_distance:
            try:
                pos_cible = next(i for i, t in enumerate(tokens) if t == mot_cible)
            except StopIteration:
                pos_cible = len(tokens) // 2  # fallback si le mot_cible n'apparaît pas
        else:
            pos_cible = None  # non utilisé

        vecs = []
        wts = []
        for j, tok in enumerate(tokens):
            if tok == mot_cible:
                continue  # on retire le mot-cible pour éviter la fuite d'info

            v = glove.get(tok)
            if v is None or v.shape[0] != d_in:
                continue

            w = 1.0
            if use_distance:
                dist = abs(j - pos_cible)
                w *= 1.0 / (1.0 + float(dist))

            if use_idf:
                w *= float(idf.get(tok, 1.0))

            vecs.append(v.astype(np.float32, copy=False))
            wts.append(w)

        if not vecs:
            vecteur_moyen = np.zeros(d_in, dtype=np.float32)
        else:
            V = np.stack(vecs, axis=0).astype(np.float32)
            w = np.asarray(wts, dtype=np.float32)
            s = float(w.sum())
            if s > 0:
                w = w / s
            vecteur_moyen = (w[:, None] * V).sum(axis=0)

        emb = (matrice_A @ vecteur_moyen).astype(np.float32)
        out.append(emb)

    df_res = df.copy()
    df_res["embedding"] = out
    return df_res

###PARTIE dataset Harvard

def retour_dataset_HVD(chemin):
    """donner en argument le chemin vers le dossier contenant les fichiers JSON du dataset d'Harvard et retourne le tableau complet avec toutes les prises de parole"""
    # Chemin vers ton dossier contenant les JSON
    base_dir = Path(chemin)
    rows = []

    for p in base_dir.rglob("*.json"):
        try:
            with p.open(encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            # si le fichier est illisible, on ignore
            continue
        
        if not isinstance(data, dict):
            continue
        gender = (data.get("bio", {}) or {}).get("gender")
        name = data.get("display_name")
        #bioguide = data.get("bioguide")
        # récupération du parti de secours (dernier mandat)
        fallback_party = None
        terms = data.get("terms") or []
        if terms:
            fallback_party = terms[-1].get("party")

        # parcours des discours
        for sp in data.get("speeches", []):
            text = sp.get("text").lower()
            text = " ".join(text.split())   # supprime tous \n, \t, espaces multiples
            party = sp.get("party") or fallback_party
            date = sp.get("date")
            chamber = sp.get("chamber")
            year = None
            if isinstance(date, str) and len(date) >= 4:
                try:
                    year = int(date[:4])
                except Exception:
                    pass
            date = pd.to_datetime(date, errors="coerce")

            rows.append({
                "speaker": name,
                "gender": gender,
                "party": party,
                "year": year,      # année du speech
                "date": date,      # date complète du speech
                "speech": text,
                "chamber": chamber,
                "source_file": p.name
            })

    # Construction du DataFrame final
    df = pd.DataFrame(rows)
    df.sort_values(by=["date"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df = df[(df['party'] == 'Democrat') | (df['party'] == 'Republican')]
    df.reset_index(drop=True, inplace=True)

    return df

# Charger le modèle spaCy et ses stopwords
nlp = spacy.load("en_core_web_sm")
STOPWORDS = set(nlp.Defaults.stop_words)

def extraire_contexte_mot_df_HVD(
    df,
    mot_cible,
    rayon=10,
    multi_mot=False,
    pattern_match=False,
    supprimer_stopwords=False,
    colonne_texte="speech",
    colonne_fichier="source_file",
    colonne_speaker="speaker",
    colonne_party="party",
    colonne_chamber="chamber",
    colonne_year="year",
    colonne_date="date",
):
    """
    Parcourt le DataFrame df et renvoie un DF au format :
    [mot_cible, contexte_complet, fichier, speaker, chamber, party(R/D), year, date]

    - rayon : nb de mots avant/après le motif
    - multi_mot : si True, 'mot_cible' est une expression (mots séparés par espace ou "_")
    - pattern_match : si True, match par préfixe
    - supprimer_stopwords : si True, on retire les stopwords AVANT la sélection de la fenêtre
      (mais on garde les tokens du motif)
    - STOPWORDS : stopwords issus de spaCy (anglais)
    """

    assert isinstance(rayon, int) and rayon >= 1, "rayon doit être un entier >= 1"

    mot_cible_lc = str(mot_cible).lower()
    expr_tokens = mot_cible_lc.replace("_", " ").split()
    n_expr = len(expr_tokens)

    token_re = re.compile(r"\b\w+\b")

    def tokenize(text):
        if not isinstance(text, str):
            return []
        return token_re.findall(text.lower())

    def map_party(p):
        if p == "Republican":
            return "R"
        if p == "Democrat":
            return "D"
        return None

    rows = []

    for row in df.itertuples(index=False):
        speech = getattr(row, colonne_texte, None)
        if not isinstance(speech, str) or not speech:
            continue

        tokens = tokenize(speech)
        if not tokens:
            continue

        # Si on supprime les stopwords
        if supprimer_stopwords:
            motif_set = set(expr_tokens) if multi_mot else {mot_cible_lc}
            tokens = [t for t in tokens if (t not in STOPWORDS) or (t in motif_set)]
            if not tokens:
                continue

        indices = []

        if not multi_mot:
            if pattern_match:
                indices = [k for k, tok in enumerate(tokens) if tok.startswith(mot_cible_lc)]
            else:
                indices = [k for k, tok in enumerate(tokens) if tok == mot_cible_lc]

            for pos in indices:
                debut = max(0, pos - rayon)
                fin = min(len(tokens), pos + rayon + 1)
                fenetre_tokens = tokens[debut:fin]
                rows.append({
                    "mot_cible": mot_cible,
                    "contexte_complet": " ".join(fenetre_tokens),
                    "fichier": getattr(row, colonne_fichier, None),
                    "speaker": getattr(row, colonne_speaker, None),
                    "chamber": getattr(row, colonne_chamber, None),
                    "party": map_party(getattr(row, colonne_party, None)),
                    "year": getattr(row, colonne_year, None),
                    "date": getattr(row, colonne_date, None),
                })

        else:
            if n_expr == 0:
                continue
            if pattern_match:
                for pos in range(len(tokens) - n_expr + 1):
                    if tokens[pos].startswith(expr_tokens[0]) and tokens[pos+1:pos+n_expr] == expr_tokens[1:]:
                        indices.append(pos)
            else:
                for pos in range(len(tokens) - n_expr + 1):
                    if tokens[pos:pos+n_expr] == expr_tokens:
                        indices.append(pos)

            for pos in indices:
                debut = max(0, pos - rayon)
                fin = min(len(tokens), pos + n_expr + rayon)
                fenetre_tokens = tokens[debut:fin]
                rows.append({
                    "mot_cible": mot_cible,
                    "contexte_complet": " ".join(fenetre_tokens),
                    "fichier": getattr(row, colonne_fichier, None),
                    "speaker": getattr(row, colonne_speaker, None),
                    "chamber": getattr(row, colonne_chamber, None),
                    "party": map_party(getattr(row, colonne_party, None)),
                    "year": getattr(row, colonne_year, None),
                    "date": getattr(row, colonne_date, None),
                })

    out = pd.DataFrame(rows, columns=[
        "mot_cible","contexte_complet","fichier","speaker","chamber","party","year","date"
    ])
    if "date" in out.columns:
        out = out.sort_values("date").reset_index(drop=True)
    return out