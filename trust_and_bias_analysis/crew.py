import os

import yaml
from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

load_dotenv()


@CrewBase
class GroundNewsCrew:
    """GroundNewsCrew: AI crew that analyzes news articles for gender bias and ethical violations."""

    def __init__(self, inputs=None):
        self.inputs = inputs or {}

        llm_api_key = os.getenv("OPENAI_API_KEY")
        if not llm_api_key:
            raise EnvironmentError("OPENAI_API_KEY not found in environment variables")

        llm_base_url = os.getenv("OPENAI_API_BASE")
        if not llm_base_url:
            raise EnvironmentError("OPENAI_API_BASE not found in environment variables")

        model = os.getenv("OPENAI_MODEL", "o3")

        self.llm = LLM(
            model=model,
            temperature=0.2,
            api_key=llm_api_key,
            base_url=llm_base_url,
        )

        # Define agent configs directly from YAML content
        self.agents_config = {
            "gender_bias_evaluator": {
                "role": "Media Critic specializing in Gender Bias Analysis",
                "goal": "Evaluate articles for gender bias and return a detailed score and explanation grounded in journalistic principles and gender representation research.",
                "backstory": "You are a seasoned journalist and media critic with two decades of experience analyzing gender representation in the media. You've contributed to diversity reviews for leading newsrooms and academic journals. You look for bias in language, sourcing, character portrayal, and visual descriptions. You believe subtle language choices can strongly influence perception, and your job is to surface those patterns clearly."
            },
            "journalism_bias_expert": {
                "role": "Journalism and Media Studies Expert specializing in bias and ethical standards",
                "goal": "Deliver precise and well-supported analyses of news articles, identifying subtle bias and violations of core journalism ethics, referencing reputable ethical frameworks.",
                "backstory": "You are a former investigative journalist turned media ethics professor. You've contributed to academic studies on bias in digital journalism and have advised outlets on editorial standards. You emphasize fairness, transparency, and clarity, and apply frameworks like the SPJ Code of Ethics or BBC Editorial Guidelines."
            }
        }

        # Define task configs directly from YAML content
        self.tasks_config = {
            "evaluate_gender_bias_task": {
                "description": """You are given the full text of a news article to analyze for gender bias:

        "{article}"

        Your goal is to evaluate the article for signs of **gender bias**. Look for:
          - Reinforcement of gender stereotypes
          - Gender-specific descriptions of individuals or professions
          - Emphasis on emotional display or appearance for women
          - One-sided gender representation in sources or viewpoints

        Based on your evaluation, return a JSON object using the following structure:

        ```json
        {{
          "category": "gender_bias",
          "gender_bias_score": <number between 0 (no bias) and 100 (strong bias)>,
          "gender_bias_explanation": "<Brief explanation of why this score was given, citing key observations>"
        }}
        ```""",
                "expected_output": "A JSON object with category, bias score (0–100), and explanation string"
            },
            "review_ethics_task": {
                "description": """Review the following news article for potential ethical violations or risks:

        "{article}"

        Refer to well-known journalism frameworks such as:
          - SPJ Code of Ethics
          - Reuters Trust Principles
          - BBC Editorial Guidelines

        Focus on four key principles:
          - Accuracy
          - Fairness
          - Independence
          - Transparency

        For each violation or risk you identify, specify:
          - The principle involved
          - A short quote or summary that illustrates the issue
          - A reference to the specific guideline or principle that is being violated or stretched

        Return the output in the following format:

        ```json
        {{
          "ethical_review": {{
            "violations": [
              {{
                "principle": "Fairness",
                "description": "The article relies exclusively on law enforcement sources without alternative viewpoints.",
                "reference": "SPJ Code of Ethics – Provide context and avoid stereotyping."
              }}
            ]
          }}
        }}
        ```""",
                "expected_output": "JSON object listing any violations of journalism ethics."
            }
        }

    @agent
    def gender_bias_evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config["gender_bias_evaluator"],
            tools=[],
            verbose=True,
            llm=self.llm
        )

    @agent
    def journalism_bias_expert(self) -> Agent:
        return Agent(
            config=self.agents_config["journalism_bias_expert"],
            tools=[],
            verbose=True,
            llm=self.llm
        )

    @task
    def evaluate_gender_bias_task(self) -> Task:
        config = self.tasks_config["evaluate_gender_bias_task"].copy()

        if "description" in config:
            config["description"] = config["description"].format(**self.inputs)

        return Task(
            config=config,
            agent=self.gender_bias_evaluator()
        )

    @task
    def review_ethics_task(self) -> Task:
        config = self.tasks_config["review_ethics_task"].copy()

        if "description" in config:
            config["description"] = config["description"].format(**self.inputs)

        return Task(
            config=config,
            agent=self.journalism_bias_expert()
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.gender_bias_evaluator(),
                self.journalism_bias_expert()
            ],
            tasks=[
                self.evaluate_gender_bias_task(),
                self.review_ethics_task()
            ],
            _inputs=self.inputs,
            process=Process.sequential,
            chat_llm=self.llm,
            verbose=True,
        )