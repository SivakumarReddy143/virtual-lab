import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io

# App title and mode selector
st.set_page_config(layout="wide")
st.title("📊 Plot Generator & Data Dashboard")

mode = st.sidebar.radio("Choose Mode", ["Basic Plots", "Dashboard"])

# -----------------------------------
# MODE 1: BASIC PLOTS
# -----------------------------------
if mode == "Basic Plots":
    st.header("🎨 Basic Plot Generator")

    chart_type = st.sidebar.selectbox("Select Chart Type", ["Bar Plot", "Line Plot", "Histogram", "Box Plot", "Pie Chart"])
    palette = st.sidebar.selectbox("Select Color Palette", ["deep", "muted", "pastel", "dark", "colorblind", "Set1", "Set2", "Set3", "husl", "coolwarm"])

    x_vals = []
    y_vals = []

    if chart_type in ["Bar Plot", "Line Plot", "Pie Chart"]:
        x_input = st.sidebar.text_input("Enter X values (comma separated):")
        y_input = st.sidebar.text_input("Enter Y values (comma separated numbers):")

        if x_input and y_input:
            x_vals = [x.strip() for x in x_input.split(',')]
            try:
                y_vals = list(map(float, y_input.split(',')))
            except:
                st.sidebar.error("Y values must be numbers.")

    elif chart_type in ["Histogram", "Box Plot"]:
        y_input = st.sidebar.text_input("Enter values (comma separated numbers):")
        if y_input:
            try:
                y_vals = list(map(float, y_input.split(',')))
            except:
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
                    ax.legend(["Values"], loc="center left", bbox_to_anchor=(1, 0.5))

            elif chart_type == "Line Plot":
                if len(x_vals) != len(y_vals):
                    st.error("X and Y must be the same length.")
                else:
                    df = pd.DataFrame({"X": x_vals, "Y": y_vals})
                    sns.lineplot(x="X", y="Y", data=df, marker="o", ax=ax, palette=palette)
                    ax.set_title("Line Plot")
                    ax.legend(["Line"], loc="center left", bbox_to_anchor=(1, 0.5))

            elif chart_type == "Histogram":
                sns.histplot(y_vals, bins=10, kde=True, ax=ax, color=sns.color_palette(palette)[0])
                ax.set_title("Histogram")
                ax.legend(["Frequency"], loc="center left", bbox_to_anchor=(1, 0.5))

            elif chart_type == "Box Plot":
                sns.boxplot(y=y_vals, ax=ax, color=sns.color_palette(palette)[0])
                ax.set_title("Box Plot")
                ax.legend(["Box"], loc="center left", bbox_to_anchor=(1, 0.5))

            elif chart_type == "Pie Chart":
                if len(x_vals) != len(y_vals):
                    st.error("Labels and values must match.")
                else:
                    colors = sns.color_palette(palette)[:len(y_vals)]
                    ax.pie(y_vals, labels=x_vals, autopct='%1.1f%%', startangle=90, colors=colors)
                    ax.axis('equal')
                    ax.set_title("Pie Chart")
                    ax.legend(x_vals, loc="center left", bbox_to_anchor=(1, 0.5))

            st.pyplot(fig)

            plot_buffer = io.BytesIO()
            fig.savefig(plot_buffer, format='png')
            plot_buffer.seek(0)

        except Exception as e:
            st.error(f"An error occurred: {e}")

    if plot_buffer:
        st.download_button("📥 Download Plot as PNG", data=plot_buffer, file_name="plot.png", mime="image/png")

# -----------------------------------
# MODE 2: DASHBOARD
# -----------------------------------
elif mode == "Dashboard":
    st.header("📈 Automatic Data Dashboard")
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("✅ File uploaded successfully!")
            st.subheader("📄 Data Preview")
            st.dataframe(df.head())

            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            cat_cols = df.select_dtypes(include=['object', 'category']).columns

            st.subheader("🔢 Numeric Distributions")
            for col in numeric_cols:
                fig, ax = plt.subplots()
                sns.histplot(df[col], bins=20, kde=True, ax=ax, color='skyblue')
                ax.set_title(f'Distribution of {col}')
                st.pyplot(fig)

            st.subheader("📦 Box Plots (Outlier Detection)")
            for col in numeric_cols:
                fig, ax = plt.subplots()
                sns.boxplot(y=df[col], ax=ax, color='lightcoral')
                ax.set_title(f'Box Plot of {col}')
                st.pyplot(fig)

            if len(cat_cols) > 0:
                st.subheader("🧩 Categorical Summaries")
                for col in cat_cols:
                    fig, ax = plt.subplots()
                    df[col].value_counts().plot(kind='bar', color='lightgreen', ax=ax)
                    ax.set_title(f'Bar Chart of {col}')
                    ax.set_ylabel('Count')
                    st.pyplot(fig)

            if len(numeric_cols) > 1:
                st.subheader("🔗 Correlation Heatmap")
                fig, ax = plt.subplots(figsize=(10, 6))
                corr = df[numeric_cols].corr()
                sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
                ax.set_title("Correlation Matrix")
                st.pyplot(fig)

        except Exception as e:
            st.error(f"❌ Failed to process file: {e}")
