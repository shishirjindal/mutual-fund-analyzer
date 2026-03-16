# -*- coding: utf-8 -*-

"""
Category-level weights for the Decision Engine scoring pipeline.
All values must sum to 1.0.
"""

RISK_PROFILES = {
    'Balanced': {
        'Return Performance':        0.25,
        'Risk':                      0.25,
        'Risk-Adjusted Performance': 0.25,
        'Manager Skill vs Benchmark':0.15,
        'Consistency (Rolling)':     0.10,
    },
    'Conservative': {
        'Return Performance':        0.15,
        'Risk':                      0.35,
        'Risk-Adjusted Performance': 0.25,
        'Manager Skill vs Benchmark':0.10,
        'Consistency (Rolling)':     0.15,
    },
    'Aggressive': {
        'Return Performance':        0.35,
        'Risk':                      0.15,
        'Risk-Adjusted Performance': 0.25,
        'Manager Skill vs Benchmark':0.20,
        'Consistency (Rolling)':     0.05,
    },
}
