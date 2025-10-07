# Cold Email Generator

A Streamlit application that generates personalized cold emails based on job descriptions and relevant portfolio links. The application uses LangChain with Groq's LLM for natural language processing and ChromaDB for efficient portfolio matching.

## Architecture

<img width="2161" height="1562" alt="Image" src="https://github.com/user-attachments/assets/e248adbe-6d29-4d9c-bf48-d0a8e2cd616d" />
## Screenshots

### Main Interface
<img width="1831" height="908" alt="Image" src="https://github.com/user-attachments/assets/b706d31a-0d97-4aa2-a463-13f90f532f91" />

### Example Output
<img width="1838" height="902" alt="Image" src="https://github.com/user-attachments/assets/a57be3dc-7b85-4be4-b548-6dae0a01eb75" />



## Features

- 🔍 **Job Description Extraction**: Automatically extracts key information from job postings
- 💼 **Portfolio Matching**: Matches job requirements with relevant portfolio examples
- ✉️ **Email Generation**: Creates personalized cold emails using AI
- 🎯 **Skill-Based Matching**: Uses vector database to find the most relevant portfolio examples
- 🚀 **Real-time Processing**: Processes job descriptions and generates emails in real-time

## Prerequisites

- Python 3.11+
- Groq API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Bou-Mery/Cold-email-Gen-project.git
cd Cold-email-Gen-project
```

2. Create and activate a virtual environment:
```bash
python -m venv ai-env
# On Windows
.\ai-env\Scripts\activate
# On Unix or MacOS
source ai-env/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

## Project Structure

```
Cold-email-Gen-project/
├── app/
│   ├── chains.py         # LangChain implementations
│   ├── main.py          # Main Streamlit application
│   ├── portfolio.py     # Portfolio management and matching
│   ├── utils.py         # Utility functions
│   └── rsrc/
│       └── links_portfolio.csv  # Portfolio data
├── vector_db/          # ChromaDB storage
├── requirements.txt    # Project dependencies
└── .env               # Environment variables
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app/main.py
```

2. Enter a job posting URL in the input field

3. Click "Generate Email" to generate a personalized cold email

The application will:
- Extract relevant information from the job posting
- Match the requirements with portfolio examples
- Generate a personalized cold email

## Technical Details

- **LangChain + Groq**: Used for natural language processing and text generation
- **ChromaDB**: Vector database for efficient portfolio matching
- **Streamlit**: Web interface framework
- **Beautiful Soup**: Web scraping for job descriptions

## Contributing

Feel free to open issues and pull requests for any improvements.

## Author

**BOUKHRAIS Meryem**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
