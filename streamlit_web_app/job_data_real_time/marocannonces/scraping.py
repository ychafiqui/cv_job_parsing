import pandas as pd
import requests
from bs4 import BeautifulSoup, SoupStrainer
import json
from langdetect import detect
from fake_useragent import UserAgent
import sys
sys.path.append("../")
from functions import preprocess_desc_for_classif, extract_skills_job, classify_job, predict_salaire_dh, preprocess_titre, extract_info_job

cols = ["id", "title", "date", "description", "city", "country", "company", "link", "source", 
        "company_logo", "lang", "domain", "hskills", "salary_estimation", "sskills", "profile",
        "education", "experience", "langues", "deadline"]

url_base = "https://www.marocannonces.com/"
url = url_base + "categorie/309/Emploi/Offres-emploi/"

source = "Maroc Annonces"

# offres_pd = pd.read_csv("marocannonces.csv")
# offres_pd = pd.DataFrame(columns=cols)

ids_to_skip = []

ua = UserAgent()

company_logo = "https://play-lh.googleusercontent.com/izzafB_eg6jXsrDvypFFf99XwyjL7J5RvjRRtWylpEc4xqe2OnUnoWWuaYeq-Fcc9A"

def scrape_marocannonces(df_path, max_pages):
    try:
        offres_pd = pd.read_csv(df_path)
    except:
        offres_pd = pd.DataFrame(columns=cols)
    while True:
        for i in range(1, max_pages + 1):
            headers = {"User-Agent": ua.random}
            try:
                page = requests.get(url + str(i) + ".html", headers=headers)
            except:
                print(source, ": Connection timed out")
                continue
            soup = BeautifulSoup(page.text, "lxml", parse_only=SoupStrainer("ul", class_="cars-list"))
            all_jobs = soup.find_all("li")
            for job in all_jobs:
                if job.find("a"):
                    job = job.find("a")
                    full_job_url = url_base + job["href"]
                    id = job["href"][36:].split("/")[0]
                
                    if not id in offres_pd["id"].astype(str).unique() and not id in ids_to_skip:
                        headers = {"User-Agent": ua.random}
                        page = requests.get(full_job_url, headers=headers)
                        soup = BeautifulSoup(page.text, "lxml", parse_only=SoupStrainer("script", type="application/ld+json"))
                        json_data = soup.find("script", type="application/ld+json")
                        if json_data:
                            try:
                                json_data = json.loads(json_data.text, strict=False)
                                title = json_data["title"]
                                title = preprocess_titre(title)
                                date = json_data["datePosted"]
                                deadline = json_data["validThrough"]
                                description = json_data["description"]
                                lang = detect(preprocess_desc_for_classif(description))
                                if lang not in ["en", "fr"]:
                                    ids_to_skip.append(id)
                                    print(source, ":", id, "Not English or French")
                                    continue
                                print(source, ":", title, "-", date)
                                city = json_data["jobLocation"]["address"]["addressLocality"]
                                country = json_data["jobLocation"]["address"]["addressCountry"]
                                company = json_data["hiringOrganization"]["name"]
                                domain = classify_job(description)
                                hskills = extract_skills_job(description)
                                hskills = ", ".join(hskills)
                                salary_estimation = predict_salaire_dh(description)
                                infos = extract_info_job(description)
                                soft_skills = "\n".join(list(infos["SOFT-SKILL"]))
                                profile = "\n".join(list(infos["POSTE"]))
                                education = "\n".join(list(infos["EDUCATION"]))
                                experience = "\n".join(list(infos["EXPERIENCE"]))
                                langues = "\n".join(list(infos["LANGUE"]))
                                offres_pd = pd.concat([offres_pd, pd.DataFrame([
                                    [id, title, date, description, city, country, company, full_job_url, source, 
                                    company_logo, lang, domain, hskills, salary_estimation, soft_skills, profile, 
                                    education, experience, langues, deadline]
                                ], columns=cols)])
                                offres_pd.to_csv(df_path, index=False)
                            except Exception as e:
                                ids_to_skip.append(id)
                                print(source, ":", id, e)
                        else:
                            ids_to_skip.append(id)
                            print(source, ":", id, "Not found")