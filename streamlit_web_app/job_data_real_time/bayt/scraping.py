import pandas as pd
import requests
from bs4 import BeautifulSoup, SoupStrainer
import json
from langdetect import detect
from fake_useragent import UserAgent
import sys
sys.path.append("../")
from functions import preprocess_desc_for_classif, extract_skills_job, classify_job, predict_salaire_dh, extract_info_job

cols = ["id", "title", "date", "description", "city", "country", "company", "link", "source", 
        "company_logo", "lang", "domain", "hskills", "salary_estimation", "sskills", "profile",
        "education", "experience", "langues", "deadline"]

url_base = "https://www.bayt.com"
url = url_base + "/en/morocco/jobs/"

source = "Bayt"
bayt_logo = "https://secure.b8cdn.com/images/logos/fb_bayt_new_en.png"

ids_to_skip = []

ua = UserAgent()

def scrape_bayt(df_path):
    try:
        offres_pd = pd.read_csv(df_path)
    except:
        offres_pd = pd.DataFrame(columns=cols)
    while True:
        headers = {"User-Agent": ua.random}
        try:
            page = requests.get(url, headers=headers)
        except:
            print(source, ": Connection timed out")
            continue
        soup = BeautifulSoup(page.text, "lxml", parse_only=SoupStrainer("div", class_="card-content"))
        all_jobs = soup.find_all("li", class_="has-pointer-d")
        for job in all_jobs:

            job_href = job.find("h2", class_="jb-title m0 t-large").find("a")["href"]
            id = job_href.split("-")[len(job_href.split("-"))-1][:-1]

            if not id in offres_pd["id"].astype(str).unique() and not id in ids_to_skip:
                full_job_url = url_base + job_href
                headers = {"User-Agent": ua.random}
                page = requests.get(full_job_url, headers=headers)
                soup = BeautifulSoup(page.text, "lxml")
                if soup.find("div", class_="media-d is-reversed t-center-m").find("a").find("img"):
                    company_logo = "https:" + soup.find("div", class_="media-d is-reversed t-center-m").find("a").find("img")["src"]
                else:
                    company_logo = bayt_logo
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