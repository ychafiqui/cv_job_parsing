import streamlit as st
import pandas as pd
import plotly.express as px
import math
import re
import requests

st.set_page_config(layout="wide")

static_data = pd.read_csv("./job_data_static/static_data.csv")

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
df["domain"] = df["domain"].apply(lambda x: x.capitalize())

date = st.selectbox("Period of time", ["Last 24 hours", "Last 3 days", "Last 7 days", "Last 15 days", "Last 30 days", "Last 12 months"], index=4)
df['date'] = pd.to_datetime(df['date'], errors='coerce', utc=True).dt.date
df_backup = df.copy()
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

st.title("Job market insights in Morocco")
st.write("These numbers are based on the data collected from **" + ", ".join(df["source"].unique()[:-1]) + "**" + " and **" + df["source"].unique()[-1] + "**")

tab1, tab2, tab7, tab8, tab3, tab4, tab5 = st.tabs([
    "💼 Job opportunities", "💵 Salary insights", "🎓 Education requirements", "💡 Experience requirements", 
    "🧠 Skill requirements", "🌐 Job boards", "🏢 Companies hiring"])

with tab1:
    cl1, cl2, cl3, cl4 = st.columns(4)
    cl1.metric("Total number of job offers scraped", str(df_backup.shape[0]))
    
    last_month_delta = df_backup[df_backup["date"] >= today - pd.Timedelta(days=30)].shape[0] - df_backup[df_backup["date"] >= today - pd.Timedelta(days=60)].shape[0]
    last_month_delta_perc = round((last_month_delta / df_backup[df_backup["date"] >= today - pd.Timedelta(days=60)].shape[0]) * 100)
    cl2.metric("Number of job offers this month", str(df[df["date"] >= today - pd.Timedelta(days=30)].shape[0]), delta=str(last_month_delta_perc)+"% Compared to last month")

    last_week_delta = df_backup[df_backup["date"] >= today - pd.Timedelta(days=7)].shape[0] - df_backup[df_backup["date"] >= today - pd.Timedelta(days=14)].shape[0]
    last_week_delta_perc = round((last_week_delta / df_backup[df_backup["date"] >= today - pd.Timedelta(days=14)].shape[0]) * 100)
    cl3.metric("Number of job offers this week", str(df[df["date"] >= today - pd.Timedelta(days=7)].shape[0]), delta=str(last_week_delta_perc)+"% Compared to last week")

    last_day_delta = df_backup[df_backup["date"] == today].shape[0] - df_backup[df_backup["date"] == today - pd.Timedelta(days=1)].shape[0]
    last_day_delta_perc = round((last_day_delta / df_backup[df_backup["date"] >= today - pd.Timedelta(days=2)].shape[0]) * 100)
    cl4.metric("Number of job offers today", str(df[df["date"] == today].shape[0]), delta=str(last_day_delta_perc)+"% Compared to yesterday")

    st.subheader("Number of jobs scraped by day")
    df_date = df[df["date"] >= today - pd.Timedelta(days=365)]
    df_date = df_date.groupby("date")["domain"].count().reset_index()
    df_date.columns = ["date", "count"]
    
    df_date["day"] = df_date["date"].apply(lambda x: x.weekday())
    df_date["day"] = df_date["day"].apply(lambda x: "Weekends" if x > 4 else "Weekdays")
    # bar chart
    fig = px.bar(df_date, x="date", y="count", color="day")
    df_date["date"] = pd.to_datetime(df_date["date"])
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.subheader("Job opportunities by domain")
    df_domain = df[df["domain"] != "Job language not supported"]
    df_domain = df_domain["domain"].value_counts().reset_index()
    df_domain.columns = ["domain", "count"]
    df_domain.reset_index(drop=True, inplace=True)
    df_domain.index += 1

    # horizontal barchart
    fig = px.bar(df_domain, x="count", y="domain", orientation='h', category_orders={"domain": df_domain["domain"].tolist()})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    # add labels to the bars
    fig.update_layout(
        annotations=[
            dict(x=xi, y=yi, text=str(xi), xanchor='left', yanchor='middle', showarrow=False) 
                for xi, yi in zip(df_domain["count"], df_domain["domain"])
        ]
    )
    st.plotly_chart(fig, use_container_width=True)
    st.write("**" + df_domain["domain"][1].capitalize() + "** is the most popular domain in the **" + date.lower() + "** with a total of **" + str(df_domain["count"][1]) + " job offers**.")

    # # job contrat type
    # st.subheader("Job opportunities by contract type")
    # internship_words = ["stage", "internship", "stagiare", "pfe"]
    # cdi_words = ["cdi", "permanent", "permanent contract", "contrat à durée indéterminée", "contrat à durée indeterminee"]
    # cdd_words = ["cdd", "temporary", "temporary contract", "contrat à durée déterminée", "contrat à durée déterminée"]
    # freelance_words = ["freelance", "freelancer", "freelancing"]
    # df_stage = df[df["title"].str.contains("|".join(internship_words), case=False) 
    #               | df["description"].str.contains("|".join(internship_words), case=False)]
    # df_cdi = df[df["title"].str.contains("|".join(cdi_words), case=False)
    #             | df["description"].str.contains("|".join(cdi_words), case=False)]
    # df_cdd = df[df["title"].str.contains("|".join(cdd_words), case=False)
    #             | df["description"].str.contains("|".join(cdd_words), case=False)]
    # df_freelance = df[df["title"].str.contains("|".join(freelance_words), case=False)
    #                     | df["description"].str.contains("|".join(freelance_words), case=False)]
    
    # df_contract = pd.DataFrame({"contract": ["Internship", "CDI", "CDD", "Freelance"], 
    #                             "count": [df_stage.shape[0], df_cdi.shape[0], df_cdd.shape[0], df_freelance.shape[0]]})
    # # add not specified
    # df_contract = df_contract.append({"contract": "Not specified", "count": df.shape[0] - df_contract["count"].sum()}, ignore_index=True)
    # df_contract = df_contract.sort_values(by="count", ascending=False)
    # # horizontal barchart
    # fig = px.bar(df_contract, x="count", y="contract", orientation='h', category_orders={"contract": df_contract["contract"].tolist()})
    # fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    # # add labels to the bars
    # fig.update_layout(
    #     annotations=[
    #         dict(x=xi, y=yi, text=str(xi), xanchor='left', yanchor='middle', showarrow=False) 
    #             for xi, yi in zip(df_contract["count"], df_contract["contract"])
    #     ]
    # )
    # st.plotly_chart(fig, use_container_width=True)
    # st.write("**" + df_contract["contract"][0] + "** is the most popular contract type in the **" + date.lower() + "** with a total of **" + str(df_contract["count"][0]) + " job offers**.")

    # # remote jobs
    # st.subheader("Remote job opportunities")
    # remote_words = ["remote", "télétravail", "teletravail", "télé-travail", "tele-travail", "télé travail", "tele travail"]
    # hybrid_words = ["hybrid", "hybride", "teletravail partiel", "télétravail partiel", "partiellement à distance", "partiellement a distance"]
    # onsite_words = ["onsite", "sur site", "sur-site", "sur place", "sur-place", "on-site", "on site", "on place", "on-place"]
    # df_remote = df[df["title"].str.contains("|".join(remote_words), case=False)
    #                  | df["description"].str.contains("|".join(remote_words), case=False)]
    # df_hybrid = df[df["title"].str.contains("|".join(hybrid_words), case=False)
    #                     | df["description"].str.contains("|".join(hybrid_words), case=False)]
    # df_onsite = df[df["title"].str.contains("|".join(onsite_words), case=False)
    #                     | df["description"].str.contains("|".join(onsite_words), case=False)]
    # df_remote = pd.DataFrame({"remote": ["Remote", "Hybrid", "Onsite"], 
    #                             "count": [df_remote.shape[0], df_hybrid.shape[0], df_onsite.shape[0]]})
    # # add not specified
    # df_remote = df_remote.append({"remote": "Not specified", "count": df.shape[0] - df_remote["count"].sum()}, ignore_index=True)
    # df_remote = df_remote.sort_values(by="count", ascending=False)
    # # horizontal barchart
    # fig = px.bar(df_remote, x="count", y="remote", orientation='h', category_orders={"remote": df_remote["remote"].tolist()})
    # fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    # # add labels to the bars
    # fig.update_layout(
    #     annotations=[
    #         dict(x=xi, y=yi, text=str(xi), xanchor='left', yanchor='middle', showarrow=False) 
    #             for xi, yi in zip(df_remote["count"], df_remote["remote"])
    #     ]
    # )
    # st.plotly_chart(fig, use_container_width=True)

with tab2:
    mean_salary = df["salary_estimation"].mean()
    st.metric(label="Average salary in the **" + date.lower() + "**", value=str(round(mean_salary)) + " Dhs")
    st.caption("Note : this is an estimation based on the domain, experience, education and skills required by job offers.")

    st.subheader("Average salary by domain")
    mean_salary_domain = df[df["domain"] != "Job language not supported"]
    mean_salary_domain = mean_salary_domain.groupby("domain")["salary_estimation"].mean().reset_index()
    mean_salary_domain = mean_salary_domain.sort_values(by="salary_estimation", ascending=False)
    mean_salary_domain.reset_index(drop=True, inplace=True)
    mean_salary_domain.index += 1
    # horizontal barchart
    fig = px.bar(mean_salary_domain, x="salary_estimation", y="domain", orientation='h', category_orders={"domain": mean_salary_domain["domain"].tolist()})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    # add labels to the bars
    fig.update_layout(
        annotations=[
            dict(x=xi, y=yi, text=str(xi) + " Dhs", xanchor='left', yanchor='middle', showarrow=False) 
                for xi, yi in zip(mean_salary_domain["salary_estimation"].apply(lambda x: round(x)), mean_salary_domain["domain"])
        ]
    )
    st.plotly_chart(fig, use_container_width=True)
    mean_salary_domain["salary_estimation"] = mean_salary_domain["salary_estimation"].apply(lambda x: str(round(x)) + " Dhs")
    st.write("**" + mean_salary_domain["domain"][1].capitalize() + "** is the domain with the highest average salary in the **" + date.lower() + "** (**" + mean_salary_domain["salary_estimation"][1] + "**).")

    st.subheader("Salary distribution by domain")
    df_domain = df[df["domain"] != "Job language not supported"]
    domain = st.selectbox("Select a domain", df_domain["domain"].unique())
    df_domain = df_domain[df_domain["domain"] == domain]
    fig = px.box(df_domain, x="domain", y="salary_estimation", points="all", color="lang")
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with tab3:
    avg_ng_skills = round(df["hskills"].str.split(", ", expand=True).count(axis=1).mean())
    st.metric("Average number of required skills per job", str(avg_ng_skills))
    st.caption("On average, a job offer in Morocco requires at least " + str(avg_ng_skills) + " skills")

    st.subheader("Most popular skills in the **" + date.lower() + "**")
    skills = df["hskills"].str.split(", ", expand=True).stack().value_counts().reset_index()
    skills.columns = ["hskill", "count"]
    skills = skills.head(10)
    skills.reset_index(drop=True, inplace=True)
    skills.index += 1
    
    # horizontal barchart
    fig = px.bar(skills, x="count", y="hskill", orientation='h', category_orders={"hskill": skills["hskill"].tolist()})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    # add labels to the bars
    fig.update_layout(
        annotations=[
            dict(x=xi, y=yi, text=str(xi), xanchor='left', yanchor='middle', showarrow=False) 
                for xi, yi in zip(skills["count"], skills["hskill"])
        ]
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Most popular skills by domain")
    df_domain = df[df["domain"] != "Job language not supported"]
    domain = st.selectbox("Select a domain", df_domain["domain"].unique(), key="1")
    df_domain = df_domain[df_domain["domain"] == domain]
    skills = df_domain["hskills"].str.split(", ", expand=True).stack().value_counts().reset_index()
    skills.columns = ["hskill", "count"]
    skills = skills.head(10)
    skills.reset_index(drop=True, inplace=True)
    skills.index += 1
    
    # horizontal barchart
    fig = px.bar(skills, x="count", y="hskill", orientation='h', category_orders={"hskill": skills["hskill"].tolist()})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    # add labels to the bars
    fig.update_layout(
        annotations=[
            dict(x=xi, y=yi, text=str(xi), xanchor='left', yanchor='middle', showarrow=False) 
                for xi, yi in zip(skills["count"], skills["hskill"])
        ]
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Most wanted profiles")
    df_profile = df[df["profile"].notna()]
    df_profile = df_profile[df_profile["profile"] != "formation supérieure"]
    df_profile = df_profile["profile"].value_counts().reset_index()
    df_profile.columns = ["profile", "count"]
    df_profile.reset_index(drop=True, inplace=True)
    df_profile = df_profile.head(15)
    # horizontal barchart
    fig = px.bar(df_profile, x="count", y="profile", orientation='h', category_orders={"profile": df_profile["profile"].tolist()})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    # add labels to the bars
    fig.update_layout(
        annotations=[
            dict(x=xi, y=yi, text=str(xi), xanchor='left', yanchor='middle', showarrow=False) 
                for xi, yi in zip(df_profile["count"], df_profile["profile"])
        ]
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Most popular skills by profile")
    profile = st.selectbox("Select a profile", df_profile["profile"].unique())
    df_profile_skills = df[df["profile"] == profile]
    df_profile_skills = df_profile_skills["hskills"].str.split(", ", expand=True).stack().value_counts().reset_index()
    df_profile_skills.columns = ["hskill", "count"]
    df_profile_skills = df_profile_skills.head(10)
    df_profile_skills.reset_index(drop=True, inplace=True)
    df_profile_skills.index += 1
    # horizontal barchart
    fig = px.bar(df_profile_skills, x="count", y="hskill", orientation='h', category_orders={"hskill": df_profile_skills["hskill"].tolist()})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    # add labels to the bars
    fig.update_layout(
        annotations=[
            dict(x=xi, y=yi, text=str(xi), xanchor='left', yanchor='middle', showarrow=False) 
                for xi, yi in zip(df_profile_skills["count"], df_profile_skills["hskill"])
        ]
    )
    st.plotly_chart(fig, use_container_width=True)

    # language requirements
    st.subheader("Language requirements")
    fr_words = ["français", "francais", "french"]
    en_words = ["anglais", "english"]
    ar_words = ["arabe", "arabic"]
    # drop job offers with no language specified
    df = df[df["langues"].notna()]
    df_fr = df[df["langues"].str.contains("|".join(fr_words), case=False)]
    df_en = df[df["langues"].str.contains("|".join(en_words), case=False)]
    df_ar = df[df["langues"].str.contains("|".join(ar_words), case=False)]
    df_lang = pd.DataFrame({"lang": ["French", "English", "Arabic"],
                            "count": [df_fr.shape[0], df_en.shape[0], df_ar.shape[0]]})
    # bar chart
    fig = px.bar(df_lang, x="lang", y="count")
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def get_website_status(url):
    try:
        response = requests.get(url, timeout=1)
        status = "✅ Online" if response.status_code == 200 else "🚫 Offline"
    except:
        status = "🚫 Offline"

    # color red if offline, green if online
    if status == "✅ Online":
        color = "green"
    else:
        color = "#ff0000"
    
    return "<p style='color:" + color + ";'>" + status + "</p>"

with tab4:
    st.subheader("Job boards status")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.markdown("Rekrute")
    col2.markdown("Emploi.ma")
    col3.markdown("Khdma.ma")
    col4.markdown("MarocAnnonces")
    col5.markdown("Bayt")
    col6.markdown("Linkedin")

    with st.spinner("Sending an HTTP request to Rekrute..."):
        rekrute_status = get_website_status("https://www.rekrute.com/")
        col1.markdown(rekrute_status, unsafe_allow_html=True)
    with st.spinner("Sending an HTTP request to Emploi.ma..."):
        emploi_ma_status = get_website_status("https://emploi.ma/")
        col2.markdown(emploi_ma_status, unsafe_allow_html=True)
    with st.spinner("Sending an HTTP request to Khdma.ma..."):
        khdma_ma_status = get_website_status("https://khdma.ma/")
        col3.markdown(khdma_ma_status, unsafe_allow_html=True)
    with st.spinner("Sending an HTTP request to Marocannonces..."):
        marocannonces_status = get_website_status("https://www.marocannonces.com/")
        col4.markdown(marocannonces_status, unsafe_allow_html=True)
    with st.spinner("Sending an HTTP request to Bayt..."):
        bayt_status = get_website_status("https://www.bayt.com/")
        col5.markdown(bayt_status, unsafe_allow_html=True)
    with st.spinner("Sending an HTTP request to Linkedin..."):
        linkedin_status = get_website_status("https://www.linkedin.com/")
        col6.markdown(linkedin_status, unsafe_allow_html=True)

    st.subheader("Job offers collected from each job board")
    st.markdown("The following graph shows the number of job offers collected from each job board in the **" + date.lower() + "**.")
    df_source = df["source"].value_counts().reset_index()
    df_source.columns = ["source", "count"]
    df_source.reset_index(drop=True, inplace=True)
    df_source.index += 1
    # horizontal barchart
    fig = px.bar(df_source, x="count", y="source", orientation='h', category_orders={"source": df_source["source"].tolist()})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    # add labels to the bars
    fig.update_layout(
        annotations=[
            dict(x=xi, y=yi, text=str(xi), xanchor='left', yanchor='middle', showarrow=False) 
                for xi, yi in zip(df_source["count"], df_source["source"])
        ]
    )
    st.plotly_chart(fig, use_container_width=True)
    st.write("**" + df_source["source"][1].capitalize() + "** is the most popular job board in the **" + date.lower() + "** with a total of **" + str(df_source["count"][1]) + " job offers**.")

with tab5:
    st.subheader("Most active companies")
    st.markdown("The following table shows the top 15 companies with the highest number of job offers in the **" + date.lower() + "**.")
    df_company_domain = df.copy()
    df_company_domain = df_company_domain[df_company_domain["company"] != "Confidential"]
    df_company_domain = df_company_domain[df_company_domain["company"] != "Confidentiel"]
    df_company_domain = df_company_domain[df_company_domain["company"] != "Confidentiel"]
    df_company_domain = df_company_domain[df_company_domain["company"] != "CONFIDENTIEL"]
    df_company_domain = df_company_domain[df_company_domain["company"] != "confidentiel"]
    df_company_domain = df_company_domain[df_company_domain["company"] != "Confidentiel "]
    df_company_domain = df_company_domain[df_company_domain["company"] != "SARL"]
    df_company_domain = df_company_domain[df_company_domain["company"] != "Anonyme"]
    df_company_domain = df_company_domain[df_company_domain["company"] != "anonyme"]
    df_company_domain = df_company_domain[df_company_domain["company"] != "ANONYME"]
    df_company_domain = df_company_domain[df_company_domain["company"] != "SA"]
    df_company_domain = df_company_domain[df_company_domain["company"] != "***"]
    df_company_domain = df_company_domain[df_company_domain["company"] != "SP"]
    df_company_domain = df_company_domain[df_company_domain["company"] != "-"]
    df_company_domain = df_company_domain[df_company_domain["company"] != "S.A"]
    df_company = df_company_domain["company"].value_counts().reset_index()
    df_company.columns = ["company", "count"]
    df_company.reset_index(drop=True, inplace=True)
    df_company.index += 1
    df_company = df_company.head(15)
    # horizontal barchart
    fig = px.bar(df_company, x="count", y="company", orientation='h', category_orders={"company": df_company["company"].tolist()})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    # add labels to the bars
    fig.update_layout(
        annotations=[
            dict(x=xi, y=yi, text=str(xi), xanchor='left', yanchor='middle', showarrow=False) 
                for xi, yi in zip(df_company["count"], df_company["company"])
        ]
    )
    st.plotly_chart(fig, use_container_width=True)
    st.write("**" + df_company["company"][1].capitalize() + "** is the most active company in the **" + date.lower() + "** with a total number of **" + str(df_company["count"][1]) + " job offers**.")

    st.subheader("Most active companies by domain")
    df_domain = df_company_domain[df_company_domain["domain"] != "Job language not supported"]
    domain = st.selectbox("Select a domain", df_domain["domain"].unique(), key="2")
    df_domain = df_domain[df_domain["domain"] == domain]
    df_domain = df_domain["company"].value_counts().reset_index()
    df_domain.columns = ["company", "count"]
    df_domain.reset_index(drop=True, inplace=True)
    df_domain.index += 1
    df_domain = df_domain.head(10)
    # horizontal barchart
    fig = px.bar(df_domain, x="count", y="company", orientation='h', category_orders={"company": df_domain["company"].tolist()})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    # add labels to the bars
    fig.update_layout(
        annotations=[
            dict(x=xi, y=yi, text=str(xi), xanchor='left', yanchor='middle', showarrow=False) 
                for xi, yi in zip(df_domain["count"], df_domain["company"])
        ]
    )
    st.plotly_chart(fig, use_container_width=True)
    st.write("**" + df_domain["company"][1].capitalize() + "** is the most active company in the **" + date.lower() + "** in the **" + domain.lower() + "** domain with a total number of **" + str(df_domain["count"][1]) + " job offers**.")

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

def get_edu_level(education):
    if type(education) == float:
        return 0
    else:
        if doctorat_re.search(education):
            return 8
        elif bac5_re.search(education):
            return 5
        elif bac3_re.search(education):
            return 3
        elif bac2_re.search(education):
            return 2
        
def fix_edu_lvl(edu):
    if edu == 0 or math.isnan(edu):
        return "Education not specified"
    else:
        return "Bac+" + str(int(edu))

with tab7:
    df_edu = df["education"].apply(lambda x: get_edu_level(x))
    df_edu = df_edu.apply(lambda x: fix_edu_lvl(x))
    df_edu = df_edu.value_counts().reset_index()
    df_edu.columns = ["education", "count"]
    df_edu = df_edu[df_edu["education"] != "Education not specified"]
    c111, c222 = st.columns(2)
    fig = px.bar(df_edu, x="education", y="count")
    c111.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    fig = px.pie(df_edu, values="count", names="education")
    c222.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.write("Most of the job offers in the **" + date.lower() + "** require at least **" + df_edu["education"][1] + "**.")

    st.subheader("Salary distribution by education level")
    df_salary_by_edu = df[df["domain"] != "Job language not supported"]
    df_salary_by_edu["education"] = df_salary_by_edu["education"].apply(lambda x: get_edu_level(x))
    df_salary_by_edu["education"] = df_salary_by_edu["education"].apply(lambda x: fix_edu_lvl(x))
    df_salary_by_edu = df_salary_by_edu[df_salary_by_edu["education"] != "Education not specified"]
    # mean salary for each education level
    df_salary_by_edu = df_salary_by_edu.groupby("education")["salary_estimation"].mean().reset_index()
    # horizontal bar chart
    fig = px.bar(df_salary_by_edu, x="salary_estimation", y="education", orientation='h', category_orders={"education": ["Bac+2", "Bac+3", "Bac+5", "Bac+8"]})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.subheader("Education requirements by domain")
    df_domain = df[df["domain"] != "Job language not supported"]
    domain = st.selectbox("Select a domain", df_domain["domain"].unique(), key="3")
    df_domain = df_domain[df_domain["domain"] == domain]
    df_edu = df_domain["education"].apply(lambda x: get_edu_level(x))
    df_edu = df_edu.apply(lambda x: fix_edu_lvl(x))
    df_edu = df_edu.value_counts().reset_index()
    df_edu.columns = ["education", "count"]
    df_edu = df_edu[df_edu["education"] != "Education not specified"]
    c1111, c2222 = st.columns(2)
    fig = px.bar(df_edu, x="education", y="count")
    c1111.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    fig = px.pie(df_edu, values="count", names="education")
    c2222.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})



def get_exp_years(exp):
    nb_exp = 0
    if type(exp) == float:
        return 0
    elif re.search(r"\d+", exp):
        nb = int(re.search(r"\d+", exp).group(0))
        if nb > nb_exp and nb < 10:
            nb_exp = nb
        return nb_exp
    else:
        return 0
    
with tab8:
    df_exp = df["experience"].apply(lambda x: get_exp_years(x))
    df_exp = df_exp.value_counts().reset_index()
    df_exp.columns = ["experience", "count"]
    df_exp = df_exp[df_exp["experience"] != 0]
    df_exp["experience"] = df_exp["experience"].replace(1, "0 to 1 year")
    df_exp["experience"] = df_exp["experience"].replace(2, "2 to 3 years")
    df_exp["experience"] = df_exp["experience"].replace(3, "2 to 3 years")
    df_exp["experience"] = df_exp["experience"].replace(4, "4 to 5 years")
    df_exp["experience"] = df_exp["experience"].replace(5, "4 to 5 years")
    df_exp["experience"] = df_exp["experience"].replace(6, "6 to 10 years")
    df_exp["experience"] = df_exp["experience"].replace(7, "6 to 10 years")
    df_exp["experience"] = df_exp["experience"].replace(8, "6 to 10 years")
    df_exp["experience"] = df_exp["experience"].replace(9, "6 to 10 years")
    c1, c2 = st.columns(2)
    fig = px.bar(df_exp, x="experience", y="count")
    c1.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    fig = px.pie(df_exp, values="count", names="experience")
    c2.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.write("Most of the job offers in the **" + date.lower() + "** require at least **" + df_exp["experience"][1] + " of experience**.")

    st.subheader("Experience requirements by domain")
    df_domain = df[df["domain"] != "Job language not supported"]
    domain = st.selectbox("Select a domain", df_domain["domain"].unique(), key="4")
    df_domain = df_domain[df_domain["domain"] == domain]
    df_exp = df_domain["experience"].apply(lambda x: get_exp_years(x))
    df_exp = df_exp.value_counts().reset_index()
    df_exp.columns = ["experience", "count"]
    df_exp = df_exp[df_exp["experience"] != 0]
    df_exp["experience"] = df_exp["experience"].replace(1, "0 to 1 year")
    df_exp["experience"] = df_exp["experience"].replace(2, "2 to 3 years")
    df_exp["experience"] = df_exp["experience"].replace(3, "2 to 3 years")
    df_exp["experience"] = df_exp["experience"].replace(4, "4 to 5 years")
    df_exp["experience"] = df_exp["experience"].replace(5, "4 to 5 years")
    df_exp["experience"] = df_exp["experience"].replace(6, "6 to 10 years")
    df_exp["experience"] = df_exp["experience"].replace(7, "6 to 10 years")
    df_exp["experience"] = df_exp["experience"].replace(8, "6 to 10 years")
    df_exp["experience"] = df_exp["experience"].replace(9, "6 to 10 years")
    c11, c22 = st.columns(2)
    fig = px.bar(df_exp, x="experience", y="count")
    c11.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    fig = px.pie(df_exp, values="count", names="experience")
    c22.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # salary and experience
    st.subheader("Salary distribution by experience level")
    df_salary_by_exp = df[df["domain"] != "Job language not supported"]
    df_salary_by_exp = df_salary_by_exp[df_salary_by_exp["domain"] == domain]
    df_salary_by_exp["experience"] = df_salary_by_exp["experience"].apply(lambda x: get_exp_years(x))
    df_salary_by_exp = df_salary_by_exp[df_salary_by_exp["experience"] != 0]
    df_salary_by_exp["experience"] = df_salary_by_exp["experience"].replace(1, "0 to 1 year")
    df_salary_by_exp["experience"] = df_salary_by_exp["experience"].replace(2, "2 to 3 years")
    df_salary_by_exp["experience"] = df_salary_by_exp["experience"].replace(3, "2 to 3 years")
    df_salary_by_exp["experience"] = df_salary_by_exp["experience"].replace(4, "4 to 5 years")
    df_salary_by_exp["experience"] = df_salary_by_exp["experience"].replace(5, "4 to 5 years")
    df_salary_by_exp["experience"] = df_salary_by_exp["experience"].replace(6, "6 to 10 years")
    df_salary_by_exp["experience"] = df_salary_by_exp["experience"].replace(7, "6 to 10 years")
    df_salary_by_exp["experience"] = df_salary_by_exp["experience"].replace(8, "6 to 10 years")
    df_salary_by_exp["experience"] = df_salary_by_exp["experience"].replace(9, "6 to 10 years")
    # mean salary for each experience level
    df_salary_by_exp = df_salary_by_exp.groupby("experience")["salary_estimation"].mean().reset_index()
    # horizontal bar chart
    fig = px.bar(df_salary_by_exp, x="salary_estimation", y="experience", orientation='h', category_orders={"experience": ["0 to 1 year", "2 to 3 years", "4 to 5 years", "6 to 10 years"]})
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    # add labels to the bars
    fig.update_layout(
        annotations=[
            dict(x=xi, y=yi, text=str(round(xi)) + " Dhs", xanchor='left', yanchor='middle', showarrow=False) 
                for xi, yi in zip(df_salary_by_exp["salary_estimation"], df_salary_by_exp["experience"])
        ]
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    