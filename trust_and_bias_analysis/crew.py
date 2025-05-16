import os

from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

load_dotenv()

@CrewBase
class GroundNewsCrew:
    """GroundNewsCrew crew"""
    def __init__(self, inputs=None):
        kbc_api_token = os.getenv("KBC_API_TOKEN")
        if not kbc_api_token:
            raise EnvironmentError("KBC_API_TOKEN not found in the environment variables")

        kbc_api_url = os.getenv("KBC_API_URL")
        if not kbc_api_url:
            raise EnvironmentError("KBC_API_URL not found in the environment variables")

        llm_api_key = os.getenv("OPENAI_API_KEY")
        if not llm_api_key:
            raise EnvironmentError("OPENAI_API_KEY not found in the environment variables")

        llm_base_url = os.getenv("OPENAI_API_BASE")
        if not llm_base_url:
            raise EnvironmentError("OPENAI_API_BASE not found in the environment variables")

        model = os.getenv("OPENAI_MODEL", "o3")

        self.kbc_api_token = kbc_api_token
        self.kbc_api_url = kbc_api_url

        self.llm = LLM(
            model=model,
            temperature=0.2,
            api_key=llm_api_key,
            base_url=llm_base_url,
        )

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.agents_config = os.path.join(current_dir, "config", "agents.yaml")
        self.tasks_config = os.path.join(current_dir, "config", "tasks.yaml")
        self.inputs = inputs or {}

    @agent
    def agent_example_one(self) -> Agent:
        """An agent example one"""

        # We can't preload some data, etc.
        return Agent(
            config=self.agents_config["agent_example_one"],
            tools=[],
            verbose=True,
            llm=self.llm
        )

    @agent
    def agent_example_two(self) -> Agent:
        """An agent example two"""

        # We can't preload some data, etc.
        return Agent(
            config=self.agents_config["agent_example_two"],
            tools=[],
            verbose=True,
            llm=self.llm
        )

    @task
    def example_download_task(self) -> Task:
        """Task to download example"""
        task_config = self.tasks_config["example_download_task"].copy()

        if "description" in task_config and self.inputs:
            task_config["description"] = task_config["description"].format(
                **self.inputs
            )

        return Task(
            config=task_config,
            agent=self.agent_example_one()
        )

    @task
    def detect_text_bias_task(self) -> Task:
        """Task to calculate billed credits from the downloaded data"""
        task_config = self.tasks_config["detect_text_bias_task"].copy()

        return Task(
            config=task_config,
            agent=self.agent_example_two()
        )


    @crew
    def crew(self) -> Crew:
        """Creates the KeboolaInsightsCrew crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            _inputs=self.inputs,
            process=Process.sequential,
            chat_llm=self.llm,
            verbose=True,
        )