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
        "education", "experience", "langues", "deadline"]

url_base = "https://www.emploi.ma"
# url = url_base + "/recherche-jobs-maroc"
url = url_base + "/recherche-jobs-maroc?page="

source = "Emploi.ma"

# offres_pd = pd.read_csv("emploi.ma.csv")
# offres_pd = pd.DataFrame(columns=cols)

ids_to_skip = []

def scrape_emploi_ma(df_path, max_pages):
    try:
        offres_pd = pd.read_csv(df_path)
    except:
        offres_pd = pd.DataFrame(columns=cols)
    while True:
        for i in range(1, max_pages + 1):
            try:
                page = requests.get(url + str(i))
            except:
                print(source, ": Connection timed out")
                continue
            soup = BeautifulSoup(page.text, "lxml", parse_only=SoupStrainer("div", class_="search-results jobsearch-results"))
            all_jobs = soup.find_all("div", class_="job-description-wrapper")
            for job in all_jobs:
                try:
                    company_logo = job.find("div", class_="col-md-1 hidden-sm hidden-xs").find("a").find("img")["src"]
                except:
                    company_logo = job.find("div", class_="col-md-1 hidden-sm hidden-xs").find("img")["src"]

                job_href = job.find("div", class_="col-lg-5 col-md-5 col-sm-5 col-xs-12 job-title").find("h5").find("a")["href"]
                id = job_href.split("-")[len(job_href.split("-"))-1]

                if not id in offres_pd["id"].astype(str).unique() and not id in ids_to_skip:
                    full_job_url = url_base + job_href    
                    page = requests.get(full_job_url)
                    soup = BeautifulSoup(page.text, "lxml", parse_only=SoupStrainer("script", type="application/ld+json"))
                    json_data = soup.find("script", type="application/ld+json")
                    if json_data:
                        try:
                            json_data = json.loads(json_data.text, strict=False)
                            title = json_data["title"]
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