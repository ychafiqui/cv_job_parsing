import datetime
import streamlit as st
from langdetect import detect
import re
import nltk
import spacy
import math
import pickle
import pandas as pd
import numpy as np

MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august",
          "september", "october", "november", "december"]

def extract_months(date_range):
    date_range = date_range.lower()
    months = []
    for month in MONTHS:
        if month in date_range:
            months.append(month)
    # reorder list of months according to their position in the date range
    months = sorted(months, key=lambda x: date_range.index(x))
    if len(months) > 1:
        return months[0], months[1]
    elif len(months) == 1:
        return months[0], None
    else:
        return None, None

def extract_date_range(date_range):
    # regular expression to detect if 2 years are present
    two_years_re = re.compile(r"\d{4}.*\d{4}")
    # regular expression to detect if only one year is present
    one_year_re = re.compile(r"\d{4}")
    if two_years_re.search(date_range):
        # if 2 years are present, extract them using another regular expression
        start_year = int(re.findall(r"\d{4}", date_range)[0])
        end_year = int(re.findall(r"\d{4}", date_range)[1])
        # if the start year is greater than the end year, swap them
        if start_year > end_year:
            start_year, end_year = end_year, start_year
        
        start_month, end_month  = extract_months(date_range)
        if not start_month: start_month = "january"
        if not end_month: end_month = "january"
        # convert month str to int
        start_month = MONTHS.index(start_month) + 1
        end_month = MONTHS.index(end_month) + 1

        start_date = datetime.date(start_year, start_month, 1)
        end_date = datetime.date(end_year, end_month, 1)
        return start_date, end_date
    elif one_year_re.search(date_range):
        # if only one year is present, extract it using another regular expression
        year = int(re.findall(r"\d{4}", date_range)[0])
        
        start_month, end_month  = extract_months(date_range)

        if not start_month and not end_month:
            start_month = 1
            start_date = datetime.date(year, start_month, 1)
            # end_date = datetime.date.today()
            end_date = None
        elif start_month and end_month:
            start_month = MONTHS.index(start_month) + 1
            end_month = MONTHS.index(end_month) + 1
            start_date = datetime.date(year, start_month, 1)
            end_date = datetime.date(year, end_month, 1)
        elif start_month and not end_month:
            start_month = MONTHS.index(start_month) + 1
            start_date = datetime.date(year, start_month, 1)
            # end_date = datetime.date.today()
            end_date = None

        return start_date, end_date
    else:
        return None, None
    

# from geopy.geocoders import Nominatim
# import openrouteservice

# geolocator = Nominatim(user_agent="my_user_agent")

# def get_dist_two_places(place1, place2):
#     loc = geolocator.geocode(place1)
#     coords_1 = (loc.longitude, loc.latitude)
#     loc2 = geolocator.geocode(place2)
#     coords_2 = (loc2.longitude, loc2.latitude)

#     client = openrouteservice.Client(key='5b3ce3597851110001cf6248d8d292d3786d4d57951829561c8b239e')
#     res = client.directions((coords_1, coords_2))
#     return round(res['routes'][0]['summary']['distance'] / 1000)

# import geopy.distance

# def get_dist_two_places2(place1, place2):
#     loc = geolocator.geocode(place1)
#     loc2 = geolocator.geocode(place2)
#     if loc and loc2:
#         coords_1 = (loc.longitude, loc.latitude)
#         coords_2 = (loc2.longitude, loc2.latitude)
#         return round(geopy.distance.geodesic(coords_1, coords_2).km)

stop_words2 = ["l'un", "l'une", "d'un", "d'une", "c'est", "l'", "d'", "t'"]
stop_words = nltk.corpus.stopwords.words('french')
stop_words_eng = nltk.corpus.stopwords.words('english')
stop_words = list(stop_words)
stop_words_eng = list(stop_words_eng)
lemmatizer = nltk.stem.WordNetLemmatizer()

def preprocess_titre(titre):
    titre = titre.replace('Ã', 'é')
    titre = titre.replace('Ã©', 'é')
    titre = titre.replace('Ã', 'à')
    titre = titre.replace('Ã¢', 'â')
    titre = titre.replace('Ã§', 'ç')
    titre = titre.replace('Ã¨', 'è')
    titre = titre.replace('Ãª', 'ê')
    titre = titre.replace('Ã®', 'î')
    titre = titre.replace('Ã´', 'ô')
    titre = titre.replace('Ã', 'â')
    titre = titre.replace('Ã', 'ç')
    titre = titre.replace('Å', 'oe')
    titre = titre.replace('Ã\xa0', 'à')
    titre = titre.replace('Ã\x80¦', '...')
    titre = titre.replace('', "'")
    titre = titre.replace('Â\x80¢', '-')
    titre = titre.replace('Ã', 'à')
    titre = titre.replace('Â\x80', '')
    titre = titre.replace("’", "'")
    titre = titre.replace("&agrave;", "à")
    titre = titre.replace("&rsquo;", "'")
    titre = titre.replace("&eacute;", "é")
    titre = titre.replace("&egrave;", "è")
    titre = titre.replace("&ecirc;", "ê")
    titre = titre.replace("&ccedil;", "ç")
    titre = titre.replace("&ocirc;", "ô")
    titre = titre.replace("&icirc;", "î")
    titre = titre.replace("&ucirc;", "û")
    titre = titre.replace("&acirc;", "â")
    titre = titre.replace("&nbsp;", " ")
    titre = titre.replace("&bull;", " ")
    titre = titre.replace("&#039;", "'")
    titre = titre.replace("&#39;", "'")
    titre = titre.replace("\t", " ")
    titre = titre.replace("- ", " - ")
    titre = titre.replace("• ", " - ")
    titre = titre.replace('\xa0', ' ')
    titre = titre.replace("&lt;", "<")
    titre = titre.replace("&gt;", ">")
    # replace multiple spaces with one
    titre = ' '.join(titre.split())
    titre = titre.strip()
    return titre

def preprocess_desc_for_classif(desc, lang='fr'):
    desc = desc.replace('ã', 'é')
    desc = desc.replace('ã©', 'é')
    desc = desc.replace('ã', 'à')
    desc = desc.replace('ã¢', 'â')
    desc = desc.replace('ã§', 'ç')
    desc = desc.replace('ã¨', 'è')
    desc = desc.replace('ãª', 'ê')
    desc = desc.replace('ã®', 'î')
    desc = desc.replace('ã´', 'ô')
    desc = desc.replace('ã', 'â')
    desc = desc.replace('ã', 'ç')
    desc = desc.replace('ã\xa0', 'à')
    desc = desc.replace('â\x80¦', '...')
    desc = desc.replace('', "'")
    desc = desc.replace('â\x80¢', '-')
    desc = desc.replace('ã', 'à')
    desc = desc.replace('â\x80', '')
    desc = desc.replace("’", "'")
    desc = desc.replace("&agrave;", "à")
    desc = desc.replace("&rsquo;", "'")
    desc = desc.replace("&eacute;", "é")
    desc = desc.replace("&egrave;", "è")
    desc = desc.replace("&ecirc;", "ê")
    desc = desc.replace("&ccedil;", "ç")
    desc = desc.replace("&ocirc;", "ô")
    desc = desc.replace("&icirc;", "î")
    desc = desc.replace("&ucirc;", "û")
    desc = desc.replace("&acirc;", "â")
    desc = desc.replace("&nbsp;", " ")
    desc = desc.replace("&bull;", " ")
    desc = desc.replace("&#39;", "'")
    desc = desc.replace("&agrave", "à")
    desc = desc.replace("&rsquo", "'")
    desc = desc.replace("&eacute", "é")
    desc = desc.replace("&egrave", "è")
    desc = desc.replace("&ecirc", "ê")
    desc = desc.replace("&ccedil", "ç")
    desc = desc.replace("&ocirc", "ô")
    desc = desc.replace("&icirc", "î")
    desc = desc.replace("&ucirc", "û")
    desc = desc.replace("&acirc", "â")
    desc = desc.replace("&nbsp", " ")
    desc = desc.replace("&bull", " ")
    desc = desc.replace("&#39", "'")
    desc = desc.replace("&#", "'")
    desc = desc.replace("\r", ". ")
    desc = desc.replace("\n", ". ")
    desc = desc.replace("\t", " ")
    desc = desc.replace("- ", " - ")
    desc = desc.replace("• ", " - ")
    desc = desc.replace('\xa0', ' ')
    desc = desc.replace("&lt;", "<")
    desc = desc.replace("&gt;", ">")
    desc = desc.replace("&lt", "<")
    desc = desc.replace("&gt", ">")
    desc = re.sub(r'\([^)]*\)', '', desc)
    desc = re.sub(r'\+', '', desc)
    if lang == 'fr':
        for w in stop_words2:
            desc = desc.replace(" " + w, " ")
        for w in stop_words:
            desc = desc.replace(" " + w + " ", " ")
    elif lang == 'en':
        for w in stop_words_eng:
            desc = desc.replace(" " + w + " ", " ")
    desc = " ".join([lemmatizer.lemmatize(w) for w in desc.split()])
    desc = desc.replace("«", "")
    desc = desc.replace("»", "")
    desc = re.sub(r'[\d?,.;:!/-]', '', desc).strip().lower()
    desc = re.sub(r'\S*@\S*\s?', '', desc)
    desc = " ".join([w for w in desc.split() if len(w) > 1])
    if lang == 'fr':
        desc = " ".join([w for w in desc.split() if w not in stop_words])
    elif lang == 'en':
        desc = " ".join([w for w in desc.split() if w not in stop_words_eng])
    desc = desc.strip()
    return desc

def preprocess_desc_for_info(desc):
    desc = desc.replace('ã', 'é')
    desc = desc.replace('ã©', 'é')
    desc = desc.replace('ã', 'à')
    desc = desc.replace('ã¢', 'â')
    desc = desc.replace('ã§', 'ç')
    desc = desc.replace('ã¨', 'è')
    desc = desc.replace('ãª', 'ê')
    desc = desc.replace('ã®', 'î')
    desc = desc.replace('ã´', 'ô')
    desc = desc.replace('ã', 'â')
    desc = desc.replace('ã', 'ç')
    desc = desc.replace('ã\xa0', 'à')
    desc = desc.replace('â\x80¦', '...')
    desc = desc.replace('', "'")
    desc = desc.replace('â\x80¢', '-')
    desc = desc.replace('ã', 'à')
    desc = desc.replace('â\x80', '')
    desc = desc.replace("’", "'")
    desc = desc.replace("&agrave;", "à")
    desc = desc.replace("&rsquo;", "'")
    desc = desc.replace("&eacute;", "é")
    desc = desc.replace("&egrave;", "è")
    desc = desc.replace("&ecirc;", "ê")
    desc = desc.replace("&ccedil;", "ç")
    desc = desc.replace("&ocirc;", "ô")
    desc = desc.replace("&icirc;", "î")
    desc = desc.replace("&ucirc;", "û")
    desc = desc.replace("&acirc;", "â")
    desc = desc.replace("&nbsp;", " ")
    desc = desc.replace("&bull;", " ")
    desc = desc.replace("&#39;", "'")
    desc = desc.replace("\t", " ")
    desc = desc.replace("- ", " - ")
    desc = desc.replace("• ", " - ")
    desc = desc.replace('\xa0', ' ')
    desc = desc.replace("&lt;", "<")
    desc = desc.replace("&gt;", ">")
    desc = re.sub(r'\s+', ' ', desc)
    desc = desc.lower()
    desc = desc.strip()
    return desc

job_classif_eng = spacy.load("../../jobs/models/job_classif_eng")
job_classif_fr = spacy.load("../../jobs/models/job_classif_fr")
job_info_extr_eng = spacy.load("../../jobs/models/job_info_extr_eng")
job_info_extr_fr = spacy.load("../../jobs/models/job_info_extr_fr")

with open('../../jobs/models/salaire_dh_model_rf.pkl', 'rb') as f:
    salaire_dh_model = pickle.load(f)
    
with open('../../jobs/models/salaire_eur_model_rf.pkl', 'rb') as f:
    salaire_eur_model = pickle.load(f)

with open('../../jobs/models/le_domaine_dh.pkl', 'rb') as f:
    le_domaine_dh = pickle.load(f)

with open('../../jobs/models/le_domaine_eur.pkl', 'rb') as f:
    le_domaine_eur = pickle.load(f)

# print(list(job_info_extr_eng.get_pipe('ner').labels))

def extract_skills_job(job):
    job = preprocess_desc_for_info(job)
    
    lang = detect(job)
    if lang == 'fr':
        doc = job_info_extr_fr(job)
    elif lang == 'en':
        doc = job_info_extr_eng(job)
    
    skills = []
    for ent in doc.ents:
        if ent.label_ == 'HARD-SKILL':
            skills.append(ent.text)
    return skills

def classify_cv(cv):
    lang = detect(cv)
    if lang == 'fr':
        cv = preprocess_desc_for_classif(cv)
        doc = job_classif_fr(cv)
    elif lang == 'en':
        cv = preprocess_desc_for_classif(cv, lang="en")
        doc = job_classif_eng(cv)
    else:
        return "CV language not supported"

    pred = max(doc.cats, key=doc.cats.get)
    return pred

def classify_job(job):
    lang = detect(job)
    if lang == 'fr':
        job = preprocess_desc_for_classif(job)
        doc = job_classif_fr(job)
    elif lang == 'en':
        job = preprocess_desc_for_classif(job, lang="en")
        doc = job_classif_eng(job)
    else:
        return "Job language not supported"

    pred = max(doc.cats, key=doc.cats.get)
    return pred

labels_job = ["POSTE", "EXPERIENCE", "EDUCATION", "CONTRAT", "SALAIRE", "HARD-SKILL", "SOFT-SKILL", "LANGUE"]

def extract_info_job(job):
    job = preprocess_desc_for_info(job)
    lang = detect(job)
    
    if lang == 'fr':
        doc = job_info_extr_fr(job)
    elif lang == 'en':
        doc = job_info_extr_eng(job)

    results = {lb: set() for lb in labels_job}
    for ent in doc.ents:
        results[ent.label_].add(ent.text)
    
    return results

def embedding_similarity(df):
    cv = st.session_state.info["cv"]
    cv_skills = st.session_state.info["hskills"]
    cv_skills = ", ".join(cv_skills)
    cv_skills = cv_skills.lower()

    doc1 = st.session_state.info_extr_eng(cv_skills)

    df = df[df["domain"] == st.session_state.info["domain"]]

    df["similarity"] = 0

    for row in df.itertuples():
        if type(row.hskills) == float and math.isnan(row.hskills):
            hskills = ""
        else:
            hskills = row.hskills
        doc2 = st.session_state.info_extr_eng(hskills)
        df.loc[row.Index, "similarity"] = doc1.similarity(doc2)
    
    df = df.sort_values(by=["similarity"], ascending=False)
    return df

doctorat = [r"(bac)(\s)?(\+|plus|\-)(\s)?(8)", "phd", "doctorant", "doctorat"]
doctorat_re = re.compile("|".join(doctorat), re.IGNORECASE)

bac5 = [r"(bac)(\s)?(\+|plus|\-)(\s)?(5)", "master", "ingénieur", "ingenieur", "m2"]
bac5_re = re.compile("|".join(bac5), re.IGNORECASE)

bac4 = [r"(bac)(\s)?(\+|plus|\-)(\s)?(4)", "m1"]
bac4_re = re.compile("|".join(bac4), re.IGNORECASE)

bac3 = [r"(bac)(\s)?(\+|plus|\-)(\s)?(3)", "licence", "bachelor", "lp", "lf", "l.p.", "l.f."]
bac3_re = re.compile("|".join(bac3), re.IGNORECASE)

bac2 = [r"(bac)(\s)?(\+|plus|\-)(\s)?(2)", "bts", "dut", "b.t.s", "d.u.t"]
bac2_re = re.compile("|".join(bac2), re.IGNORECASE)

bac1 = [r"(bac)(\s)?(\+|plus|\-)(\s)?(1)"]
bac1_re = re.compile("|".join(bac1), re.IGNORECASE)

def extract_ner_features(desc):
    desc = preprocess_desc_for_info(desc)
    nb_exp = 0
    hs = []
    ss = []
    lg = []
    education = []
    lang = detect(desc)
    if lang == 'fr':
        doc = job_info_extr_fr(desc)
    elif lang == 'en':
        doc = job_info_extr_eng(desc)
    for ent in doc.ents:
        if ent.label_ == "EXPERIENCE":
            if re.search(r"\d+", ent.text):
                nb = int(re.search(r"\d+", ent.text).group(0))
                if nb > nb_exp and nb < 10:
                    nb_exp = nb

        elif ent.label_ == "HARD-SKILL":
            hs.append(ent.text)

        elif ent.label_ == "SOFT-SKILL":
            ss.append(ent.text)

        elif ent.label_ == "LANGUE":
            lg.append(ent.text)
        
        elif ent.label_ == "EDUCATION":
            education.append(ent.text)

    hs = list(set(hs))
    ss = list(set(ss))
    lg = list(set(lg))
    skills_tok2vec = np.average(job_info_extr_fr(" ".join(hs)).vector, axis=0)

    lvl = 0
    education = " ".join(education)
    if doctorat_re.search(education):
        lvl = 6
    elif bac5_re.search(education):
        lvl = 5
    elif bac4_re.search(education):
        lvl = 4
    elif bac3_re.search(education):
        lvl = 3
    elif bac2_re.search(education):
        lvl = 2
    elif bac1_re.search(education):
        lvl = 1

    return nb_exp, len(hs), len(ss), lvl, len(lg), skills_tok2vec


remote_words_indicator = ["remote", "à distance", "a distance", "télétravail", "teletravail", "téletravail", "telétravail"]

def predict_salaire_eur(desc, domaine=None):
    if not domaine:
        domaine = classify_job(desc)
    domaine = le_domaine_eur.transform([domaine])
    desc = preprocess_desc_for_info(desc)
    experience, nb_skills, nb_soft_skills, education_level, nb_lg, skills_tok2vec = extract_ner_features(desc)
    X = pd.DataFrame([[experience, nb_skills, nb_soft_skills, education_level, nb_lg]], 
        columns=["nb_exp", "nb_hard_skills", "nb_soft_skills", "education_level", "nb_langues"])
    X["remote"] = desc.__contains__("|".join(remote_words_indicator))
    X["remote"] = X["remote"].astype(int)
    X["desc_len"] = len(desc)
    X["skills_tok2vec"] = skills_tok2vec
    X["domaine"] = domaine
    salaire = salaire_eur_model.predict(X)
    return int(salaire[0])

def predict_salaire_dh(desc, domaine=None):
    if not domaine:
        domaine = classify_job(desc)
    domaine = le_domaine_dh.transform([domaine])
    desc = preprocess_desc_for_info(desc)
    experience, nb_skills, nb_soft_skills, education_level, nb_lg,skills_tok2vec = extract_ner_features(desc)
    X = pd.DataFrame([[experience, nb_skills, nb_soft_skills, education_level, nb_lg]], 
        columns=["nb_exp", "nb_hard_skills", "nb_soft_skills", "education_level", "nb_langues"])
    X["remote"] = desc.__contains__("|".join(remote_words_indicator))
    X["remote"] = X["remote"].astype(int)
    X["desc_len"] = len(desc)
    X["skills_tok2vec"] = skills_tok2vec
    X["domaine"] = domaine
    salaire = salaire_dh_model.predict(X)
    return int(salaire[0])