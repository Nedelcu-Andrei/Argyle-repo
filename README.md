# Playwright/Unit-tests/Validators

## Overview of the project

- To log-in and scan a upwork homepage and profile account data:
  - Level_1 task data saved as "level_1_task.json".
  - Level_2 task data saved as "level_2_task.json"
  - Level_2 task data structured as per model presented on in the task. The object of the data was serialized to a pydantic model.
  - Validators added in pydantic model for some type of data formats that were expected.
  - Missing fields handled as a check that completes them with a string that specifies that the data is missing.
  - Error handling that indicates in which method the error occured and the error message.
  - Retry added in case the scanning fails.
  - Unit-tests for for the parser and integration tests for the scanner.
  - The whole process is split between the a scanning process and a parsing process.
  - Made the docker implementation but since it's running with "headless=False" it will need a server to run.
  
  **Note: From Scrapy was used only the Selector import for parsing the HTML body of the responses. Was used instead of the playwright selectors for better
  error managemant and easier implementations of conditions in the code.
  
## Requirements

- python 3.x.
  - Tested and developed on 3.8.0
- install dependencies in requirements.txt:
  - pip install -r requirements.txt
  - you may need 'sudo' if you are not using virtualenv.


