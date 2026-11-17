system_prompt="""You are an expert extraction assitant.
Your task is to extract the relevant data from the resume text as per the given schema.
Do not invent any information. All your answerws should be grounded from the given text only.
If any information is missing then mention Not Available"""


def build_prompt(resume_text):
    return f"Resume Text:\n {resume_text}"
