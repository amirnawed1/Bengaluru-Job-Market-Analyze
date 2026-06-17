import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Set page config
st.set_page_config(
    page_title="Bengaluru Job Market Analyzer",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Bengaluru Job Market Analyzer")
st.markdown("### Real-time insights into Data & Analytics jobs in Bengaluru")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Job Type filter
job_types = ["All"] + list(df["Job Type"].unique())
selected_job_type = st.sidebar.selectbox("Job Type", job_types)

# Experience filter
exp_options = ["All", "Fresher (0-1 years)", "Mid (1-3 years)"]
selected_exp = st.sidebar.selectbox("Experience Level", exp_options)

# Salary filter
min_salary = st.sidebar.slider("Minimum Salary (LPA)", 
                                min_value=float(df["Salary (LPA)"].min()), 
                                max_value=float(df["Salary (LPA)"].max()), 
                                value=float(df["Salary (LPA)"].min()),
                                step=0.5)

# Apply filters
filtered_df = df.copy()

if selected_job_type != "All":
    filtered_df = filtered_df[filtered_df["Job Type"] == selected_job_type]

if selected_exp == "Fresher (0-1 years)":
    filtered_df = filtered_df[filtered_df["Experience"].str.contains("0-1|0-0")]
elif selected_exp == "Mid (1-3 years)":
    filtered_df = filtered_df[filtered_df["Experience"].str.contains("1-3|0-3")]

filtered_df = filtered_df[filtered_df["Salary (LPA)"] >= min_salary]

# ========== KPI METRICS ==========
st.subheader("📈 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Jobs", len(filtered_df))

with col2:
    avg_salary = filtered_df["Salary (LPA)"].mean()
    st.metric("Average Salary", f"₹{avg_salary:.1f} LPA")

with col3:
    if not filtered_df.empty:
        top_company = filtered_df["Company"].value_counts().index[0]
    else:
        top_company = "No data"
    st.metric("Top Hiring Company", top_company)

with col4:
    if not filtered_df.empty:
        fresher_count = len(filtered_df[filtered_df["Experience"].str.contains("0-0|0-1")])
    else:
        fresher_count = 0
    st.metric("Fresher Jobs", fresher_count

st.markdown("---")

# ========== CHARTS ==========
st.subheader("📊 Job Market Insights")

col1, col2 = st.columns(2)

with col1:
    # Top 10 Skills
    st.markdown("### 🔥 Most Demanded Skills")
    
    all_skills = []
    for skills in filtered_df["Skills"]:
        skill_list = [s.strip() for s in skills.split(",")]
        all_skills.extend(skill_list)
    
    skill_counts = Counter(all_skills)
    top_skills = pd.DataFrame(skill_counts.most_common(10), 
                               columns=["Skill", "Count"])
    
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=top_skills, y="Skill", x="Count", palette="viridis", ax=ax)
    ax.set_xlabel("Number of Job Listings")
    ax.set_title("Top 10 Skills Employers Want")
    st.pyplot(fig)

with col2:
    # Top Hiring Companies
    st.markdown("### 🏢 Top Hiring Companies")
    
    top_companies = filtered_df["Company"].value_counts().head(10)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    top_companies.plot(kind="barh", color="coral", ax=ax)
    ax.set_xlabel("Number of Openings")
    ax.set_title("Companies with Most Job Openings")
    ax.invert_yaxis()
    st.pyplot(fig)

# ========== SALARY ANALYSIS ==========
st.markdown("---")
st.subheader("💰 Salary Analysis")

col1, col2 = st.columns(2)

with col1:
    # Salary by Job Type
    st.markdown("### Salary Distribution by Job Type")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=filtered_df, x="Job Type", y="Salary (LPA)", palette="Set2", ax=ax)
    ax.set_title("Salary Range: Full-time vs Internship")
    st.pyplot(fig)

with col2:
    # Average Salary by Experience
    st.markdown("### Average Salary by Experience Level")
    
    def categorize_exp(exp):
        if "0-0" in exp or "0-1" in exp:
            return "Fresher"
        elif "0-2" in exp or "0-3" in exp:
            return "Entry Level"
        else:
            return "Experienced"
    
    filtered_df["Exp Category"] = filtered_df["Experience"].apply(categorize_exp)
    avg_salary_by_exp = filtered_df.groupby("Exp Category")["Salary (LPA)"].mean()
    
    fig, ax = plt.subplots(figsize=(8, 5))
    avg_salary_by_exp.plot(kind="bar", color=["#FF6B6B", "#4ECDC4", "#45B7D1"], ax=ax)
    ax.set_ylabel("Average Salary (LPA)")
    ax.set_title("Salary by Experience Category")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    st.pyplot(fig)

# ========== JOB TITLES ==========
st.markdown("---")
st.subheader("📋 Most Common Job Titles")

job_titles = filtered_df["Job Title"].value_counts().head(10)

fig, ax = plt.subplots(figsize=(10, 5))
job_titles.plot(kind="bar", color="mediumseagreen", ax=ax)
ax.set_xlabel("Job Title")
ax.set_ylabel("Number of Listings")
ax.set_title("Top 10 Job Titles in Demand")
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
st.pyplot(fig)

# ========== RAW DATA ==========
st.markdown("---")
st.subheader("📁 View Raw Data")

if st.checkbox("Show job listings"):
    st.dataframe(filtered_df[["Job Title", "Company", "Skills", "Salary (LPA)", "Experience"]])
    
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name="bengaluru_jobs.csv",
        mime="text/csv"
    )

# ========== INSIGHTS SECTION ==========
st.markdown("---")
st.subheader("💡 Key Insights")

sql_count = sum(1 for skills in filtered_df["Skills"] if "SQL" in skills)
python_count = sum(1 for skills in filtered_df["Skills"] if "Python" in skills)
powerbi_count = sum(1 for skills in filtered_df["Skills"] if "Power BI" in skills)
excel_count = sum(1 for skills in filtered_df["Skills"] if "Excel" in skills)

insight1 = f"• **SQL is king:** {sql_count}/{len(filtered_df)} jobs ({sql_count*100//len(filtered_df)}%) require SQL — it's the #1 skill to learn."
insight2 = f"• **Python is close behind:** {python_count}/{len(filtered_df)} jobs require Python ({python_count*100//len(filtered_df)}%)."
insight3 = f"• **Power BI & Excel matter:** {powerbi_count} jobs need Power BI, {excel_count} need Excel — don't skip these basics."
insight4 = f"• **Average fresher salary:** ₹{filtered_df[filtered_df['Experience'].str.contains('0-0|0-1')]['Salary (LPA)'].mean():.1f} LPA"

st.markdown(insight1)
st.markdown(insight2)
st.markdown(insight3)
st.markdown(insight4)

st.markdown("---")
st.markdown("### 🚀 Made by Amir Nawed | Data Analyst Portfolio Project")
st.markdown("Data sourced from LinkedIn, Naukri, and company career pages")
