import streamlit as st
import pandas as pd
from pathlib import Path

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="EduPro | Student Insights",
    page_icon="🎓",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
BASE_DIR = Path(__file__).resolve().parent

@st.cache_data
def load_data():
    students_path = BASE_DIR / "student_features.csv"
    courses_path = BASE_DIR / "courses.csv"
    transactions_path = BASE_DIR / "transactions_public.csv"

    students = pd.read_csv(students_path)
    courses = pd.read_csv(courses_path)
    transactions = pd.read_csv(transactions_path)

    return students, courses, transactions


try:
    students, courses, transactions = load_data()
except FileNotFoundError as error:
    st.error("Required CSV file dorakaledu.")
    st.write("App file location:", str(BASE_DIR))
    st.write("Expected files:")
    st.code(
        "student_features.csv\n"
        "courses.csv\n"
        "transactions_public.csv"
    )
    st.caption("CSV files anni app.py unna main folder lo undali.")
    st.stop()
except Exception as error:
    st.error("Data load cheyyadam lo problem vachindi.")
    st.code(str(error))
    st.stop()


# ---------------- HEADER ----------------
st.title("🎓 EduPro")
st.subheader(
    "Student Segmentation & Personalized Course Recommendations"
)
st.write(
    "Explore learner segments and discover suitable courses."
)

# ---------------- SIDEBAR ----------------
st.sidebar.header("Navigation")

page = st.sidebar.radio(
    "Choose a page",
    [
        "Dashboard",
        "Learner Profile",
        "Course Recommendations"
    ]
)


# ---------------- DASHBOARD ----------------
if page == "Dashboard":

    st.header("📊 Student Segmentation Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Students", len(students))
    col2.metric("Available Courses", len(courses))
    col3.metric(
        "Student Segments",
        students["Cluster"].nunique()
        if "Cluster" in students.columns else "N/A"
    )

    if "Cluster" in students.columns:

        st.subheader("Students in Each Cluster")

        cluster_counts = (
            students["Cluster"]
            .value_counts()
            .sort_index()
        )

        st.bar_chart(cluster_counts)

        st.subheader("Cluster Summary")

        required_columns = [
            "Cluster",
            "UserID",
            "total_courses",
            "total_spending",
            "average_course_rating"
        ]

        if all(col in students.columns for col in required_columns):

            summary = students.groupby("Cluster").agg(
                Students=("UserID", "count"),
                Avg_Courses=("total_courses", "mean"),
                Avg_Spending=("total_spending", "mean"),
                Avg_Rating=("average_course_rating", "mean")
            ).round(2)

            st.dataframe(summary, use_container_width=True)

        else:
            st.info("Cluster summary ki konni columns available levu.")

    else:
        st.warning("Student data lo Cluster column dorakaledu.")


# ---------------- LEARNER PROFILE ----------------
elif page == "Learner Profile":

    st.header("👩‍🎓 Explore a Learner")

    if "UserID" not in students.columns:
        st.error("Student data lo UserID column dorakaledu.")
        st.stop()

    student_ids = students["UserID"].dropna().astype(str).tolist()

    if not student_ids:
        st.info("Student records available levu.")
        st.stop()

    user_id = st.selectbox("Select Student ID", student_ids)

    student = students[
        students["UserID"].astype(str) == user_id
    ].iloc[0]

    col1, col2, col3 = st.columns(3)

    cluster = student.get("Cluster", "N/A")
    total_courses = student.get("total_courses", "N/A")
    total_spending = student.get("total_spending", "N/A")

    col1.metric(
        "Student Segment",
        str(int(cluster)) if pd.notna(cluster) and cluster != "N/A"
        else "N/A"
    )

    col2.metric(
        "Courses in Transactions",
        str(int(total_courses))
        if pd.notna(total_courses) and total_courses != "N/A"
        else "N/A"
    )

    col3.metric(
        "Total Spending",
        f"{float(total_spending):,.2f}"
        if pd.notna(total_spending) and total_spending != "N/A"
        else "N/A"
    )

    st.subheader("Learning Preferences")

    st.write(
        "**Preferred Category:**",
        student.get("preferred_category", "Not available")
    )

    st.write(
        "**Preferred Level:**",
        student.get("preferred_level", "Not available")
    )

    rating = student.get("average_course_rating", None)

    st.write(
        "**Average Course Rating:**",
        round(float(rating), 2)
        if pd.notna(rating) else "Not available"
    )

    st.info(
        "For privacy, individual transaction history is not displayed "
        "in this public demo."
    )


# ---------------- COURSE RECOMMENDATIONS ----------------
elif page == "Course Recommendations":

    st.header("📚 Personalized Course Recommendations")

    required_student_columns = [
        "UserID",
        "preferred_category",
        "preferred_level"
    ]

    required_course_columns = [
        "CourseID",
        "CourseName",
        "CourseCategory",
        "CourseLevel",
        "CoursePrice",
        "CourseRating"
    ]

    if not all(col in students.columns for col in required_student_columns):
        st.error("Student data lo required preference columns levu.")
        st.stop()

    if not all(col in courses.columns for col in required_course_columns):
        st.error("Course data lo required columns levu.")
        st.stop()

    student_ids = students["UserID"].dropna().astype(str).tolist()

    if not student_ids:
        st.info("Student records available levu.")
        st.stop()

    user_id = st.selectbox("Choose a learner", student_ids)

    student = students[
        students["UserID"].astype(str) == user_id
    ].iloc[0]

    categories = ["Any"] + sorted(
        courses["CourseCategory"].dropna().astype(str).unique().tolist()
    )

    levels = ["Any"] + sorted(
        courses["CourseLevel"].dropna().astype(str).unique().tolist()
    )

    preferred_category = str(student["preferred_category"])
    preferred_level = str(student["preferred_level"])

    category_index = (
        categories.index(preferred_category)
        if preferred_category in categories else 0
    )

    level_index = (
        levels.index(preferred_level)
        if preferred_level in levels else 0
    )

    category = st.selectbox(
        "Course Category",
        categories,
        index=category_index
    )

    level = st.selectbox(
        "Course Level",
        levels,
        index=level_index
    )

    recommendations = courses.copy()

    if category != "Any":
        recommendations = recommendations[
            recommendations["CourseCategory"].astype(str) == category
        ]

    if level != "Any":
        recommendations = recommendations[
            recommendations["CourseLevel"].astype(str) == level
        ]

    recommendations["CourseRating"] = pd.to_numeric(
        recommendations["CourseRating"],
        errors="coerce"
    )

    recommendations = recommendations.sort_values(
        "CourseRating",
        ascending=False,
        na_position="last"
    ).head(5)

    if recommendations.empty:

        st.info(
            "Matching courses dorakaledu. Vere category or level try cheyyi."
        )

    else:

        st.success("Top 5 recommended courses")

        st.dataframe(
            recommendations[
                [
                    "CourseID",
                    "CourseName",
                    "CourseCategory",
                    "CourseLevel",
                    "CoursePrice",
                    "CourseRating"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


# ---------------- FOOTER ----------------
st.divider()

st.caption(
    "EduPro academic project | Student segmentation and course "
    "recommendations based on available student preferences and course ratings."
)