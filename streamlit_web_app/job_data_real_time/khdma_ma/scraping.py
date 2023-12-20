import pandas as pd
import requests
from bs4 import BeautifulSoup, SoupStrainer
import json
from langdetect import detect
import sys
sys.path.append("../")
from functions import preprocess_desc_for_classif, extract_skills_job, classify_job, predict_salaire_dh, extract_info_job

cols = ["id", "title", "date", "description", "city", "country", "company", "link", "source", 
        "company_logo", "lang", "domain", "hskills", "salary_estimation", "sskills", "profile",
        "education", "experience", "langues"]

url_base = "https://khdma.ma/"
url = url_base + "offres-emploi-maroc/"

source = "Khdma.ma"

# offres_pd = pd.read_csv("khdma.ma.csv")
# offres_pd = pd.DataFrame(columns=cols)

ids_to_skip = []

company_logo = "https://khdma.ma/design/images/logo.png"

def scrape_khdma_ma(df_path, max_pages):
    try:
        offres_pd = pd.read_csv(df_path)
    except:
        offres_pd = pd.DataFrame(columns=cols)
    while True:
        for i in range(1, max_pages + 1):
            page = requests.get(url + str(i))
            soup = BeautifulSoup(page.text, "lxml", parse_only=SoupStrainer("div", class_="listings-container"))
            all_jobs = soup.find_all("a")
            for job in all_jobs:
                full_job_url = job["href"]
                id = full_job_url.split("-")[len(full_job_url.split("-"))-1]
                
                if not id in offres_pd["id"].astype(str).unique() and not id in ids_to_skip:
                    page = requests.get(full_job_url)
                    soup = BeautifulSoup(page.text, "lxml", parse_only=SoupStrainer("script", type="application/ld+json"))
                    json_data = soup.find("script", type="application/ld+json")
                    if json_data:
                        try:
                            json_data = json.loads(json_data.text[:-8], strict=False)
                            title = json_data["title"]
                            date = json_data["datePosted"]
                            description = json_data["description"]
                            lang = detect(preprocess_desc_for_classif(description))
                            if lang not in ["en", "fr"]:
                                ids_to_skip.append(id)
                                print(source, ":", id, "Not English or French")
                                continue
                            print(source, ":", title, "-", date)
                            city = json_data["jobLocation"]["address"][-1]["addressLocality"]
                            country = json_data["jobLocation"]["address"][-1]["addressCountry"]
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
                                company_logo, lang, domain, hskills, salary_estimation, soft_skills, profile, education, experience, langues]
                            ], columns=cols)])
                            offres_pd.to_csv(df_path, index=False)
                        except Exception as e:
                            ids_to_skip.append(id)
                            print(source, ":", id, e)
                    else:
                        ids_to_skip.append(id)
                        print(source, ":", id, "Not found")