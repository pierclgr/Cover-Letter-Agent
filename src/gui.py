import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
import os
import json
from pathlib import Path
from typing import Optional, Tuple
from src.utils import pdf_to_txt, str_to_txt
from src.agent import CoverLetterAgent


class CoverLetterGenerator:
    """
    A GUI application for generating personalized cover letters based on a resume,
    job posting URL or description, and personal description.

    The application allows users to select a PDF resume, enter a job posting URL OR
    paste a job description, provide a personal description, and optionally provide
    OpenAI API credentials to generate a tailored cover letter.

    Attributes
    ----------
    root : tk.Tk
        The root Tkinter window
    data_dir : Path
        Directory for storing application data
    saved_description_path : Path
        Path to the saved personal description file
    resume_path : tk.StringVar
        Path to the selected resume PDF file
    job_url : tk.StringVar
        URL of the job posting
    save_description : tk.BooleanVar
        Flag to save the personal description for future use
    openai_key : tk.StringVar
        OpenAI API key (optional)
    openai_model : tk.StringVar
        OpenAI model to use (optional)
    description_text : scrolledtext.ScrolledText
        Text widget for personal description input
    job_description_text : scrolledtext.ScrolledText
        Text widget for job description input
    output_text : scrolledtext.ScrolledText
        Text widget for displaying the generated cover letter
    """

    def __init__(self, root: tk.Tk) -> None:
        """
        Initialize the Cover Letter Generator application.

        Parameters
        ----------
        root : tk.Tk
            The root Tkinter window

        Returns
        -------
        None
        """
        self.root = root
        self.root.title("Cover Letter Generator")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # Set application icon if available
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        # Create data directory if it doesn't exist
        self.data_dir = Path(__file__).parent.parent / "app_data"
        self.data_dir.mkdir(exist_ok=True)
        self.saved_description_path = self.data_dir / "saved_description.txt"

        # Variables
        self.resume_path = tk.StringVar()
        self.job_url = tk.StringVar()
        self.save_description = tk.BooleanVar(value=False)
        self.openai_key = tk.StringVar()
        self.openai_model = tk.StringVar(value="gpt-4.1-nano")

        # Create the main frame with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Resume file selection
        ttk.Label(main_frame, text="Resume File (PDF)*:").grid(row=0, column=0, sticky=tk.W, pady=5)
        resume_frame = ttk.Frame(main_frame)
        resume_frame.grid(row=0, column=1, sticky=tk.W + tk.E, pady=5)
        ttk.Entry(resume_frame, textvariable=self.resume_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(resume_frame, text="Browse", command=self.browse_resume).pack(side=tk.RIGHT, padx=5)

        # Job URL (now optional)
        ttk.Label(main_frame, text="Job Posting URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.job_url, width=50).grid(row=1, column=1, sticky=tk.W + tk.E, pady=5)

        # Job description text area (alternative to URL)
        ttk.Label(main_frame, text="OR Job Description:").grid(row=2, column=0, sticky=tk.W + tk.N, pady=5)
        job_description_frame = ttk.Frame(main_frame)
        job_description_frame.grid(row=2, column=1, sticky=tk.W + tk.E, pady=5)

        self.job_description_text = scrolledtext.ScrolledText(job_description_frame, width=50, height=5, wrap=tk.WORD)
        self.job_description_text.pack(fill=tk.BOTH, expand=True)

        job_description_help = ttk.Label(job_description_frame,
                                         text="Paste the job description text here if you don't have a URL",
                                         foreground="gray", font=("", 8))
        job_description_help.pack(anchor=tk.W, pady=1)

        job_input_note = ttk.Label(job_description_frame,
                                   text="Note: Either Job URL OR Job Description must be provided",
                                   foreground="blue", font=("", 8))
        job_input_note.pack(anchor=tk.W, pady=1)

        # Personal description
        ttk.Label(main_frame, text="Personal Description*:").grid(row=3, column=0, sticky=tk.W + tk.N, pady=5)
        description_frame = ttk.Frame(main_frame)
        description_frame.grid(row=3, column=1, sticky=tk.W + tk.E, pady=5)

        self.description_text = scrolledtext.ScrolledText(description_frame, width=50, height=5, wrap=tk.WORD)
        self.description_text.pack(fill=tk.BOTH, expand=True)

        description_help = ttk.Label(description_frame,
                                     text="Describe your career goals, motivations, and relevant background (required)",
                                     foreground="gray", font=("", 8))
        description_help.pack(anchor=tk.W, pady=1)

        required_fields_note = ttk.Label(description_frame,
                                         text="* Fields marked with asterisk are mandatory",
                                         foreground="red", font=("", 8))
        required_fields_note.pack(anchor=tk.W, pady=1)

        # Save description checkbox
        save_check = ttk.Checkbutton(description_frame, text="Save description for future use",
                                     variable=self.save_description)
        save_check.pack(anchor=tk.W, pady=2)

        # OpenAI settings
        openai_frame = ttk.LabelFrame(main_frame, text="OpenAI Settings (Optional)")
        openai_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W + tk.E, pady=10)

        ttk.Label(openai_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(openai_frame, textvariable=self.openai_key, width=40, show="*").grid(row=0, column=1,
                                                                                       sticky=tk.W + tk.E, padx=5,
                                                                                       pady=5)

        ttk.Label(openai_frame, text="Model:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        model_combo = ttk.Combobox(openai_frame, textvariable=self.openai_model, width=30)
        model_combo['values'] = ('gpt-4.1-nano', 'gpt-4-turbo', 'gpt-3.5-turbo')
        model_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        api_help = ttk.Label(openai_frame,
                             text="These fields are optional. If not provided, the application will use default settings.",
                             foreground="gray", font=("", 8))
        api_help.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=0)

        # Generate button
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        generate_button = ttk.Button(button_frame, text="Write Cover Letter",
                                     command=self.generate_cover_letter, width=20)
        generate_button.pack(side=tk.LEFT, padx=5)

        clear_button = ttk.Button(button_frame, text="Clear All",
                                  command=self.clear_form, width=10)
        clear_button.pack(side=tk.LEFT, padx=5)

        # Output text area
        out_label_frame = ttk.Frame(main_frame)
        out_label_frame.grid(row=6, column=0, columnspan=2, sticky=tk.W + tk.E, pady=5)

        ttk.Label(out_label_frame, text="Generated Cover Letter:").pack(side=tk.LEFT)
        ttk.Button(out_label_frame, text="Copy", command=self.copy_to_clipboard, width=8).pack(side=tk.RIGHT)

        self.output_text = scrolledtext.ScrolledText(main_frame, width=80, height=20, wrap=tk.WORD)
        self.output_text.grid(row=7, column=0, columnspan=2, sticky=tk.W + tk.E + tk.N + tk.S, pady=5)
        self.output_text.config(state=tk.DISABLED)

        # Configure the grid to resize properly
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)

        # Status bar
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("Ready")

        # Load saved settings
        self.load_saved_description()

        # Set up protocol for window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def browse_resume(self) -> None:
        """
        Open a file dialog to select a resume PDF file.

        Opens a file dialog restricted to PDF files and updates the resume_path
        variable with the selected file path.

        Returns
        -------
        None
        """
        filetypes = [("PDF files", "*.pdf")]
        filename = filedialog.askopenfilename(filetypes=filetypes, title="Select Resume PDF")
        if filename:
            self.resume_path.set(filename)
            self.status_var.set(f"Resume selected: {os.path.basename(filename)}")

    def load_saved_description(self) -> None:
        """
        Load saved personal description if available.

        Reads the saved personal description from disk and populates the description
        text area if the file exists.

        Returns
        -------
        None
        """
        try:
            if self.saved_description_path.exists():
                with open(self.saved_description_path, 'r', encoding='utf-8') as f:
                    saved_text = f.read()
                    self.description_text.delete('1.0', tk.END)
                    self.description_text.insert(tk.END, saved_text)
                    self.save_description.set(True)
        except Exception as e:
            self.status_var.set(f"Error loading saved description")
            print(f"Error loading saved description: {e}")

    def save_description_to_file(self) -> None:
        """
        Save personal description to file if checkbox is checked.

        If the save description checkbox is selected, writes the current content of
        the description text area to disk for future use.

        Returns
        -------
        None
        """
        if self.save_description.get():
            try:
                with open(self.saved_description_path, 'w', encoding='utf-8') as f:
                    f.write(self.description_text.get("1.0", tk.END))
            except Exception as e:
                self.status_var.set("Error saving description")
                print(f"Error saving description: {e}")

    def validate_inputs(self) -> Tuple[bool, str]:
        """
        Validate all user inputs before processing.

        Checks that all required fields are filled and valid.
        Either job URL or job description must be provided.
        OpenAI API key and model are optional and not validated.

        Returns
        -------
        tuple
            A tuple containing (is_valid, error_message)
        """
        # Check resume file (mandatory)
        if not self.resume_path.get().strip():
            return False, "Please select a resume file (mandatory field)"

        if not os.path.exists(self.resume_path.get()):
            return False, "Resume file does not exist"

        if not self.resume_path.get().lower().endswith('.pdf'):
            return False, "Resume file must be in PDF format"

        # Check if either job URL or job description is provided
        job_url = self.job_url.get().strip()
        job_description = self.job_description_text.get("1.0", tk.END).strip()

        if not job_url and not job_description:
            return False, "Please provide either a job posting URL or paste a job description"

        # If job URL is provided, validate it
        if job_url:
            if not (job_url.startswith('http://') or job_url.startswith('https://')):
                return False, "Job URL must start with http:// or https://"

        # Check personal description (mandatory)
        personal_description = self.description_text.get("1.0", tk.END).strip()
        if not personal_description:
            return False, "Please enter a personal description (mandatory field)"

        if len(personal_description) < 20:
            return False, "Personal description is too short (minimum 20 characters)"

        # Note: OpenAI API key and model are optional and not validated

        return True, ""

    def generate_cover_letter(self) -> None:
        """
        Generate a cover letter based on user inputs.

        Validates all inputs, then processes the resume, job URL or job description,
        and personal description to generate a cover letter using either the provided
        OpenAI credentials or default settings.

        Returns
        -------
        None
        """
        # Validate inputs
        valid, error_msg = self.validate_inputs()
        if not valid:
            self.show_error(error_msg)
            return

        # Update status
        self.status_var.set("Generating cover letter...")
        self.root.update_idletasks()

        # Save the description if requested
        self.save_description_to_file()

        # Get inputs
        resume_path = self.resume_path.get()
        job_url = self.job_url.get().strip()
        job_description = self.job_description_text.get("1.0", tk.END).strip()
        personal_description = self.description_text.get("1.0", tk.END).strip()
        api_key = self.openai_key.get().strip()
        model = self.openai_model.get().strip()

        try:
            cover_letter = self.process_cover_letter_request(
                resume_path=resume_path,
                job_url=job_url,
                job_description=job_description,
                personal_description=personal_description,
                api_key=api_key,
                model=model
            )

            # Display the result
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, cover_letter)
            self.output_text.config(state=tk.DISABLED)

            self.status_var.set("Cover letter generated successfully")
        except Exception as e:
            self.show_error(f"Error generating cover letter: {str(e)}")
            self.status_var.set("Error generating cover letter")

    def process_cover_letter_request(self, resume_path: str, job_url: str,
                                     job_description: str, personal_description: str,
                                     api_key: Optional[str], model: Optional[str]) -> str:
        """
        Process the cover letter request by executing the cover letter agent.

        Parameters
        ----------
        resume_path : str
            Path to the resume PDF file.
        job_url : str
            URL of the job posting.
        job_description : str
            Pasted job description text.
        personal_description : str
            Personal description of the job seeker.
        api_key : Optional[str]
            OpenAI API key.
        model : Optional[str]
            OpenAI model name.

        Returns
        -------
        cover_letter : str
            The generated cover letter.
        """

        # convert the pdf to txt
        resume_path = pdf_to_txt(resume_path)

        if job_url:
            job_posting_path = None
        else:
            job_posting_path = str_to_txt(job_description, file_name="job_description")

        # create the agent
        cover_letter_agent = CoverLetterAgent(
            file_path=resume_path,
            open_ai_key=api_key,
            open_ai_model=model,
            job_posting_path=job_posting_path
        )

        # generate the cover letter
        if job_url:
            cover_letter = cover_letter_agent.kickoff(job_posting_url=job_url, personal_writeup=personal_description)
        else:
            # If job_description is provided instead of URL
            cover_letter = cover_letter_agent.kickoff(personal_writeup=personal_description)

        return cover_letter

    def clear_form(self) -> None:
        """
        Clear all form fields.

        Resets all input fields to their default state.

        Returns
        -------
        None
        """
        self.resume_path.set("")
        self.job_url.set("")
        self.job_description_text.delete("1.0", tk.END)
        self.description_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.status_var.set("Form cleared")

    def copy_to_clipboard(self) -> None:
        """
        Copy the generated cover letter to clipboard.

        Copies the current content of the output text area to the system clipboard.

        Returns
        -------
        None
        """
        content = self.output_text.get("1.0", tk.END)
        if content.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.status_var.set("Cover letter copied to clipboard")
        else:
            self.status_var.set("Nothing to copy")

    def show_error(self, message: str) -> None:
        """
        Display an error message to the user.

        Shows a modal error dialog with the provided message.

        Parameters
        ----------
        message : str
            The error message to display

        Returns
        -------
        None
        """
        messagebox.showerror("Error", message, parent=self.root)

    def on_closing(self) -> None:
        """
        Handle the window closing event.

        Saves settings and descriptions before closing the application.


        Returns
        -------
        None
        """
        # Save description if needed
        if self.save_description.get():
            self.save_description_to_file()
        self.root.destroy()


def main_gui() -> None:
    """
    Main entry point for the application.

    Creates the Tkinter root window and initializes the application.

    Returns
    -------
    None
    """
    # Set up the root window
    root = tk.Tk()

    # Apply a theme if available
    try:
        style = ttk.Style()
        if os.name == 'nt':  # Windows
            style.theme_use('vista')
        elif os.name == 'posix':  # macOS, Linux
            style.theme_use('clam')
    except:
        pass

    # Initialize the application
    app = CoverLetterGenerator(root)

    # Start the main event loop
    root.mainloop()
