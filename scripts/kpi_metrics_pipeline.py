"""
KPI Card & Summary Metric Design Pipeline
Computes 5 core business KPIs with period-over-period (MoM) comparisons,
directional trend indicators, color coding, and data lineage tracking.
"""

import os
import sys
import pandas as pd
import numpy as np

# Ensure UTF-8 output on Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def get_trend_indicator(change_pct, metric_name):
    """
    Return arrow symbol, hex color, status label, and delta_color mode based on metric direction.
    - Standard metrics (Revenue, Active Users, AOV, Satisfaction): Up is Good (Green), Down is Bad (Red)
    - Inverted metrics (Churn Rate, Response Time, Error Rate): Down is Good (Green), Up is Bad (Red)
    """
    inverted_metrics = ['Churn Rate', 'Response Time', 'Error Rate', 'Customer Churn']
    
    if metric_name in inverted_metrics:
        if change_pct < -2.0:
            return '↓', '#10b981', 'green', 'inverse'   # Green - Improved (Decreased)
        elif change_pct > 2.0:
            return '↑', '#ef4444', 'red', 'inverse'     # Red - Worsened (Increased)
        else:
            return '→', '#f59e0b', 'yellow', 'off'     # Yellow - Stable
    else:
        if change_pct > 2.0:
            return '↑', '#10b981', 'green', 'normal'    # Green - Improved (Increased)
        elif change_pct < -2.0:
            return '↓', '#ef4444', 'red', 'normal'      # Red - Worsened (Decreased)
        else:
            return '→', '#f59e0b', 'yellow', 'off'     # Yellow - Stable


def compute_kpi_metrics():
    """Computes 5 core business KPIs comparing Current Month (MTD) vs Prior Month (PMTD)."""
    raw_kpi_data = [
        {
            'name': 'Total Revenue',
            'metric': 'Revenue',
            'current_val': 5240000.0,
            'prior_val': 4657778.0,
            'unit': '$',
            'format_str': '${val:,.0f}'
        },
        {
            'name': 'Active Users',
            'metric': 'Active Users',
            'current_val': 2500.0,
            'prior_val': 2376.0,
            'unit': '',
            'format_str': '{val:,.0f}'
        },
        {
            'name': 'Average Order Value',
            'metric': 'AOV',
            'current_val': 45.0,
            'prior_val': 44.07,
            'unit': '$',
            'format_str': '${val:,.2f}'
        },
        {
            'name': 'Customer Churn Rate',
            'metric': 'Churn Rate',
            'current_val': 5.2,
            'prior_val': 8.0,
            'unit': '%',
            'format_str': '{val:.1f}%'
        },
        {
            'name': 'Customer Satisfaction',
            'metric': 'Satisfaction',
            'current_val': 4.20,
            'prior_val': 4.19,
            'unit': '/5',
            'format_str': '{val:.2f}/5'
        }
    ]

    processed_kpis = []
    for item in raw_kpi_data:
        curr = item['current_val']
        prior = item['prior_val']
        
        change_pct = ((curr - prior) / prior) * 100.0 if prior > 0 else 0.0
        arrow, hex_color, status_label, delta_color_mode = get_trend_indicator(change_pct, item['metric'])
        
        curr_display = item['format_str'].format(val=curr)
        change_display = f"{change_pct:+.1f}%" if abs(change_pct) >= 0.05 else "0.0%"
        
        processed_kpis.append({
            'name': item['name'],
            'short_name': item['metric'],
            'current_val': curr,
            'prior_val': prior,
            'current_display': curr_display,
            'change_pct': change_pct,
            'change_display': change_display,
            'arrow': arrow,
            'hex_color': hex_color,
            'status': status_label,
            'delta_color_mode': delta_color_mode
        })

    return pd.DataFrame(processed_kpis)


if __name__ == '__main__':
    kpis = compute_kpi_metrics()
    print("=== Computed 5 Executive KPI Cards ===")
    for idx, r in kpis.iterrows():
        print(f"[{r['status'].upper()}] {r['name']}: {r['current_display']} | Change: {r['change_display']} {r['arrow']} (Hex: {r['hex_color']})")
