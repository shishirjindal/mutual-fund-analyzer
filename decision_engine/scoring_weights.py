# -*- coding: utf-8 -*-

"""
Category-level weights for the Decision Engine scoring pipeline.
All values must sum to 1.0.
"""

CATEGORY_WEIGHTS = {
    'Return Performance': 0.23,
    'Risk': 0.22,
    'Risk-Adjusted Performance': 0.28,
    'Manager Skill vs Benchmark': 0.17,
    'Consistency (Rolling)': 0.10,
}
