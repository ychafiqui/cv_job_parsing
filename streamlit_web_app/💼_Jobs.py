import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_tags import st_tags
import pandas as pd
# import sys
# sys.path.append("../")
from functions import embedding_similarity

st.set_page_config(layout="wide")

if "max_jobs_per_page" not in st.session_state:
    st.session_state.max_jobs_per_page = 10

rekrute = pd.read_csv("./job_data_real_time/rekrute/rekrute.csv")
emploi_ma = pd.read_csv("./job_data_real_time/emploi_ma/emploi.ma.csv")
khdma_ma = pd.read_csv("./job_data_real_time/khdma_ma/khdma.ma.csv")
khdma_ma["country"] = khdma_ma["country"].replace("ma", "Maroc")
marocannonces = pd.read_csv("./job_data_real_time/marocannonces/marocannonces.csv")
bayt = pd.read_csv("./job_data_real_time/bayt/bayt.csv")
linkedin = pd.read_csv("./job_data_real_time/linkedin/linkedin.csv")
linkedin["country"] = linkedin["country"].replace("MA", "Maroc")
df = pd.concat([rekrute, emploi_ma, khdma_ma, marocannonces, bayt, linkedin], ignore_index=True)
df["city"] = df["city"].fillna("")
df["city"] = df["city"].apply(lambda x: x.capitalize())

if "info" in st.session_state:
    st.title("Job recommendations")
    st.success("Based on your profile, we recommend the following jobs")
    col01, col02, col03, col04 = st.columns(4)
    sort = col01.selectbox("Sort by", ["Best match", "Most recent", "Highest salary", "Closest to you"])

else:
    st.title("Jobs around the world")
    st.warning("Upload your cv to get tailored job recommendations and additonal featrues...")
    if st.button("Upload CV"):
        switch_page("Upload_CV")
    col01, col02, col03, col04 = st.columns(4)
    sort = col01.selectbox("Sort by", ["Most recent", "Highest salary"])

domain = col02.multiselect("Domain", df.domain.unique().tolist(), default=[st.session_state.info["domain"]] if "info" in st.session_state else None)
date = col03.selectbox("Date", ["Last 24 hours", "Last 3 days", "Last 7 days", "Last 15 days", "Last 30 days", "Last 12 months"], index=None)
city = col04.selectbox("City", df.city.unique().tolist(), index=None)

with st.expander("Advanced search", expanded=False):
    skills = st_tags(label='Skills', text='Press enter to add more', value=[], suggestions=[])
    cl01, cl02, cl03, cl04 = st.columns(4)
    source = cl01.selectbox("Source", df.source.unique().tolist(), index=None)
    country = cl02.selectbox("Country", df.country.unique().tolist(), index=None)
    language = cl03.selectbox("Language", df.lang.unique().tolist(), index=None)
    salary_range = cl04.slider("Salary range (Dhs)", min_value=3000, max_value=30000, value=(3000, 30000), step=1000)
    company = cl01.selectbox("Company", df.company.unique().tolist(), index=None)
    search = cl02.text_input("Search", value="")
    # st.button("Search")

df['date'] = pd.to_datetime(df['date'], errors='coerce', utc=True).dt.date
# df["date"] = pd.to_datetime(df["date"]).dt.date
today = pd.to_datetime("today").date()

if date == "Last 24 hours":
    df = df[df["date"] == today]
elif date == "Last 3 days":
    df = df[df["date"] >= today - pd.Timedelta(days=3)]
elif date == "Last 7 days":
    df = df[df["date"] >= today - pd.Timedelta(days=7)]
elif date == "Last 15 days":
    df = df[df["date"] >= today - pd.Timedelta(days=15)]
elif date == "Last 30 days":
    df = df[df["date"] >= today - pd.Timedelta(days=30)]
elif date == "Last 12 months":
    df = df[df["date"] >= today.replace(year=today.year - 1)]

if source:
    df = df[df["source"] == source]
if company:
    df = df[df["company"] == company]

if city:
    df = df[df["city"] == city]
if country:
    df = df[df["country"] == country]
if domain:
    df = df[df["domain"].isin(domain)]
if search:
    df = df[df["title"].str.contains(search, case=False)
             | df["company"].str.contains(search, case=False)
             | df["description"].str.contains(search, case=False)]
if skills:
    for skill in skills:
        df = df[df["description"].str.contains(skill, case=False)]
if language:
    df = df[df["lang"] == language]
if salary_range:
    df = df[(df["salary_estimation"] >= salary_range[0]) & (df["salary_estimation"] <= salary_range[1])]

if sort == "Most recent":
    df = df.sort_values(by=["date"], ascending=False)
elif sort == "Best match":
    df = embedding_similarity(df)
elif sort == "Highest salary":
    df = df.sort_values(by=["salary_estimation"], ascending=False)

df2 = df.head(st.session_state.max_jobs_per_page)

jobs = df2.to_dict("records")

if len(jobs) == 0:
    st.warning("No jobs found")
    st.stop()
else:
    for job in jobs:
        expander_title = "**" + job["title"] + " - " + job["company"] + "**"
        if sort == "Best match":
            expander_title += " - " + str(round(job["similarity"] * 100)) + "% Matching"

        with st.expander(expander_title, expanded=True):
            col1, col2 = st.columns([1, 5])
            col1.markdown("<img src='" + job["company_logo"] + "' style='display: block; margin-left: auto; margin-right: auto; object-fit: contain;' width=140 height=140>", unsafe_allow_html=True)
            col2.write(job["date"].strftime("**%d %B %Y**"))
            # col2.write(job["date"])
            address = job['city'] + ", " + job["country"] if job['city'] else job["country"]
            col2.markdown('<div style="margin: -13px 0px; color: darkblue">' + address + '</div>', unsafe_allow_html=True)
            col2.caption("Estimated salary : :blue[***" + str(round(job["salary_estimation"])) + " Dhs**]")
            # col2.caption("Source : **" + job["source"] +"** | Estimated salary : **" + str(round(job["salary_estimation"])) + " Dhs**")
            col2.link_button("Apply for this job on **" + job["source"]+"**", job["link"])

if len(df2) < len(df):
    if st.button("Show more"):
        st.session_state.max_jobs_per_page += 10
        st.experimental_rerun()
        # st.return()