#!/opt/homebrew/bin/python3
# -*- coding: utf-8 -*-

import sys
import logging
from log.logger_config import configure_logging
from mfa import MutualFundAnalyzer

configure_logging()
logger = logging.getLogger(__name__)


def main() -> None:
    """
    CLI entry point for the Mutual Fund Analyzer.

    Runs analysis for one or more scheme codes and logs results.
    For full chart-based analysis, use the Streamlit UI instead: streamlit run app.py

    Usage:
        python main.py <scheme_codes>
        Example: python main.py 101206
        Example: python main.py 101206,112277
    """
    if len(sys.argv) < 2:
        logger.error(
            "No scheme codes provided. Usage: python main.py <scheme_codes>  "
            "(e.g. python main.py 101206,101207)"
        )
        return

    scheme_codes = [code.strip() for code in sys.argv[1].split(",")]
    logger.info("Starting analysis for %d scheme(s): %s", len(scheme_codes), ", ".join(scheme_codes))

    for scheme_code in scheme_codes:
        mf_analyzer = MutualFundAnalyzer(scheme_code)
        mf_analyzer.process_scheme()

    logger.info("Analysis complete for all %d scheme(s)", len(scheme_codes))


if __name__ == "__main__":
    main()
