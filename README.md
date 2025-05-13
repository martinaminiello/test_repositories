# one_week_test
Installation and Setup Guide
Verify that the virtual environment is activated:
Make sure the virtual environment is activated before proceeding with the installation of dependencies.

On Windows:
`.\venv\Scripts\activate`

On macOS/Linux:
`source venv/bin/activate`

Check the Python interpreter:
Ensure that the selected Python interpreter is the one from the virtual environment (venv). You can verify this in your IDE settings or by using the command:
`which python`
It should point to the venv folder.

Install dependencies:
Once the virtual environment is activated, install all required dependencies by running:
`pip install -r requirements.txt`

Create .env file with your Github token:
`GITHUB_TOKEN=your_token`


