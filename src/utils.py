import os
from PyPDF2 import PdfReader
import numpy as np


def pdf_to_txt(pdf_path: str) -> str:
    """
    This function takes a path to a PDF file and generates a text file with the same filename but with .txt extension
    in the app_data folder.

    The text in the PDF is extracted using the PyPDF2 library.

    Parameters
    ----------
    pdf_path : str
        Path to the PDF file.

    Returns
    -------
    str
        Path to the generated text file
    """

    # create the app_data folder in the root of the project if it doesn't exist
    data_folder = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'app_data'
    )
    os.makedirs(data_folder, exist_ok=True)

    # create the text file with the same name as the PDF but with .txt extension
    file_path = os.path.join(data_folder, 'resume.txt')

    # convert PDF to TXT and save it to disk
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    extracted_text = page.extract_text()
    np.savetxt(file_path, [extracted_text], fmt='%s')

    return file_path


def str_to_txt(text: str, file_name: str) -> str:
    """
    This function takes a string and generates a text file with the name 'job_posting.txt'
    in the app_data folder.

    Parameters
    ----------
    text : str
        The input string to be saved to a text file.
    file_name: str
        The name of the file to be saved.

    Returns
    -------
    str
        Path to the generated text file.
    """

    # create the app_data folder in the root of the project if it doesn't exist
    data_folder = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'app_data'
    )
    os.makedirs(data_folder, exist_ok=True)

    # create the text file with the same name as the PDF but with .txt extension
    file_path = os.path.join(data_folder, f'{file_name}.txt')

    # save the text to disk
    np.savetxt(file_path, [text], fmt='%s')

    return file_path
