import streamlit as st
import pandas as pd
import math
from io import BytesIO

# Streamlit page configuration
st.set_page_config(page_title="CSV Viewer", layout="wide")

st.title("📄 CSV Viewer with Pagination & Export")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

def convert_df_to_excel(df: pd.DataFrame):
    """Convert a dataframe to Excel bytes."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        # No need to call writer.save()
    processed_data = output.getvalue()
    return processed_data


if uploaded_file is not None:
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

    # Pagination setup
    rows_per_page = st.number_input("Rows per page", min_value=5, max_value=100, value=10, step=5)
    total_rows = len(df)
    total_pages = math.ceil(total_rows / rows_per_page)

    if "page" not in st.session_state:
        st.session_state.page = 1

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous") and st.session_state.page > 1:
            st.session_state.page -= 1
    with col3:
        if st.button("Next ➡️") and st.session_state.page < total_pages:
            st.session_state.page += 1

    # Calculate indices
    start_idx = (st.session_state.page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page
    page_data = df.iloc[start_idx:end_idx]

    # Show info
    st.write(f"Page {st.session_state.page} of {total_pages}")
    st.write(f"Showing rows {start_idx + 1} to {min(end_idx, total_rows)} of {total_rows}")

    # Display dataframe
    st.dataframe(page_data, use_container_width=True)

    # Export to Excel
    excel_bytes = convert_df_to_excel(df)
    st.download_button(
        label="📥 Download Full CSV as Excel",
        data=excel_bytes,
        file_name="exported_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("👆 Upload a CSV file to view its contents.")
