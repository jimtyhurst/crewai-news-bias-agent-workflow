#!/usr/bin/env python
import argparse
import warnings
from dotenv import load_dotenv
from trust_and_bias_analysis.crew import GroundNewsCrew

load_dotenv()

warnings.filterwarnings('ignore', category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the GroundNews Crew with command line arguments for article id.
    """
    parser = argparse.ArgumentParser(description='Run Ground News Crew Analysis')
    parser.add_argument(
        '--input_article',
        type=str,
        help='Input article for the analysis'
    )

    args = parser.parse_args()

    inputs = {
        "input_article": args.input_article
    }

    try:
        print(f"Starting data analysis for Ground News with article= {args.input_article}")
        crew_result = GroundNewsCrew(inputs=inputs).crew().kickoff()
        print("Text Analysis completed successfully")
        print("\n\n########################")
        print("## Analysis Report")
        print("########################\n")
        print(f"Final Results: {crew_result}")
        return crew_result
    except Exception as e:
        print(f"An error occurred while running the crew: {e}")
        raise

if __name__ == "__main__":
    print("## Welcome to Ground News Crew")
    print('-------------------------------------')
    run()