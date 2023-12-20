import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(layout="wide")

if "info" not in st.session_state:
    # switch_page("Upload_CV")
    st.warning("Upload your cv to access your profile and additonal featrues...")
    if st.button("Upload CV"):
        switch_page("Upload_CV")
    
from streamlit_tags import st_tags
import plotly.graph_objects as go
import math
import sys
sys.path.append("../")
from functions import predict_salaire_cv_dh, profile_strength, get_exp_months, get_edu_level, job_classif_eng

domains = list(job_classif_eng.get_pipe('textcat').labels)
domains = sorted(domains)
domains = [domain.capitalize() for domain in domains]

prfl_cv = st.session_state.info["profile"] + " " + " ".join(st.session_state.info["hskills"]) + \
    " " + " ".join(st.session_state.info["sskills"]) + " " + " ".join(st.session_state.info["langs"]) + \
    " " + " ".join(st.session_state.info["edu"]["diploma"]) + " " + " ".join(st.session_state.info["exp"]["job_title"])

prfl_strength = profile_strength(st.session_state.info)

nb_months_exp = get_exp_months(st.session_state.info["exp"])
nb_years_exp = nb_months_exp // 12
nb_months_exp = nb_months_exp % 12

edu_level = get_edu_level(st.session_state.info["edu"])

salary_estimation = predict_salaire_cv_dh(prfl_cv, st.session_state.info["domain"], nb_years_exp, edu_level)
salary_estimation = math.ceil(salary_estimation / 100) * 100

# st.session_state.info
fig = go.Figure(
    go.Indicator(
        mode = "gauge+number",
        value = prfl_strength,
        number = {'suffix': "%"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Profile strength"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "blue"},
            'threshold': {
                'line': {'color': "green", 'width': 4},
                'thickness': 0.75,
                'value': 80}
                }
    )
)
fig.update_layout(height=150, margin=dict(l=50, r=50, t=0, b=0))


with st.sidebar:
    st.subheader("Your profile strength")
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.caption("Your profile strength is calculated based on the information you provided. The more information you provide, the higher your profile strength will be.")

c1, c2 = st.columns(2)
c1.write("**Your profile :**")
c1.markdown("**" + st.session_state.info["fname"] + " " + st.session_state.info["lname"] + "**, " + st.session_state.info["profile"])
c1.write("Education level: **Bac+" + str(edu_level) + "**")
c1.write("Total experience: **" + str(nb_years_exp) + " years, " + str(nb_months_exp) + " months**")
delta = str(salary_estimation - st.session_state.old_salary) + " Dhs" if "old_salary" in st.session_state and salary_estimation - st.session_state.old_salary != 0 else None
c2.metric("Your esimated salary", str(salary_estimation) + " Dhs", delta=delta, help="Salary is estimated based on your experience, education, skills and other inforamtion...")
c2.caption("This is an estimation of your salary based on your profile. The more information you provide, the more accurate the estimation will be.")

st.info("Fields marked with * are required", icon="ℹ")
with st.expander("Contact information", expanded=True):
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    selected_fname = col1.text_input("First name *", value=st.session_state.info["fname"])
    if not selected_fname: col1.error("First name is required")
    
    selected_lname = col2.text_input("Last name *", st.session_state.info["lname"])
    if not selected_lname: col2.error("Last name is required")

    selected_email = col3.text_input("Email *", value=st.session_state.info["email"])
    if not selected_email: col3.error("Email is required")

    selected_phone = col4.text_input("Phone *", value=st.session_state.info["phone"])
    if not selected_phone: col4.error("Phone is required")

    selected_address = st.text_input("Address", value=st.session_state.info["address"])
    
with st.expander("Profile section", expanded=True):
    cl1, cl2 = st.columns(2)
    selected_profile = cl1.text_input("Profile title", value=st.session_state.info["profile"])

    selected_domain = cl2.selectbox("Domain", domains, index=domains.index(st.session_state.info["domain"].capitalize()))

    selected_hskills = st_tags(
        label='Hard skills',
        text='Press enter to add more',
        value=st.session_state.info["hskills"],
        suggestions=st.session_state.info["hskills"],
    )

def delete_edu(i):
    st.session_state.info["edu"]["start_date"].pop(i)
    st.session_state.info["edu"]["end_date"].pop(i)
    st.session_state.info["edu"]["diploma"].pop(i)
    st.session_state.info["edu"]["school"].pop(i)

def add_edu():
    st.session_state.info["edu"]["start_date"].append(None)
    st.session_state.info["edu"]["end_date"].append(None)
    st.session_state.info["edu"]["diploma"].append("")
    st.session_state.info["edu"]["school"].append("")

def delete_exp(i):
    st.session_state.info["exp"]["start_date"].pop(i)
    st.session_state.info["exp"]["end_date"].pop(i)
    st.session_state.info["exp"]["job_title"].pop(i)
    st.session_state.info["exp"]["company"].pop(i)
    st.session_state.info["exp"]["desc"].pop(i)

def add_exp():
    st.session_state.info["exp"]["start_date"].append(None)
    st.session_state.info["exp"]["end_date"].append(None)
    st.session_state.info["exp"]["job_title"].append("")
    st.session_state.info["exp"]["company"].append("")
    st.session_state.info["exp"]["desc"].append("")
    
with st.expander("Education section", expanded=True):
    selected_edu = {"start_date": [], "end_date": [], "diploma": [], "school": []}
    start_dates = st.session_state.info["edu"]["start_date"]
    end_dates = st.session_state.info["edu"]["end_date"]
    diplomas = st.session_state.info["edu"]["diploma"]
    schools = st.session_state.info["edu"]["school"]

    for i, (start_date, end_date, diploma, school) in enumerate(zip(start_dates, end_dates, diplomas, schools)):
        col5, col6 = st.columns(2)
                
        selected_edu["diploma"].append(col5.text_input("Diploma name", value=diploma, key="diploma" + str(i)))
        selected_edu["school"].append(col6.text_input("School name", value=school, key="school" + str(i)))
        col55, col66 = st.columns(2)
        ongoing = col66.checkbox("Ongoing", value=False, key="ongoing_edu" + str(i))
        selected_edu["start_date"].append(col5.date_input("Start date", value=start_date, key="start_date_edu" + str(i)))
        selected_edu["end_date"].append(col6.date_input("End date", value=end_date if not ongoing else None, key="end_date_edu" + str(i), disabled=ongoing))
        st.button("Delete education", key="delete_edu" + str(i), on_click=lambda i=i: delete_edu(i))
        st.divider()

    st.button("Add education", key="add_edu", on_click=lambda: add_edu())

with st.expander("Experience section", expanded=True):
    selected_exp = {"start_date": [], "end_date": [], "job_title": [], "company": [], "desc": []}
    start_dates = st.session_state.info["exp"]["start_date"]
    end_dates = st.session_state.info["exp"]["end_date"]
    job_titles = st.session_state.info["exp"]["job_title"]
    companies = st.session_state.info["exp"]["company"]
    descs = st.session_state.info["exp"]["desc"]
    for i, (start_date, end_date, job_title, company, desc) in enumerate(zip(start_dates, end_dates, job_titles, companies, descs)):
        col7, col8 = st.columns(2)
        col55, col66 = st.columns(2)
        ongoing = col66.checkbox("Ongoing", value=False, key="ongoing_exp" + str(i))
        selected_exp["job_title"].append(col7.text_input("Job Title", value=job_title, key="job_title" + str(i)))
        selected_exp["company"].append(col8.text_input("Company Name", value=company, key="company" + str(i)))
        selected_exp["start_date"].append(col7.date_input("Start date", value=start_date, key="start_date_exp" + str(i)))
        selected_exp["end_date"].append(col8.date_input("End date", value=end_date if not ongoing else None, key="end_date_exp" + str(i), disabled=ongoing))
        selected_exp["desc"].append(st.text_area("Description", value=desc, key="desc" + str(i)))
        st.button("Delete experience", key="delete_exp" + str(i), on_click=lambda i=i: delete_exp(i))
        st.divider()
            
    st.button("Add experience", key="add_exp", on_click=lambda: add_exp())

with st.expander("Other information", expanded=True):
    selected_sskills = st_tags(
        label='Soft skills',
        text='Press enter to add more',
        value=st.session_state.info["sskills"],
        suggestions=st.session_state.info["sskills"]
    )

    selected_langs = st_tags(
        label='Languages',
        text='Press enter to add more',
        value=st.session_state.info["langs"],
        suggestions=st.session_state.info["langs"]
    )

    selected_hobbies = st_tags(
        label='Hobbies',
        text='Press enter to add more',
        value=st.session_state.info["hobbies"],
        suggestions=st.session_state.info["hobbies"]
    )

submit = st.button("Submit")

if submit:
    st.session_state.info = {
        "fname": selected_fname,
        "lname": selected_lname,
        "email": selected_email,
        "phone": selected_phone,
        "address": selected_address,
        "profile": selected_profile,
        "hskills": selected_hskills,
        "edu": selected_edu,
        "exp": selected_exp,
        "sskills": selected_sskills,
        "langs": selected_langs,
        "hobbies": selected_hobbies,
        "cv": st.session_state.info["cv"],
        "domain": selected_domain.lower()
    }
    st.session_state.old_salary = salary_estimation
    st.experimental_rerun()
    # switch_page("Jobs_List")