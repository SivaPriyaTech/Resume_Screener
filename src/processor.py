import os
import time
from pathlib import Path
from datetime import datetime

from src.data_loader import load_data
from src.models import ScreeningResume
from src.prompt_builder import system_prompt, build_prompt
from src.llm_client import call_llm
from src.retry_handler import call_with_retry
from src.data_saver import (
    save_json,
    export_to_excel,
    save_run_logs
) 


run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

print(f'RUN ID: {run_id}')

def processor(config):

    #Starte execution timer

    start_time = time.perf_counter()
    run_date = datetime.now().astimezone().strftime('%Y/%m/%d')

    errors = []
    data = []
    processed = []

    source_path = config['input']['source_path']
    output_dir = Path(config['output']['output_path'])
    application_name = config['application_name']

    output = output_dir / f"{application_name}_{run_id}"
    raw_path = output / f"raw"
    parsed_path = output / f"parsed"
    log_path = output/ f'logs'

    provider = config['llm']['provider']
    model = config['llm']['model']

    max_attempts = config['retry']['max_attempts']
    initial_delay = config['retry']['initial_delay']
    max_delay = config['retry']['max_delay']

    # create output folders
    os.makedirs(output, exist_ok=True)
    os.makedirs(raw_path, exist_ok=True)
    os.makedirs(parsed_path, exist_ok=True)

    # Get/load the resumes
    resume_files = sorted(
        Path(source_path).glob(
            f"*.txt"
        )
    )

    if not resume_files:
        raise FileNotFoundError("No resume files are found")

    # Process Resumes

    for file_path in resume_files:

        cand_id = file_path.stem
        print(f"\n Processing ID: {cand_id} ")
        processed.append(cand_id)

        try:

            # Load resumes

            text = load_data(file_path)

            # Build prompt 
            user_prompt = build_prompt(resume_text=text)

            # Call LLM api
            response = call_with_retry(
                    call_llm,
                    client=config['client'],
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_format=ScreeningResume,
                    model=model,
                    max_attempts= max_attempts,
                    max_delay= max_delay,
                    initial_delay= initial_delay
                )

            # save raw api response
            raw_dump = response.model_dump(mode='json')

            save_json(output_path=raw_path, file_name= cand_id, data= raw_dump)

            # Extract parsed response

            parsed_obj = response.parsed
            parsed_dump = parsed_obj.model_dump(mode='json')
            save_json(output_path=parsed_path, file_name= cand_id, data= parsed_dump)

            parsed_dump['cand_id'] = cand_id

            data.append(parsed_dump)

            print(f"Successfully processed: {cand_id}")

        except Exception as e:
            print(f"ERROR in {cand_id}: {e}")

            errors.append({
                'candidate_id': {cand_id},
                'error': str(e)
            })

        export_error = None
        try:
            print('\n Saving Excel Output')
            
            export_to_excel(
                output_path=output,
                file_name=f"result",
                data = data
            )

            export_to_excel(
                output_path=log_path,
                file_name=f"errors",
                data = errors
            )

        except Exception as e:
            export_error = str(e)
            print(f'Errors while saving the excel files: {e}')

        # calc total exec time
        end_time = time.perf_counter()

        total_minutes =round((end_time - start_time)/60, 2)

        # Prepare run details

        run_details = {
            'run_id' : run_id,
            'date' : run_date,
            'provider': provider,
            'model': model,
            'total': len(processed),
            'successful': len(data),
            'failed': len(errors),
            'execution_time': f"{total_minutes} minutes",
            'status': 'successful' if export_error is None else 'failed'
        } 

        # Save logs

        save_run_logs(output_path=log_path, log_file_name=f"logs.md", run_details=run_details)

        print('\n Pipeline is completed!!')

        print(f'\n Total resume processed {run_details['total']}')

        if export_error:
            raise RuntimeError(
                f"Failed to save excel output: {export_error}"
            )