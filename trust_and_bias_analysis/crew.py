import os

from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

load_dotenv()


@CrewBase
class GroundNewsCrew:
    """GroundNewsCrew: AI crew that analyzes news articles for gender bias and ethical violations."""

    def __init__(self, inputs=None):
        llm_api_key = os.getenv("OPENAI_API_KEY")
        if not llm_api_key:
            raise EnvironmentError("OPENAI_API_KEY not found in environment variables")

        llm_base_url = os.getenv("OPENAI_API_BASE")
        if not llm_base_url:
            raise EnvironmentError("OPENAI_API_BASE not found in environment variables")

        model = os.getenv("OPENAI_MODEL", "gpt-4.1")

        self.llm = LLM(
            model=model,
            temperature=0.2,
            api_key=llm_api_key,
            base_url=llm_base_url,
            stop=None
        )

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.agents_config = os.path.join(current_dir, "config", "agents.yaml")
        self.tasks_config = os.path.join(current_dir, "config", "tasks.yaml")
        self.inputs = inputs or {}

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