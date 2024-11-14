# PartSelect Chat Agent

## Project Overview
The PartSelect Chat Agent is an intelligent conversational assistant designed to enhance the user experience on the PartSelect e-commerce website. The primary focus of the chat agent is to provide customers with accurate and helpful information related to Refrigerator and Dishwasher parts, assisting them in their purchasing decisions and troubleshooting needs.

## Key Features
- Natural language understanding and processing capabilities
- Seamless integration with the PartSelect product catalog
- Ability to provide detailed product information, including specifications, compatibility, and pricing
- Guided troubleshooting and installation instructions for specific parts

## Technologies Used
- Frontend: React
- Backend: Django
- Database: PostgreSQL with pgvector extension
- Natural Language Processing: OpenAI GPT-4o-mini

## Getting Started
To set up and run the PartSelect Chat Agent locally, follow these steps:

### Clone the repository:
```bash
git clone https://github.com/gchoi5738/PartsAgent.git
cd partselect_chat
```

Create a virtual environment:
```bash
python3 -m venv env
source env/bin/activate
```
Install the backend dependencies:
```bash
pip install -r requirements.txt
```
Set up the database:

Install PostgreSQL and create a new database named partselect.
Install the pgvector extension in the partselect database.


Configure the environment variables:

Create a .env file in the backend directory with the following contents:
```bash
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
DB_NAME=partselect
DB_USER=yourusername
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
OPENAI_API_KEY=your-openai-api-key
```
Replace your-secret-key-here, yourusername, yourpassword, and your-openai-api-key with your actual values.


Run the database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```



Set up the frontend:

Navigate to the frontend directory:
```bash
cd frontend
```
Install the frontend dependencies:
```bash
npm install
```


Start the development servers:

In the backend directory, run:
```bash
python manage.py runserver
```
In the frontend directory, run:
```bash
npm start
```


Open your browser and visit http://localhost:5173 to access the PartSelect Chat Agent.



## Contributing
We welcome contributions from the open-source community to enhance the functionality and usability of the PartSelect Chat Agent. If you'd like to contribute, please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to get involved.

## License
This project is licensed under the [MIT License](LICENSE).

## Contact
For any questions, suggestions, or feedback, please reach out to the project maintainers at [support@partselect.com](mailto:support@partselect.com).