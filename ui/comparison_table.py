"""Renders the multi-fund comparison table and CSV download."""

import datetime
import streamlit as st
import pandas as pd
from typing import List, Dict, Any


class ComparisonTable:
    """Renders the multi-fund ranking table and CSV export."""

    @staticmethod
    def render(all_results: List[Dict[str, Any]], selected_category: str) -> None:
        header_label = (
            f"🏆 {selected_category} — Fund Comparison"
            if selected_category else "🏆 Mutual Fund Comparison Summary"
        )
        st.header(header_label)

        comparison_data, raw_comparison_data = [], []
        for metrics in all_results:
            row = {'Scheme Name': metrics['scheme_name'], 'Overall\nScore': metrics['final_score']}
            raw_row = {'Scheme Name': metrics['scheme_name'], 'Overall Score': metrics['final_score']}
            for cat, score in metrics['category_scores'].items():
                row[cat.replace(' ', '\n').replace('-', '-\n')] = score
                raw_row[cat] = score
            comparison_data.append(row)
            raw_comparison_data.append(raw_row)

        comparison_df = pd.DataFrame(comparison_data).sort_values(by='Overall\nScore', ascending=False)
        raw_df = pd.DataFrame(raw_comparison_data).sort_values(by='Overall Score', ascending=False)

        st.subheader("📊 Ranking & Score Breakdown")
        st.table(ComparisonTable._style(comparison_df))

        csv = raw_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Comparison CSV",
            data=csv,
            file_name=f"fund_comparison_{datetime.date.today()}.csv",
            mime='text/csv',
        )

    @staticmethod
    def _style(df: pd.DataFrame):
        return (
            df.set_index('Scheme Name').style
            .format("{:.2f}")
            .background_gradient(cmap='RdYlGn', subset=['Overall\nScore'], low=0.4, high=0.2)
            .set_properties(**{'border': '1px solid #e6e9ef'})
            .applymap(lambda v: 'background-color: #ff4b4b; color: white;'
                      if isinstance(v, (int, float)) and v == 0.0 else '')
            .set_table_styles([
                {'selector': 'thead th', 'props': [('font-weight', 'bold')]},
                {'selector': 'tbody th', 'props': [('font-weight', 'bold')]},
            ])
        )


# Module-level alias for app.py
render = ComparisonTable.render
