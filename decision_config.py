"""
Configuration for the Decision Engine scoring and normalization.
Uses Z-Score + Sigmoid normalization pipeline for relative peer-group scoring.
"""

# Weights for each category (Total must sum to 1.0)
CATEGORY_WEIGHTS = {
    'Return Performance': 0.23,
    'Risk': 0.22,
    'Risk-Adjusted Performance': 0.28,
    'Manager Skill vs Benchmark': 0.17,
    'Consistency (Rolling)': 0.10
}

# Individual metric configurations within each category
# Each metric has:
# - id: matching the internal extraction logic
# - name: display name
# - weight: weight within the category (sum of weights in category must be 1.0)
# - steepness: Controls the sigmoid slope applied to the Z-score.
#              Positive for higher-is-better, Negative for lower-is-better.
#              Typical range: 1.5 to 2.5 for standard distribution.
METRIC_CONFIGS = {
    'Return Performance': [
        # CAGR Performance (Total Weight 75%)
        {
            'id': 'static_5y_cagr',
            'name': '5Y CAGR',
            'weight': 0.45,
            'steepness': 1.8
        },
        {
            'id': 'static_3y_cagr',
            'name': '3Y CAGR',
            'weight': 0.30,
            'steepness': 1.7
        },
        # Short term & Calendar Performance (Total Weight 25%)
        {
            'id': 'static_1y_return',
            'name': '1Y Return',
            'weight': 0.10,
            'steepness': 1.4
        },
        {
            'id': 'calendar_avg',
            'name': 'Calendar Avg',
            'weight': 0.07,
            'steepness': 1.5
        },
        {
            'id': 'worst_calendar_year',
            'name': 'Worst Calendar Year',
            'weight': 0.08,
            'steepness': -1.8
        }
    ],
    'Risk': [
        # Static MDD 5Y (Total Weight 35%)
        # Sub-weights: Max DD (70%) -> 0.35 * 0.7 = 0.245
        # Sub-weights: DD Duration (30%) -> 0.35 * 0.3 = 0.105
        {
            'id': 'static_mdd_5y_value',
            'name': 'Max Drawdown (5Y)',
            'weight': 0.245,
            'steepness': -2.3
        },
        {
            'id': 'static_mdd_5y_duration',
            'name': 'MDD Duration (5Y)',
            'weight': 0.105,
            'steepness': -1.7
        },
        # Annualized Volatility (Total Weight 40%)
        # 60/40 split between 5Y and 3Y
        {
            'id': 'static_std_dev_5y',
            'name': 'Std Dev (5Y)',
            'weight': 0.25,
            'steepness': -2.1
        },
        {
            'id': 'static_std_dev_3y',
            'name': 'Std Dev (3Y)',
            'weight': 0.15,
            'steepness': -2.0
        },
        # Downside Risk (Total Weight 18%)
        {
            'id': 'static_ulcer_5y',
            'name': 'Ulcer Index',
            'weight': 0.18,
            'steepness': -2.2
        },
        # Rolling MDD 3Y (Total Weight 7%)
        # Sub-weights: Median (50%), 75th %ile (30%), Worst (20%)
        {
            'id': 'rolling_mdd_3y_median',
            'name': 'Rolling Median DD',
            'weight': 0.035,
            'steepness': -2.2
        },
        {
            'id': 'rolling_mdd_3y_percentile_75',
            'name': 'Rolling 75%ile DD',
            'weight': 0.021,
            'steepness': -2.3
        },
        {
            'id': 'rolling_mdd_3y_worst',
            'name': 'Rolling Worst DD',
            'weight': 0.014,
            'steepness': -2.4
        }
    ],
    'Risk-Adjusted Performance': [
        # Sharpe Ratio (Total Weight 35%) - 60/40 split 5Y/3Y
        {
            'id': 'static_sharpe_5y',
            'name': 'Sharpe Ratio (5Y)',
            'weight': 0.21,
            'steepness': 2.6
        },
        {
            'id': 'static_sharpe_3y',
            'name': 'Sharpe Ratio (3Y)',
            'weight': 0.14,
            'steepness': 2.4
        },
        # Sortino Ratio (Total Weight 30%) - 60/40 split 5Y/3Y
        {
            'id': 'static_sortino_5y',
            'name': 'Sortino Ratio (5Y)',
            'weight': 0.18,
            'steepness': 2.7
        },
        {
            'id': 'static_sortino_3y',
            'name': 'Sortino Ratio (3Y)',
            'weight': 0.12,
            'steepness': 2.5
        },
        # Calmar Ratio (Total Weight 25%) - 60/40 split 5Y/3Y
        {
            'id': 'static_calmar_5y',
            'name': 'Calmar Ratio (5Y)',
            'weight': 0.15,
            'steepness': 2.6
        },
        {
            'id': 'static_calmar_3y',
            'name': 'Calmar Ratio (3Y)',
            'weight': 0.10,
            'steepness': 2.4
        },
        # Treynor Ratio (Total Weight 10%) - 60/40 split 5Y/3Y
        {
            'id': 'static_treynor_5y',
            'name': 'Treynor Ratio (5Y)',
            'weight': 0.06,
            'steepness': 2.0
        },
        {
            'id': 'static_treynor_3y',
            'name': 'Treynor Ratio (3Y)',
            'weight': 0.04,
            'steepness': 1.8
        }
    ],
    'Manager Skill vs Benchmark': [
        # Alpha Generation (Total Weight 45%)
        {
            'id': 'static_alpha_5y',
            'name': 'Alpha (5Y)',
            'weight': 0.25,
            'steepness': 2.2
        },
        {
            'id': 'static_alpha_3y',
            'name': 'Alpha (3Y)',
            'weight': 0.20,
            'steepness': 2.0
        },
        # Risk Efficiency (Total Weight 27%)
        {
            'id': 'static_ir_5y',
            'name': 'Info Ratio (5Y)',
            'weight': 0.15,
            'steepness': 2.7
        },
        {
            'id': 'static_ir_3y',
            'name': 'Info Ratio (3Y)',
            'weight': 0.12,
            'steepness': 2.5
        },
        # Outperformance Frequency (Total Weight 13%)
        {
            'id': 'static_hit_ratio_5y',
            'name': 'Hit Ratio (5Y)',
            'weight': 0.08,
            'steepness': 1.8
        },
        {
            'id': 'static_hit_ratio_3y',
            'name': 'Hit Ratio (3Y)',
            'weight': 0.05,
            'steepness': 1.6
        },
        # Rolling IR Consistency (Total Weight 8%)
        # Sub-weights: Median (40%), % Positive (40%), Std Dev (20%)
        {
            'id': 'rolling_ir_3y_median',
            'name': 'Rolling IR (3Y Median)',
            'weight': 0.032,
            'steepness': 2.6
        },
        {
            'id': 'rolling_ir_3y_positive',
            'name': 'Rolling IR (3Y % > 0)',
            'weight': 0.032,
            'steepness': 2.4
        },
        {
            'id': 'rolling_ir_3y_std',
            'name': 'Rolling IR (3Y Std Dev)',
            'weight': 0.016,
            'steepness': -2.2
        },
        # Rolling Alpha Consistency (Total Weight 7%)
        # Sub-weights: Median (40%), % Positive (40%), Std Dev (20%)
        {
            'id': 'rolling_alpha_3y_median',
            'name': 'Rolling Alpha (3Y Median)',
            'weight': 0.028,
            'steepness': 2.2
        },
        {
            'id': 'rolling_alpha_3y_positive',
            'name': 'Rolling Alpha (3Y % > 0)',
            'weight': 0.028,
            'steepness': 2.0
        },
        {
            'id': 'rolling_alpha_3y_std',
            'name': 'Rolling Alpha (3Y Std Dev)',
            'weight': 0.014,
            'steepness': -2.0
        }
    ],
    'Consistency (Rolling)': [
        # Rolling Returns Consistency (Total Weight 50%)
        # 5Y (30%): Median (50%), 25th% (30%), Std Dev (20%)
        {
            'id': 'rolling_5y_median',
            'name': 'Rolling Returns (5Y Median)',
            'weight': 0.15,
            'steepness': 2.0
        },
        {
            'id': 'rolling_5y_percentile_25',
            'name': 'Rolling Returns (5Y 25th%)',
            'weight': 0.09,
            'steepness': 2.1
        },
        {
            'id': 'rolling_5y_std_dev',
            'name': 'Rolling Returns (5Y Std Dev)',
            'weight': 0.06,
            'steepness': -2.0
        },
        # 3Y (20%): Median (50%), 25th% (30%), Std Dev (20%)
        {
            'id': 'rolling_3y_median',
            'name': 'Rolling Returns (3Y Median)',
            'weight': 0.10,
            'steepness': 1.9
        },
        {
            'id': 'rolling_3y_percentile_25',
            'name': 'Rolling Returns (3Y 25th%)',
            'weight': 0.06,
            'steepness': 2.0
        },
        {
            'id': 'rolling_3y_std_dev',
            'name': 'Rolling Returns (3Y Std Dev)',
            'weight': 0.04,
            'steepness': -1.9
        },

        # Rolling Sharpe Consistency (Total Weight 30%)
        # 5Y (18%): Median (50%), 25th% (30%), Std Dev (20%)
        {
            'id': 'rolling_sharpe_5y_median',
            'name': 'Rolling Sharpe (5Y Median)',
            'weight': 0.09,
            'steepness': 2.5
        },
        {
            'id': 'rolling_sharpe_5y_percentile_25',
            'name': 'Rolling Sharpe (5Y 25th%)',
            'weight': 0.054,
            'steepness': 2.6
        },
        {
            'id': 'rolling_sharpe_5y_std_dev',
            'name': 'Rolling Sharpe (5Y Std Dev)',
            'weight': 0.036,
            'steepness': -2.3
        },
        # 3Y (12%): Median (50%), 25th% (30%), Std Dev (20%)
        {
            'id': 'rolling_sharpe_3y_median',
            'name': 'Rolling Sharpe (3Y Median)',
            'weight': 0.06,
            'steepness': 2.4
        },
        {
            'id': 'rolling_sharpe_3y_percentile_25',
            'name': 'Rolling Sharpe (3Y 25th%)',
            'weight': 0.036,
            'steepness': 2.5
        },
        {
            'id': 'rolling_sharpe_3y_std_dev',
            'name': 'Rolling Sharpe (3Y Std Dev)',
            'weight': 0.024,
            'steepness': -2.2
        },

        # Rolling Hit Ratio Consistency (Total Weight 20%)
        # 5Y (12%): Median (60%), 25th% (40%)
        {
            'id': 'rolling_hit_ratio_5y_median',
            'name': 'Rolling Hit Ratio (5Y Median)',
            'weight': 0.072,
            'steepness': 1.7
        },
        {
            'id': 'rolling_hit_ratio_5y_percentile_25',
            'name': 'Rolling Hit Ratio (5Y 25th%)',
            'weight': 0.048,
            'steepness': 1.8
        },
        # 3Y (8%): Median (60%), 25th% (40%)
        {
            'id': 'rolling_hit_ratio_3y_median',
            'name': 'Rolling Hit Ratio (3Y Median)',
            'weight': 0.048,
            'steepness': 1.6
        },
        {
            'id': 'rolling_hit_ratio_3y_percentile_25',
            'name': 'Rolling Hit Ratio (3Y 25th%)',
            'weight': 0.032,
            'steepness': 1.7
        }
    ]
}
