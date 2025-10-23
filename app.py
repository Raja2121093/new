import streamlit as st
import pandas as pd
import math
from io import BytesIO

# Streamlit page configuration
st.set_page_config(page_title="Interactive CSV Viewer", layout="wide")
st.title("📄 Interactive CSV Viewer with Pagination & Export")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

def convert_df_to_excel(df: pd.DataFrame):
    """Convert a dataframe to Excel bytes."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8", low_memory=False)
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding="latin1", low_memory=False)
    except Exception as e:
        st.error(f"❌ Error reading CSV: {e}")
        st.stop()

    if df.empty:
        st.warning("⚠️ The uploaded CSV is empty!")
        st.stop()

    # Sidebar for pagination controls
    st.sidebar.header("Pagination Settings")
    rows_per_page = st.sidebar.number_input("Rows per page", min_value=5, max_value=100, value=10, step=5)

    total_rows = len(df)
    total_pages = math.ceil(total_rows / rows_per_page)

    if "page" not in st.session_state:
        st.session_state.page = 1

    st.sidebar.write(f"Total rows: {total_rows} | Total pages: {total_pages}")
    page_input = st.sidebar.number_input("Go to page", min_value=1, max_value=total_pages, value=st.session_state.page, step=1)
    st.session_state.page = page_input

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous") and st.session_state.page > 1:
            st.session_state.page -= 1
    with col3:
        if st.button("Next ➡️") and st.session_state.page < total_pages:
            st.session_state.page += 1

    # Slice the dataframe for current page
    start_idx = (st.session_state.page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page
    page_data = df.iloc[start_idx:end_idx]

    # Display table info and dataframe
    st.markdown(f"**Page {st.session_state.page} of {total_pages}**")
    st.markdown(f"Showing rows {start_idx + 1} to {min(end_idx, total_rows)} of {total_rows}")
    st.dataframe(page_data, use_container_width=True)

    # Export options
    st.sidebar.header("Export Options")
    if st.sidebar.button("📥 Download Current Page as Excel"):
        excel_bytes = convert_df_to_excel(page_data)
        st.sidebar.download_button(
            label="Download Current Page",
            data=excel_bytes,
            file_name=f"page_{st.session_state.page}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    if st.sidebar.button("📥 Download Full CSV as Excel"):
        excel_bytes = convert_df_to_excel(df)
        st.sidebar.download_button(
            label="Download Full CSV",
            data=excel_bytes,
            file_name="full_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("👆 Upload a CSV file to view its contents.")
