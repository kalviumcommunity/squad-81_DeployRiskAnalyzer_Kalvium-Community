"""
Streamlit Export Integration Component
Adds one-click export button and download options for CSV, HTML, and PDF reports.
"""

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from export_functions import export_analysis


def render_streamlit_export_sidebar(df, summary_text, charts_dict):
    """
    Renders export controls and download buttons in the Streamlit sidebar.
    
    Args:
        df (pd.DataFrame): Data to export.
        summary_text (str): Executive summary markdown string.
        charts_dict (dict): Plotly charts dictionary.
    """
    st.sidebar.markdown("---")
    st.sidebar.header("📥 Export & Report Generation")
    
    if st.sidebar.button("⚙️ Generate Multi-Format Report"):
        with st.spinner("Generating CSV, PDF, and HTML reports..."):
            report_dir = export_analysis(df, summary_text, charts_dict, 'output')
            st.session_state['latest_report_dir'] = report_dir
            st.sidebar.success(f"✓ Report exported to:\n`{report_dir}`")
            
    # Provide direct download buttons
    st.sidebar.subheader("Direct File Downloads")
    
    # 1. CSV Download
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📊 Download Data (CSV)",
        data=csv_bytes,
        file_name="cleaned_analysis_data.csv",
        mime="text/csv"
    )
    
    # 2. HTML Download (if latest report generated)
    if 'latest_report_dir' in st.session_state:
        html_path = os.path.join(st.session_state['latest_report_dir'], "interactive_report.html")
        pdf_path = os.path.join(st.session_state['latest_report_dir'], "summary_report.pdf")
        
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                html_bytes = f.read()
            st.sidebar.download_button(
                label="🌐 Download Report (HTML)",
                data=html_bytes,
                file_name="interactive_report.html",
                mime="text/html"
            )
            
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.sidebar.download_button(
                label="📄 Download Summary (PDF)",
                data=pdf_bytes,
                file_name="summary_report.pdf",
                mime="application/pdf"
            )


def main():
    """Standalone test runner for Streamlit Export Integration."""
    st.set_page_config(page_title="Streamlit Export Integration Demo", layout="wide")
    st.title("Streamlit Export & Report Generation Demo")
    
    df = pd.DataFrame({
        'order_date': pd.date_range('2024-01-01', periods=30),
        'revenue': [45000 + i*500 for i in range(30)],
        'orders': [150 + i*2 for i in range(30)]
    })
    
    summary = """# Executive Sales & Churn Report
## Summary Findings
- Total Revenue expanded significantly over the past 30 days.
- Support response SLA of <2 hours reduced customer churn by 4x.
"""
    
    fig = go.Figure(data=go.Scatter(x=df['order_date'], y=df['revenue'], mode='lines+markers', name='Revenue'))
    fig.update_layout(title="Revenue Trend over Time")
    
    charts = {'Revenue Trend': fig}
    
    st.subheader("Data Overview")
    st.dataframe(df)
    st.plotly_chart(fig, use_container_width=True)
    
    render_streamlit_export_sidebar(df, summary, charts)


if __name__ == '__main__':
    main()
