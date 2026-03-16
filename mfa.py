#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-

"""
Mutual Fund Analyzer

This script calculates various types of returns and risk metrics for mutual fund schemes.
"""

import logging
import datetime
from typing import Dict, Any, Optional
from constants.constants import Constants
from fetchers.scheme_fetcher import SchemeFetcher
from fetchers.benchmark_fetcher import BenchmarkFetcher
from calculators.rolling.rolling_returns_calculator import RollingReturnsCalculator
from calculators.rolling.calendar_year_returns_calculator import CalendarYearReturnsCalculator
from calculators.static.static_standard_deviation_calculator import StaticStandardDeviationCalculator
from calculators.static.static_downside_deviation_calculator import StaticDownsideDeviationCalculator
from calculators.rolling.rolling_standard_deviation_calculator import RollingStandardDeviationCalculator
from calculators.static.static_sharpe_ratio_calculator import StaticSharpeRatioCalculator
from calculators.rolling.rolling_sharpe_ratio_calculator import RollingSharpeRatioCalculator
from calculators.static.static_sortino_ratio_calculator import StaticSortinoRatioCalculator
from calculators.rolling.rolling_sortino_ratio_calculator import RollingSortinoRatioCalculator
from calculators.static.static_drawdown_calculator import StaticDrawdownCalculator
from calculators.static.static_alpha_calculator import StaticAlphaCalculator
from calculators.static.static_beta_calculator import StaticBetaCalculator
from calculators.static.static_information_ratio_calculator import StaticInformationRatioCalculator
from calculators.static.static_treynor_ratio_calculator import StaticTreynorRatioCalculator
from calculators.static.static_calmar_ratio_calculator import StaticCalmarRatioCalculator
from calculators.static.static_ulcer_index_calculator import StaticUlcerIndexCalculator
from calculators.rolling.rolling_alpha_calculator import RollingAlphaCalculator
from calculators.rolling.rolling_beta_calculator import RollingBetaCalculator
from calculators.rolling.rolling_information_ratio_calculator import RollingInformationRatioCalculator
from calculators.static.static_hit_ratio_calculator import StaticHitRatioCalculator
from calculators.rolling.rolling_hit_ratio_calculator import RollingHitRatioCalculator
from calculators.rolling.rolling_drawdown_calculator import RollingDrawdownCalculator
from calculators.rolling.worst_calendar_year_calculator import WorstCalendarYearCalculator
from decision_engine.decision_engine import DecisionEngine




class MutualFundAnalyzer:
    """Analyzer for mutual fund parameters including returns, risk measures, and performance metrics."""
    
    def __init__(self, scheme_code: str):
        """
        Initialize the calculator and fetch scheme data.
        
        Initializes instance variables:
        - years_to_calculate: List of years for calendar year returns calculation
        - scheme_code: Mutual fund scheme code
        - scheme_data: Historical NAV data for the scheme
        
        Args:
            scheme_code: Mutual fund scheme code
        """
        self.years_to_calculate = [datetime.date.today().year - i for i in range(1, Constants.NUM_CALENDAR_YEARS + 1)]
        self.scheme_code = scheme_code
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.scheme_data = SchemeFetcher().fetch(self.scheme_code)
        self.benchmark_data = BenchmarkFetcher().fetch()
        
        # Initialize results variables
        self.rolling_data: Dict[str, Any] = {}
        self.calendar_data: Dict[str, Any] = {}
        self.static_std_dev_data: Dict[str, Any] = {}
        self.static_downside_dev_data: Dict[str, Any] = {}
        self.rolling_std_dev_data: Dict[str, Any] = {}
        self.static_sharpe_data: Dict[str, Any] = {}
        self.rolling_sharpe_data: Dict[str, Any] = {}
        self.static_sortino_data: Dict[str, Any] = {}
        self.rolling_sortino_data: Dict[str, Any] = {}
        self.static_drawdown_data: Dict[str, Any] = {}
        self.static_alpha_data: Dict[str, Any] = {}
        self.static_beta_data: Dict[str, Any] = {}
        self.static_information_ratio_data: Dict[str, Any] = {}
        self.static_treynor_ratio_data: Dict[str, Any] = {}
        self.static_calmar_ratio_data: Dict[str, Any] = {}
        self.static_ulcer_index_data: Dict[str, Any] = {}
        self.rolling_alpha_data: Dict[str, Any] = {}
        self.rolling_beta_data: Dict[str, Any] = {}
        self.rolling_information_ratio_data: Dict[str, Any] = {}
        self.static_hit_ratio_data: Dict[str, Any] = {}
        self.rolling_hit_ratio_data: Dict[str, Any] = {}
        self.rolling_drawdown_data: Dict[str, Any] = {}
        self.worst_calendar_data: Dict[str, Any] = {}

    def _run_step(self, step_name: str, fn, *args, **kwargs):
        """Run a single calculation step, logging outcome. Returns empty dict or list on failure."""
        scheme_name = self.scheme_data.get('scheme_name', self.scheme_code) if self.scheme_data else self.scheme_code
        try:
            result = fn(*args, **kwargs)
            return result
        except Exception as e:
            self.logger.error("[%s] Failed: %s — %s", scheme_name, step_name, e)
            # Return same empty type as expected by callers
            return [] if step_name.startswith("Rolling") else {}

    def get_metrics(self) -> Dict[str, Any]:
        """Return all calculated metrics as a dictionary for the UI or Decision Engine."""
        return {
            'scheme_name': self.scheme_data.get('scheme_name', 'Unknown') if self.scheme_data else 'Unknown',
            'rolling_data': self.rolling_data,
            'calendar_data': self.calendar_data,
            'static_std_dev_data': self.static_std_dev_data,
            'static_downside_dev_data': self.static_downside_dev_data,
            'rolling_std_dev_data': self.rolling_std_dev_data,
            'static_sharpe_data': self.static_sharpe_data,
            'rolling_sharpe_data': self.rolling_sharpe_data,
            'static_sortino_data': self.static_sortino_data,
            'rolling_sortino_data': self.rolling_sortino_data,
            'static_drawdown_data': self.static_drawdown_data,
            'rolling_drawdown_data': self.rolling_drawdown_data,
            'static_alpha_data': self.static_alpha_data,
            'static_beta_data': self.static_beta_data,
            'static_information_ratio_data': self.static_information_ratio_data,
            'static_treynor_ratio_data': self.static_treynor_ratio_data,
            'static_calmar_ratio_data': self.static_calmar_ratio_data,
            'static_ulcer_index_data': self.static_ulcer_index_data,
            'rolling_alpha_data': self.rolling_alpha_data,
            'rolling_beta_data': self.rolling_beta_data,
            'rolling_information_ratio_data': self.rolling_information_ratio_data,
            'static_hit_ratio_data': self.static_hit_ratio_data,
            'rolling_hit_ratio_data': self.rolling_hit_ratio_data,
            'worst_calendar_data': self.worst_calendar_data,
        }
    
    def process_scheme(self) -> None:
        """Orchestrate all metric calculations for the scheme."""
        if self.scheme_data is None:
            self.logger.error(
                "Cannot process scheme %s — no data available (fetch may have failed)", self.scheme_code
            )
            return

        scheme_name = self.scheme_data.get('scheme_name', self.scheme_code)
        self.logger.info("Starting analysis for '%s'", scheme_name)
        self._run_standalone_metrics()
        self._run_benchmark_metrics(scheme_name)
        self.logger.info("Analysis complete for '%s'", scheme_name)

    def _run_standalone_metrics(self) -> None:
        """Run all metrics that don't require benchmark data."""
        self.rolling_data             = self._run_step("Rolling Returns",           RollingReturnsCalculator.calculate,          self.scheme_data)
        self.calendar_data            = self._run_step("Calendar Year Returns",      CalendarYearReturnsCalculator.calculate,     self.scheme_data, self.years_to_calculate)
        self.static_std_dev_data      = self._run_step("Static Std Deviation",       StaticStandardDeviationCalculator.calculate, self.scheme_data)
        self.static_downside_dev_data = self._run_step("Static Downside Deviation",  StaticDownsideDeviationCalculator.calculate, self.scheme_data)
        self.rolling_std_dev_data     = self._run_step("Rolling Std Deviation",      RollingStandardDeviationCalculator.calculate,self.scheme_data)
        self.static_sharpe_data       = self._run_step("Static Sharpe Ratio",        StaticSharpeRatioCalculator.calculate,       self.scheme_data)
        self.rolling_sharpe_data      = self._run_step("Rolling Sharpe Ratio",       RollingSharpeRatioCalculator.calculate,      self.scheme_data)
        self.static_sortino_data      = self._run_step("Static Sortino Ratio",       StaticSortinoRatioCalculator.calculate,      self.scheme_data)
        self.rolling_sortino_data     = self._run_step("Rolling Sortino Ratio",      RollingSortinoRatioCalculator.calculate,     self.scheme_data)
        self.static_drawdown_data     = self._run_step("Static Drawdown",            StaticDrawdownCalculator.calculate,          self.scheme_data)
        self.rolling_drawdown_data    = self._run_step("Rolling Drawdown",           RollingDrawdownCalculator.calculate,         self.scheme_data)
        self.static_calmar_ratio_data = self._run_step("Static Calmar Ratio",        StaticCalmarRatioCalculator.calculate,       self.scheme_data)
        self.static_ulcer_index_data  = self._run_step("Static Ulcer Index",         StaticUlcerIndexCalculator.calculate,        self.scheme_data)
        self.worst_calendar_data      = self._run_step("Worst Calendar Year",        WorstCalendarYearCalculator.calculate,       self.calendar_data)

    def _run_benchmark_metrics(self, scheme_name: str) -> None:
        """Run all metrics that require benchmark data, if available."""
        if not self.benchmark_data:
            self.logger.warning("Benchmark data unavailable — skipping benchmark-based metrics for '%s'", scheme_name)
            return

        self.logger.info("Benchmark data available — running benchmark-based metrics for '%s'", scheme_name)
        self.static_alpha_data              = self._run_step("Static Alpha",             StaticAlphaCalculator.calculate,             self.scheme_data, self.benchmark_data)
        self.static_beta_data               = self._run_step("Static Beta",              StaticBetaCalculator.calculate,              self.scheme_data, self.benchmark_data)
        self.static_information_ratio_data  = self._run_step("Static Information Ratio", StaticInformationRatioCalculator.calculate,  self.scheme_data, self.benchmark_data)
        self.static_treynor_ratio_data      = self._run_step("Static Treynor Ratio",     StaticTreynorRatioCalculator.calculate,      self.scheme_data, self.benchmark_data)
        self.rolling_alpha_data             = self._run_step("Rolling Alpha",            RollingAlphaCalculator.calculate,            self.scheme_data, self.benchmark_data)
        self.rolling_beta_data              = self._run_step("Rolling Beta",             RollingBetaCalculator.calculate,             self.scheme_data, self.benchmark_data)
        self.rolling_information_ratio_data = self._run_step("Rolling Information Ratio",RollingInformationRatioCalculator.calculate, self.scheme_data, self.benchmark_data)
        self.static_hit_ratio_data          = self._run_step("Static Hit Ratio",         StaticHitRatioCalculator.calculate,          self.scheme_data, self.benchmark_data)
        self.rolling_hit_ratio_data         = self._run_step("Rolling Hit Ratio",        RollingHitRatioCalculator.calculate,         self.scheme_data, self.benchmark_data)

