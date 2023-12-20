import streamlit as st
from pdfminer.high_level import extract_text
import base64
from streamlit_tags import st_tags
from functions import extract_date_range
from streamlit_extras.switch_page_button import switch_page
import sys
sys.path.append("../")
from functions import classify_cv, job_classif_eng

st.set_page_config(layout="wide")

labels = ["FNAME", "LNAME", "PROFILE", "ADDRESS", "EMAIL", "PHONE", "EDUCATION", "EXPERIENCE", 
          "HSKILL", "SSKILL", "LANGUAGE", "PROJECT", "CERTIFICATION", "HOBBY"]

domains = list(job_classif_eng.get_pipe('textcat').labels)
domains = sorted(domains)
domains = [domain.capitalize() for domain in domains]

with st.spinner('Loading AI models... Please wait.'):
    import spacy
    if 'info_extr_eng_trf' not in st.session_state:
        st.session_state.info_extr_eng_trf = spacy.load("../resumes/model_transformers/model-best")
    if 'info_extr_eng' not in st.session_state:
        st.session_state.info_extr_eng = spacy.load("../resumes/model/model-best")
    if 'exp_edu_extr' not in st.session_state:
        st.session_state.exp_edu_extr = spacy.load("../resumes/model_exp_edu/model-best")

if 'labels_dict' not in st.session_state:
    st.session_state.labels_dict = {}
    for label in labels:
        st.session_state.labels_dict[label] = []

cv_file = st.file_uploader("Upload your CV (only accepts PDF files)", type="pdf")

col01, col02 = st.columns(2)

if cv_file is not None:
    base64_pdf = base64.b64encode(cv_file.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>'
    col01.markdown(pdf_display, unsafe_allow_html=True)

    cv = extract_text(cv_file)
    domain = classify_cv(cv)
    domain = domain.capitalize()

    if "cv" not in st.session_state:
        st.session_state.cv = cv
        doc = st.session_state.info_extr_eng_trf(cv)
        for ent in doc.ents:
            st.session_state.labels_dict[ent.label_].append(ent.text)
        st.toast('Your information was pre-filled from your CV. You can edit it and submit it.', icon='🎉')
    if cv != st.session_state.cv:
        if "labels_dict" in st.session_state:
            st.session_state.labels_dict = {}
            for label in labels:
                st.session_state.labels_dict[label] = []
        doc = st.session_state.info_extr_eng_trf(cv)
        for ent in doc.ents:
            st.session_state.labels_dict[ent.label_].append(ent.text)
        st.session_state.cv = cv
        st.toast('Your information was pre-filled from your CV. You can edit it and submit it.', icon='🎉')

    col02.info("Fields marked with * are required", icon="ℹ")
    with col02.expander("Contact information", expanded=True):
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        if len(st.session_state.labels_dict["FNAME"]) > 0:
            selected_fname = col1.text_input("First name *", value=st.session_state.labels_dict["FNAME"][0])
        else: selected_fname = col1.text_input("First name *")
        if not selected_fname: col1.error("First name is required")
        
        if len(st.session_state.labels_dict["LNAME"]) > 0:
            selected_lname = col2.text_input("Last name *", value=st.session_state.labels_dict["LNAME"][0])
        else: selected_lname = col2.text_input("Last name* ")
        if not selected_lname: col2.error("Last name is required")

        if len(st.session_state.labels_dict["EMAIL"]) > 0:
            selected_email = col3.text_input("Email *", value=st.session_state.labels_dict["EMAIL"][0])
        else: selected_email = col3.text_input("Email *")
        if not selected_email: col3.error("Email is required")

        if len(st.session_state.labels_dict["PHONE"]) > 0:
            selected_phone = col4.text_input("Phone *", value=st.session_state.labels_dict["PHONE"][0])
        else: selected_phone = col4.text_input("Phone *")
        if not selected_phone: col4.error("Phone is required")

        if len(st.session_state.labels_dict["ADDRESS"]) > 0:
            selected_address = st.text_input("Address", value=st.session_state.labels_dict["ADDRESS"][0])
        else:
            selected_address = st.text_input("Address")
        
    with col02.expander("Profile section", expanded=True):
        cl1, cl2 = st.columns(2)
        if len(st.session_state.labels_dict["PROFILE"]) > 0:
            selected_profile = cl1.text_input("Profile title", value=st.session_state.labels_dict["PROFILE"][0])
        else:
            selected_profile = cl1.text_input("Profile title")

        selected_domain = cl2.selectbox("Domain", domains, index=domains.index(domain))

        if len(st.session_state.labels_dict["HSKILL"]) > 0:
            hskills = set(st.session_state.labels_dict["HSKILL"])
            selected_hskills = st_tags(
                label='Hard skills',
                text='Press enter to add more',
                value=list(hskills),
                suggestions=list(hskills),
            )
        else:
            selected_hskills = st_tags(
                label='Hard skills',
                text='Press enter to add more',
                value=[],
                suggestions=[],
            )

    with st.expander("Education section", expanded=True):
        selected_edu = {"start_date": [], "end_date": [], "diploma": [], "school": []}
        if len(st.session_state.labels_dict["EDUCATION"]) > 0:
            for i, edu in enumerate(st.session_state.labels_dict["EDUCATION"]):
                # ongoing = st.toggle("Ongoing", value=False, key="ongoing_edu" + str(i))
                col5, col6 = st.columns(2)
                doc2 = st.session_state.exp_edu_extr(edu)
                date_range, diploma, school = "", "", ""
                for ent in doc2.ents:
                    if ent.label_ == "DATE_RANGE":
                        date_range = ent.text
                    elif ent.label_ == "DEGREE_NAME":
                        diploma = ent.text
                    elif ent.label_ == "SCHOOL_NAME":
                        school = ent.text
                start_date, end_date = extract_date_range(date_range)
                selected_edu["diploma"].append(col5.text_input("Diploma name", value=diploma, key="diploma" + str(i)))
                selected_edu["school"].append(col6.text_input("School name", value=school, key="school" + str(i)))
                col55, col66 = st.columns(2)
                ongoing = col66.checkbox("Ongoing", value=False, key="ongoing_edu" + str(i))
                selected_edu["start_date"].append(col5.date_input("Start date", value=start_date, key="start_date_edu" + str(i)))
                selected_edu["end_date"].append(col6.date_input("End date", value=end_date if not ongoing else None, key="end_date_edu" + str(i), disabled=ongoing))
                st.button("Delete education", key="delete_edu" + str(i), on_click=lambda i=i: st.session_state.labels_dict["EDUCATION"].pop(i))
                st.divider()

        st.button("Add education", key="add_edu", on_click=lambda: st.session_state.labels_dict["EDUCATION"].append(""))

    with st.expander("Experience section", expanded=True):
        selected_exp = {"start_date": [], "end_date": [], "job_title": [], "company": [], "desc": []}
        if len(st.session_state.labels_dict["EXPERIENCE"]) > 0:
            for i, exp in enumerate(st.session_state.labels_dict["EXPERIENCE"]):
                col7, col8 = st.columns(2)
                doc2 = st.session_state.exp_edu_extr(exp)
                date_range, job_title, company, desc = "", "", "", ""
                for ent in doc2.ents:
                    if ent.label_ == "DATE_RANGE":
                        date_range = ent.text
                    elif ent.label_ == "JOB_TITLE":
                        job_title = ent.text
                    elif ent.label_ == "COMPANY_NAME":
                        company = ent.text
                    elif ent.label_ == "DESCRIPTION":
                        desc = ent.text
                start_date, end_date = extract_date_range(date_range)
                col55, col66 = st.columns(2)
                ongoing = col66.checkbox("Ongoing", value=False, key="ongoing_exp" + str(i))
                selected_exp["job_title"].append(col7.text_input("Job Title", value=job_title, key="job_title" + str(i)))
                selected_exp["company"].append(col8.text_input("Company Name", value=company, key="company" + str(i)))
                selected_exp["start_date"].append(col7.date_input("Start date", value=start_date, key="start_date_exp" + str(i)))
                selected_exp["end_date"].append(col8.date_input("End date", value=end_date if not ongoing else None, key="end_date_exp" + str(i), disabled=ongoing))
                selected_exp["desc"].append(st.text_area("Description", value=desc, key="desc" + str(i)))
                st.button("Delete experience", key="delete_exp" + str(i), on_click=lambda i=i: st.session_state.labels_dict["EXPERIENCE"].pop(i))
                st.divider()
                
        st.button("Add experience", key="add_exp", on_click=lambda: st.session_state.labels_dict["EXPERIENCE"].append(""))
    
    # with st.expander("Academic projects", expanded=True):
    #     if len(st.session_state.labels_dict["PROJECT"]) > 0:
    #         for i, proj in enumerate(st.session_state.labels_dict["PROJECT"]):
    #             st.text_area("Project", value=proj, key="proj" + str(i))
    #             st.button("Delete project", key="delete_proj" + str(i), on_click=lambda i=i: st.session_state.labels_dict["PROJECT"].pop(i))
    #     st.button("Add project", key="add_proj", on_click=lambda: st.session_state.labels_dict["PROJECT"].append(""))
    
    # with st.expander("Certifications", expanded=True):
    #     if len(st.session_state.labels_dict["CERTIFICATION"]) > 0:
    #         for i, cert in enumerate(st.session_state.labels_dict["CERTIFICATION"]):
    #             st.text_area("Certification", value=cert, key="cert" + str(i))
    #             st.button("Delete certification", key="delete_cert" + str(i), on_click=lambda i=i: st.session_state.labels_dict["CERTIFICATION"].pop(i))
    #     st.button("Add certification", key="add_cert", on_click=lambda: st.session_state.labels_dict["CERTIFICATION"].append(""))

    with st.expander("Other information", expanded=True):
        if len(st.session_state.labels_dict["SSKILL"]) > 0:
            sskills = set(st.session_state.labels_dict["SSKILL"])
            selected_sskills = st_tags(
                label='Soft skills',
                text='Press enter to add more',
                value=list(sskills),
                suggestions=list(sskills)
            )
        else:
            selected_sskills = st_tags(
                label='Soft skills',
                text='Press enter to add more',
                value=[],
                suggestions=[]
            )
        if len(st.session_state.labels_dict["LANGUAGE"]) > 0:
            langs = set(st.session_state.labels_dict["LANGUAGE"])
            selected_langs = st_tags(
                label='Languages',
                text='Press enter to add more',
                value=list(langs),
                suggestions=list(langs)
            )
        else:
            selected_langs = st_tags(
                label='Languages',
                text='Press enter to add more',
                value=[],
                suggestions=[]
            )
        if len(st.session_state.labels_dict["HOBBY"]) > 0:
            hobbies = set(st.session_state.labels_dict["HOBBY"])
            selected_hobbies = st_tags(
                label='Hobbies',
                text='Press enter to add more',
                value=list(hobbies),
                suggestions=list(hobbies)
            )
        else:
            selected_hobbies = st_tags(
                label='Hobbies',
                text='Press enter to add more',
                value=[],
                suggestions=[]
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
            "cv": cv,
            "domain": selected_domain.lower()
        }
        switch_page("Your_Profile")