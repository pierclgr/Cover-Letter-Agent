from crewai import Agent, Task, Crew, LLM
from crewai_tools import FileReadTool, ScrapeWebsiteTool, TXTSearchTool
import os


class CoverLetterAgent:
    """
    A class used to create a crew of agents for writing cover letters.

    Parameters
    ----------
    file_path : str
        The path to the resume file.
    open_ai_key : str, optional
        The Open AI key to use for the LLM.
    open_ai_model : str, optional
        The Open AI model to use for the LLM.

    Attributes
    ----------
    researcher : Agent
        The agent responsible for extracting job requirements.
    profiler : Agent
        The agent responsible for compiling a personal and professional profile.
    cover_letter_writer : Agent
        The agent responsible for writing the cover letter.
    research_task : Task
        The task for the Researcher agent to extract job requirements.
    profile_task : Task
        The task for the Profiler agent to compile a personal and professional profile.
    cover_letter_writing_task : Task
        The task for the Cover Letter Writer agent to write the cover letter.
    cover_letter_crew : Crew
        The crew of agents.
    """

    def __init__(self, file_path: str, open_ai_key: str = None, open_ai_model: str = None,
                 job_posting_path: str = None):
        """
        Initialize the CoverLetterAgent class.

        Parameters
        ----------
        file_path : str
            The path to the resume file.
        open_ai_key : str, optional
            The Open AI key to use for the LLM.
        open_ai_model : str, optional
            The Open AI model to use for the LLM.
        job_posting_path : str, optional
            The path to the job posting file.
        """
        if open_ai_key:
            llm = None
            os.environ["OPENAI_API_KEY"] = open_ai_key

            # set openai model accordingly to the give one, if any
            if open_ai_model:
                os.environ["OPENAI_MODEL_NAME"] = open_ai_model
            else:
                os.environ["OPENAI_MODEL_NAME"] = 'gpt-4.1-nano'
        else:
            # use local Ollama model if no openai key is provided
            llm = LLM(
                model="ollama/qwen3:latest",
                base_url="http://localhost:11434"
            )

        # create the tool to scrape a website
        self.scrape_tool = ScrapeWebsiteTool()

        # create the tools to read the resume
        self.read_resume = FileReadTool(file_path=file_path)

        # create the semantic search tool with ollama embeddings if no openai key is provided
        if llm:
            self.semantic_search_resume = TXTSearchTool(txt=file_path,
                                                        config=dict(
                                                            embedder=dict(
                                                                provider="ollama",
                                                                config=dict(
                                                                    model="mxbai-embed-large:latest"
                                                                ),
                                                            ),
                                                        ))
        else:
            self.semantic_search_resume = TXTSearchTool(txt=file_path)

        # create the tools to read the job posting
        if job_posting_path:
            self.read_job_posting = FileReadTool(file_path=job_posting_path)

            # create the semantic search tool with ollama embeddings if no openai key is provided
            if llm:
                self.semantic_search_job_posting = TXTSearchTool(txt=job_posting_path,
                                                                 config=dict(
                                                                     embedder=dict(
                                                                         provider="ollama",
                                                                         config=dict(
                                                                             model="mxbai-embed-large:latest"
                                                                         ),
                                                                     ),
                                                                 ))
            else:
                self.semantic_search_job_posting = TXTSearchTool(txt=job_posting_path)
            job_posting_tools = [self.read_job_posting, self.semantic_search_job_posting]
        else:
            job_posting_tools = []

        # create the agents
        # Agent 1: Researcher
        self.researcher = Agent(
            role="Tech Job Analyst",
            goal="Analyze job descriptions to identify key requirements and skills",
            tools=[self.scrape_tool],
            verbose=True,
            backstory=(
                "As a Job Analyst, your expertise in navigating and extracting critical information from job postings "
                "is unmatched. Your skills help pinpoint and highlight the necessary qualifications and skills sought "
                "by employers, forming the foundation for effective application tailoring."
            ),
            llm=llm
        )

        # Agent 2: Profiler
        resume_tools = [self.read_resume, self.semantic_search_resume]
        self.profiler = Agent(
            role="Personal Profiler for Engineers",
            goal="Analyze job applicants' resumes to help them stand out in the job market and write a personal "
                 "profile for the applicant.",
            tools=resume_tools,
            verbose=True,
            backstory=(
                "Equipped with analytical expertise, you dissect and synthesize information from diverse sources, "
                "including resumes to craft comprehensive personal and professional profiles of job applicants laying "
                "the groundwork for personalized cover letter writing."
            ),
            llm=llm
        )

        # create the tasks
        # Task for Researcher Agent: Extract Job Requirements
        if job_posting_tools:
            description = (
                "Analyze the job posting using tools to extract and synthesize key skills, experiences, and "
                "qualifications required. Use the tools to gather content and identify and categorize the requirements."
            )
        else:
            description = (
                "Analyze the job posting URL ({job_posting_url}) to extract and synthesize key skills, experiences, "
                "and qualifications required. Use the tools to gather content and identify and categorize the "
                "requirements."
            )

        # Agent 3: Cover Letter Writer
        self.cover_letter_writer = Agent(
            role="Cover Letter Writer for Engineers",
            goal="Write an outstanding cover letter for a given candidate applying to a given job position.",
            verbose=True,
            backstory=(
                "With a strategic mind and an eye for detail, you excel at writing cover letters to highlight the most "
                "relevant skills and experiences of a candidate, ensuring they resonate perfectly with the job's "
                "requirements."
            ),
            llm=llm
        )

        self.research_task = Task(
            description=description,
            tools=job_posting_tools,
            expected_output=(
                "A comprehensive profile document that includes the job description, mandatory and optional "
                "requirements, skills, qualifications, and experiences."
            ),
            agent=self.researcher,
            async_execution=True
        )

        # Task for Profiler Agent: Compile Personal Profile
        self.profile_task = Task(
            description=(
                "Compile a detailed personal and professional profile using tools to extract and synthesize "
                "information from the applicant resume and also emphasize the candidate's personality and personal "
                "characteristic extracted from the personal writeup ({personal_writeup}) of the candidate."
            ),
            expected_output=(
                "A comprehensive profile document that includes skills, project experiences, contributions, interests, "
                "and communication style about the applicant."
            ),
            agent=self.profiler,
            async_execution=True
        )

        self.cover_letter_writing_task = Task(
            description=(
                "Using the profile description and job requirements obtained from previous tasks, write the cover "
                "letter to highlight the most relevant areas of the applicant. Adjust and enhance the cover letter "
                "content according to the applicants resume. Make sure this is the best cover letter ever but don't "
                "make up any information. Match the characteristics of the applicant with the job requirements and "
                "highlight how the candidate's profile aligns with the job requirements, both on a professional and "
                "personal side."
            ),
            expected_output=(
                "A cover letter document written on the basis to the job requirements and the profile of the applicant "
                "that effectively highlights the candidate's qualifications and experiences that match the job "
                "requirements."
            ),
            context=[self.research_task, self.profile_task],
            agent=self.cover_letter_writer
        )

        # create the crew
        self.cover_letter_crew = Crew(
            agents=[self.researcher,
                    self.profiler,
                    self.cover_letter_writer
                    ],

            tasks=[self.research_task,
                   self.profile_task,
                   self.cover_letter_writing_task
                   ],
            verbose=True
        )

    def kickoff(self, personal_writeup: str, job_posting_url: str = None) -> str:
        """
        Start the crew with the given inputs.

        Parameters
        ----------
        job_posting_url : str
            The URL of the job posting.
        personal_writeup : str
            The personal write-up of the applicant.

        Returns
        -------
        str
            The cover letter.
        """
        if job_posting_url:
            job_application_inputs = {
                'job_posting_url': job_posting_url,
                'personal_writeup': personal_writeup
            }
        else:
            job_application_inputs = {
                'personal_writeup': personal_writeup
            }

        result = self.cover_letter_crew.kickoff(inputs=job_application_inputs)

        return str(result)
