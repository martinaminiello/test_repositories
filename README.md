# one_week_test
Installation and Setup Guide
Verify that the virtual environment is activated:
Make sure the virtual environment is activated before proceeding with the installation of dependencies.

On Windows:

bash
Copy
Edit
.\venv\Scripts\activate
On macOS/Linux:

bash
Copy
Edit
source venv/bin/activate
Check the Python interpreter:
Ensure that the selected Python interpreter is the one from the virtual environment (venv). You can verify this in your IDE settings or by using the command:

bash
Copy
Edit
which python
It should point to the venv folder.

Install dependencies:
Once the virtual environment is activated, install all required dependencies by running:

bash
Copy
Edit

Create .env file with your Github token:
bash
Copy
Edit
GITHUB_TOKEN=your_token

pip install -r requirements.txt
