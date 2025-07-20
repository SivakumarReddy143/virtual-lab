
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# App config
st.set_page_config(page_title="EDA & Plots", layout="wide")
st.title("📊 Data Visualization & EDA Dashboard")

# Sidebar mode selection
mode = st.sidebar.radio("Select Mode", ["Basic Plots", "EDA Dashboard"])

# Color palette selection
palette_options = sorted(sns.palettes.SEABORN_PALETTES.keys())
palette = st.sidebar.selectbox("Color Palette", palette_options)
sns.set_palette(palette)

# ---------- BASIC PLOTS ----------
if mode == "Basic Plots":
    st.header("🧩 Basic Plot Generator")

    chart_type = st.sidebar.selectbox("Select Chart Type", [
        "Bar Plot", "Line Plot", "Histogram", "Box Plot", "Pie Chart"
    ])

    x_vals, y_vals = [], []

    if chart_type in ["Bar Plot", "Line Plot", "Pie Chart"]:
        x_input = st.sidebar.text_input("Enter X values (comma separated):")
        y_input = st.sidebar.text_input("Enter Y values (comma separated numbers):")

        if x_input and y_input:
            x_vals = [x.strip() for x in x_input.split(',')]
            try:
                y_vals = list(map(float, y_input.split(',')))
            except ValueError:
                st.sidebar.error("Y values must be numbers.")

    elif chart_type in ["Histogram", "Box Plot"]:
        y_input = st.sidebar.text_input("Enter values (comma separated numbers):")
        if y_input:
            try:
                y_vals = list(map(float, y_input.split(',')))
            except ValueError:
                st.sidebar.error("Values must be numeric.")

    plot_buffer = None

    if st.sidebar.button("Generate Plot"):
        fig, ax = plt.subplots(figsize=(8, 5))
        try:
            if chart_type == "Bar Plot":
                if len(x_vals) != len(y_vals):
                    st.error("X and Y must be the same length.")
                else:
                    df = pd.DataFrame({"X": x_vals, "Y": y_vals})
                    sns.barplot(x="X", y="Y", data=df, ax=ax, palette=palette)
                    ax.set_title("Bar Plot")

            elif chart_type == "Line Plot":
                if len(x_vals) != len(y_vals):
                    st.error("X and Y must be the same length.")
                else:
                    df = pd.DataFrame({"X": x_vals, "Y": y_vals})
                    sns.lineplot(x="X", y="Y", data=df, marker="o", ax=ax)
                    ax.set_title("Line Plot")

            elif chart_type == "Histogram":
                sns.histplot(y_vals, bins=10, kde=True, ax=ax, color=sns.color_palette(palette)[0])
                ax.set_title("Histogram")

            elif chart_type == "Box Plot":
                sns.boxplot(y=y_vals, ax=ax, color=sns.color_palette(palette)[0])
                ax.set_title("Box Plot")

            elif chart_type == "Pie Chart":
                if len(x_vals) != len(y_vals):
                    st.error("Labels and values must match.")
                else:
                    colors = sns.color_palette(palette)[:len(y_vals)]
                    ax.pie(y_vals, labels=x_vals, autopct='%1.1f%%', startangle=90, colors=colors)
                    ax.axis('equal')
                    ax.set_title("Pie Chart")

            st.pyplot(fig)

            # Save plot for download
            plot_buffer = io.BytesIO()
            fig.savefig(plot_buffer, format='png')
            plot_buffer.seek(0)

        except Exception as e:
            st.error(f"An error occurred: {e}")

    if plot_buffer:
        st.download_button("📥 Download Plot as PNG", data=plot_buffer, file_name="plot.png", mime="image/png")

# ---------- EDA DASHBOARD ----------
elif mode == "EDA Dashboard":
    st.header("📈 EDA Dashboard")
    file = st.file_uploader("Upload CSV File", type=["csv"])

    if file:
        df = pd.read_csv(file)
        st.subheader("📄 Data Preview")
        st.dataframe(df)

        st.subheader("📋 Summary")
        st.write(df.describe(include="all").T)

        st.subheader("🧩 Missing Values")
        st.write(df.isnull().sum())

        # Detect column types
        num_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
        cat_initial = df.select_dtypes(include=["object", "category"]).columns.tolist()
        cat_cols = [col for col in cat_initial if df[col].nunique() / len(df) < 0.9]
        dropped = [col for col in cat_initial if col not in cat_cols]
        if dropped:
            st.warning(f"Dropped high-cardinality categorical columns: {', '.join(dropped)}")

        # ---------- UNIVARIATE ----------
        st.subheader("📊 Univariate Plots")
        col1, col2 = st.columns(2)

        with col1:
            if num_cols:
                col = st.selectbox("Numeric Column", num_cols, key="hist")
                fig, ax = plt.subplots()
                sns.kdeplot(df[col], ax=ax)
                ax.set_title(f"Distribution of {col}")
                st.pyplot(fig)

        with col2:
            if cat_cols:
                col = st.selectbox("Categorical Column", cat_cols, key="bar")
                fig1, ax1 = plt.subplots()
                df[col].value_counts().plot(kind="bar", color=sns.color_palette(palette), ax=ax1)
                ax1.set_title(f"Bar Plot of {col}")
                st.pyplot(fig1)

                fig2, ax2 = plt.subplots()
                df[col].value_counts().plot.pie(autopct="%1.1f%%", startangle=90, ax=ax2)
                ax2.set_ylabel("")
                ax2.set_title(f"Pie Chart of {col}")
                st.pyplot(fig2)

        # ---------- CORRELATION ----------
        if len(num_cols) >= 2:
            st.subheader("🔗 Correlation Heatmap")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(df[num_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
            ax.set_title("Correlation Heatmap")
            st.pyplot(fig)

        # ---------- BIVARIATE ----------
        if len(num_cols) >= 2:
            st.subheader("📈 Scatter Plot")
            col_x = st.selectbox("X-axis", num_cols, key="scatter_x")
            col_y = st.selectbox("Y-axis", num_cols, key="scatter_y")
            hue_col = st.selectbox("Hue (Optional)", ["None"] + cat_cols, key="scatter_hue")

            fig, ax = plt.subplots()
            sns.scatterplot(data=df, x=col_x, y=col_y, hue=df[hue_col] if hue_col != "None" else None, ax=ax)
            ax.set_title(f"{col_x} vs {col_y}")
            st.pyplot(fig)

        # ---------- MULTIVARIATE BOX PLOT ----------
        if num_cols and cat_cols:
            st.subheader("📦 Box Plot")
            num = st.selectbox("Numeric Column", num_cols, key="box_num")
            cat = st.selectbox("Categorical Column", cat_cols, key="box_cat")
            hue = st.selectbox("Hue (Optional)", ["None"] + [c for c in cat_cols if c != cat], key="box_hue")

            fig, ax = plt.subplots()
            sns.boxplot(data=df, x=cat, y=num, hue=df[hue] if hue != "None" else None, ax=ax)
            ax.set_title(f"Boxplot of {num} by {cat}" + (f" with hue {hue}" if hue != "None" else ""))
            st.pyplot(fig)

        # ---------- COUNT PLOT WITH HUE ----------
        if cat_cols:
            st.subheader("🧮 Count Plot with Hue")
            cat1 = st.selectbox("Main Category", cat_cols, key="count_main")
            hue_cat = st.selectbox("Hue Category", ["None"] + [c for c in cat_cols if c != cat1], key="count_hue")

            fig, ax = plt.subplots()
            sns.countplot(data=df, x=cat1, hue=df[hue_cat] if hue_cat != "None" else None, ax=ax)
            ax.set_title(f"Count Plot of {cat1}" + (f" with hue {hue_cat}" if hue_cat != "None" else ""))
            plt.xticks(rotation=45)
            st.pyplot(fig)

        # ---------- PAIR PLOT ----------
        if len(num_cols) > 1 and st.checkbox("🔁 Show Pair Plot (slow for large datasets)"):
            st.subheader("🔁 Pair Plot")
            hue = st.selectbox("Hue for Pair Plot", ["None"] + cat_cols, key="pair_hue")
            fig = sns.pairplot(df[num_cols + [hue]] if hue != "None" else df[num_cols], hue=hue if hue != "None" else None)
            st.pyplot(fig)

st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: #f0f2f6;
        color: #888;
        text-align: center;
        padding: 10px 0;
        font-size: 0.9em;
        z-index: 100;
    }
    </style>
    <div class=\"footer\">
        &copy; 2025 Madanapalle Institute of Technology & Science — Virtual Lab for EDA. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)
