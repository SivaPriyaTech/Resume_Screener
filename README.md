# Resume Extraction Module

A Python pipeline that extracts structured candidate information from plain-text resumes using the OpenAI API. It processes all `.txt` resume files from a configured input directory and creates JSON, Excel, and run-log outputs.

## Features

- Processes multiple text resumes in one run
- Uses structured Pydantic response schemas
- Supports configurable OpenAI model and retry settings
- Saves raw and parsed LLM responses as JSON
- Exports candidate results and errors to Excel
- Generates a Markdown run log

## Project Structure

```text
resume_extraction_module/
├── config/
│   └── config.yaml
├── data/
│   ├── resumes/
│   └── new_resumes/
├── src/
│   ├── config_loader.py
│   ├── data_loader.py
│   ├── data_saver.py
│   ├── llm_client.py
│   ├── models.py
│   ├── processor.py
│   ├── prompt_builder.py
│   └── retry_handler.py
├── main.py
└── requirements.txt
```

## Requirements

- Python 3.10 or newer
- An OpenAI API key

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Set the API key environment variable named in `config/config.yaml`:

```powershell
$env:OPEN_API_KEY = "your-api-key"
```

For a persistent user-level setting:

```powershell
[Environment]::SetEnvironmentVariable("OPEN_API_KEY", "your-api-key", "User")
```

## Configuration

Update `config/config.yaml` to configure the application:

```yaml
application_name: resume_screener
input:
  source_path: data/new_resumes
output:
  output_path: test_response
llm:
  api_key: OPEN_API_KEY
  provider: openai
  model: gpt-4o-mini
retry:
  max_attempts: 3
  initial_delay: 2
  max_delay: 30
```

The `llm.api_key` value is the name of the environment variable, not the API key itself.

## Usage

Place resume text files in `data/new_resumes` and run:

```powershell
python main.py
```

Only UTF-8 encoded `.txt` files are accepted.

## Output

Each run creates a timestamped directory under `test_response`:

```text
test_response/
└── resume_screener_<YYYYMMDD_HHMMSS>/
    ├── result.xlsx
    ├── raw/
    │   └── <candidate-id>.json
    ├── parsed/
    │   └── <candidate-id>.json
    └── logs/
        ├── errors.xlsx
        └── logs.md
```

- `raw/` contains the complete LLM response data
- `parsed/` contains the structured candidate fields
- `result.xlsx` contains successful extraction results
- `errors.xlsx` contains processing errors
- `logs/logs.md` contains run details and totals
