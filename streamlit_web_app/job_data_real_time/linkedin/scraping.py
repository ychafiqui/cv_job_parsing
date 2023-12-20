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

url_base = "https://www.linkedin.com/"

# # anytime
# url = url_base + "jobs/search/?currentJobId=3713439189&geoId=102787409&location=Morocco&origin=JOBS_HOME_LOCATION_HISTORY&refresh=true"

# last 24 hours
url = url_base + "jobs/search/?currentJobId=3775170375&f_TPR=r86400&geoId=102787409&location=Morocco&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=DD"

source = "LinkedIn"
linkedin_logo = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/LinkedIn_Logo.svg/1024px-LinkedIn_Logo.svg.png"

ids_to_skip = []

ua = UserAgent()

def scrape_linkedin(df_path):
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
        soup = BeautifulSoup(page.text, "lxml", parse_only=SoupStrainer("ul", class_="jobs-search__results-list"))
        all_jobs = soup.find_all("li")
        for job in all_jobs:
            try:
                full_job_url = job.find("div").find("a")["href"]
            except:
                continue
            id = job.find("div").get("data-entity-urn")[18:]

            datetime = job.find("time").get("datetime").strip()
            
            if not id in offres_pd["id"].astype(str).unique() and not id in ids_to_skip:
                headers = {"User-Agent": ua.random}
                page = requests.get(full_job_url, headers=headers)
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
                            linkedin_logo, lang, domain, hskills, salary_estimation, soft_skills, profile, 
                            education, experience, langues, deadline]
                        ], columns=cols)])
                        offres_pd.to_csv(df_path, index=False)
                    except Exception as e:
                        ids_to_skip.append(id)
                        print(source, ":", id, e)
                else:
                    try:
                        soup = BeautifulSoup(page.text, "lxml")
                        title = soup.find("h1", class_="top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title").text.strip()
                        company = soup.find("a", class_="topcard__org-name-link topcard__flavor--black-link").text.strip()
                        description = soup.find("div", class_="show-more-less-html__markup show-more-less-html__markup--clamp-after-5 relative overflow-hidden").text.strip()
                        lang = detect(preprocess_desc_for_classif(description))
                        if lang not in ["en", "fr"]:
                            ids_to_skip.append(id)
                            print(source, ":", id, "Not English or French")
                            continue
                        city = soup.find("span", class_="topcard__flavor topcard__flavor--bullet").text.strip()
                        country = "Morocco"
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
                            [id, title, datetime, description, city, country, company, full_job_url, source, 
                            linkedin_logo, lang, domain, hskills, salary_estimation, soft_skills, profile, 
                            education, experience, langues, None]
                        ], columns=cols)])
                        offres_pd.to_csv(df_path, index=False)
                    except:
                        ids_to_skip.append(id)
                        print(source, ":", id, "Error")