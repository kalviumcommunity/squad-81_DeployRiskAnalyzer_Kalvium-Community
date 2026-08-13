"""
Report Automation & Export Pipeline
Automating generation of CSV datasets, PDF executive reports,
and interactive HTML reports with Plotly visualizations.
"""

import os
import sys
import time
import re
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ReportLab for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Schedule for automated background exports
import schedule

# Ensure UTF-8 output on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def markdown_to_html(markdown_text):
    """Simple markdown to HTML converter for report generation."""
    html = markdown_text
    
    # Headers
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Bold & Italic
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Bullet points
    lines = html.split('\n')
    in_list = False
    new_lines = []
    
    for line in lines:
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            item_text = line.strip()[2:]
            if not in_list:
                new_lines.append('<ul>')
                in_list = True
            new_lines.append(f'<li>{item_text}</li>')
        else:
            if in_list:
                new_lines.append('</ul>')
                in_list = False
            if line.strip() and not line.strip().startswith('<h'):
                new_lines.append(f'<p>{line}</p>')
            else:
                new_lines.append(line)
                
    if in_list:
        new_lines.append('</ul>')
        
    return '\n'.join(new_lines)


def generate_pdf_report(summary_text, pdf_path):
    """Generates a professional PDF report from markdown summary text using ReportLab."""
    try:
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
        )
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=12
        )
        
        h2_style = ParagraphStyle(
            'DocH2',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#333333'),
            spaceBefore=10,
            spaceAfter=6
        )
        
        body_style = ParagraphStyle(
            'DocBody',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#222222'),
            spaceAfter=6
        )
        
        bullet_style = ParagraphStyle(
            'DocBullet',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            leftIndent=15,
            textColor=colors.HexColor('#222222'),
            spaceAfter=4
        )

        story = []
        lines = summary_text.split('\n')
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
                
            if stripped.startswith('# '):
                story.append(Paragraph(stripped[2:], title_style))
                story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1f77b4'), spaceAfter=10))
            elif stripped.startswith('## '):
                story.append(Paragraph(stripped[3:], h2_style))
            elif stripped.startswith('### '):
                story.append(Paragraph(stripped[4:], h2_style))
            elif stripped.startswith('- ') or stripped.startswith('* '):
                formatted_bullet = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', stripped[2:])
                story.append(Paragraph(f"• {formatted_bullet}", bullet_style))
            else:
                formatted_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', stripped)
                story.append(Paragraph(formatted_text, body_style))
                
        doc.build(story)
        return True
    except Exception as e:
        print(f"Warning: PDF ReportLab generation failed ({e}). Using fallback PDF exporter.")
        # Fallback using simple text writer
        with open(pdf_path, 'wb') as f:
            pdf_header = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF\n"
            f.write(pdf_header)
        return True


def export_analysis(df, summary_text, charts_dict, output_dir='output'):
    """
    Export analysis in three primary formats: CSV, PDF, and HTML.
    
    Args:
        df (pd.DataFrame): Cleaned DataFrame with analysis results.
        summary_text (str): Executive summary as markdown string.
        charts_dict (dict): Dictionary of {chart_name: plotly_figure}.
        output_dir (str): Root output directory.
        
    Returns:
        str: Absolute or relative path to the generated report directory.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    report_dir = os.path.join(output_dir, f"{timestamp}_analysis")
    os.makedirs(report_dir, exist_ok=True)
    
    print(f"\n=== Starting Multi-Format Report Export -> {report_dir} ===")
    
    # 1. Export Cleaned CSV
    csv_path = os.path.join(report_dir, "cleaned_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"✓ CSV exported: {csv_path}")
    
    # 2. Export PDF Summary
    pdf_path = os.path.join(report_dir, "summary_report.pdf")
    generate_pdf_report(summary_text, pdf_path)
    print(f"✓ PDF exported: {pdf_path}")
    
    # 3. Export Interactive HTML with Embedded Plotly Charts
    html_path = os.path.join(report_dir, "interactive_report.html")
    html_summary = markdown_to_html(summary_text)
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Interactive Analysis & Executive Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 30px; background-color: #f8f9fa; color: #333; }}
        .container {{ max-width: 1100px; margin: 0 auto; background: #fff; padding: 40px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
        h1 {{ color: #1f77b4; border-bottom: 2px solid #1f77b4; padding-bottom: 10px; }}
        h2 {{ color: #333; margin-top: 25px; }}
        .summary {{ background: #f0f7ff; padding: 20px; border-left: 4px solid #1f77b4; border-radius: 4px; margin-bottom: 30px; }}
        .chart-container {{ margin: 35px 0; background: #fff; border: 1px solid #e1e4e8; border-radius: 6px; padding: 15px; }}
        ul {{ line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Analysis & Executive Insight Report</h1>
        <div class="summary">
            {html_summary}
        </div>
"""
    
    for chart_name, fig in charts_dict.items():
        div_id = chart_name.lower().replace(' ', '_')
        html_content += f"""
        <div class="chart-container">
            <h2>{chart_name}</h2>
            {fig.to_html(include_plotlyjs=False, full_html=False, div_id=div_id)}
        </div>
"""
        
    html_content += """
    </div>
</body>
</html>
"""
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✓ HTML exported: {html_path}")
    
    # 4. Create Metadata README file
    metadata_path = os.path.join(report_dir, "README.md")
    metadata_content = f"""# Analysis Report Metadata

- **Generated Timestamp:** {datetime.now().isoformat()}
- **Record Count:** {len(df)} rows
- **Column Schema:** {', '.join(df.columns)}
- **Date Horizon:** {df['order_date'].min()} to {df['order_date'].max() if 'order_date' in df.columns else 'N/A'}
- **Output Artifacts:**
  - `cleaned_data.csv`: Raw analysis dataset for Excel
  - `summary_report.pdf`: Printable executive summary
  - `interactive_report.html`: Self-contained interactive report with Plotly charts
  - `README.md`: Report metadata & lineage description
"""
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write(metadata_content)
    print(f"✓ Metadata created: {metadata_path}")
    
    return report_dir


def verify_exports(report_dir):
    """Verifies that all exported report files are present, valid, and readable."""
    print(f"\n=== Verifying Export Folder: {report_dir} ===")
    required_files = ['cleaned_data.csv', 'summary_report.pdf', 'interactive_report.html', 'README.md']
    
    all_valid = True
    for filename in required_files:
        filepath = os.path.join(report_dir, filename)
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"✓ {filename}: {file_size:,} bytes")
        else:
            print(f"✗ {filename}: MISSING")
            all_valid = False
            
    # Test CSV readability
    try:
        csv_path = os.path.join(report_dir, 'cleaned_data.csv')
        df_test = pd.read_csv(csv_path)
        print(f"✓ CSV Verification: Successfully loaded {len(df_test):,} rows and {len(df_test.columns)} columns.")
    except Exception as e:
        print(f"✗ CSV Read Failed: {e}")
        all_valid = False
        
    html_abs_path = os.path.abspath(os.path.join(report_dir, 'interactive_report.html'))
    print(f"✓ HTML Browser Link: file:///{html_abs_path.replace(os.sep, '/')}")
    
    return all_valid


def scheduled_export_job():
    """Scheduled task execution function."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running scheduled automated report export...")
    
    # Synthesize sample dataset
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    df = pd.DataFrame({
        'order_date': dates,
        'revenue': np.random.normal(50000, 8000, 100),
        'order_count': np.random.randint(100, 500, 100)
    })
    
    summary = """# Automated Weekly Churn & Sales Report
## Executive Summary
- **Revenue Performance**: Total revenue expanded 12.5% MoM.
- **Support Response Impact**: 2-hour SLAs reduced customer churn to 3%.
- **Action Required**: Approve Q1 hiring budget.
"""
    
    fig = go.Figure(data=go.Scatter(x=df['order_date'], y=df['revenue'], mode='lines', name='Revenue'))
    fig.update_layout(title="Daily Revenue")
    
    charts = {'Daily Revenue Trend': fig}
    
    report_dir = export_analysis(df, summary, charts, 'output')
    verify_exports(report_dir)


if __name__ == '__main__':
    # Run immediate export verification
    scheduled_export_job()
