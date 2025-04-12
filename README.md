# Analytics Dashboard

A simple dashboard for document processing and stock analysis with a Dockerized Redis backend.

## Prerequisites
- [Python 3.11+](https://www.python.org/downloads/)
- [Node.js and npm](https://nodejs.org/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

## Setup and Initialization

### 1. Clone or Download the Project
```powershell
git clone https://github.com/HEET0520/Analytics-Dash.git
```
2. Set Up Environment Variables
Create a .env file :
```powershell
HF_TOKEN=your_huggingface_token_here
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here
NEWSAPI_KEY=your_newsapi_key_here
```

3. Install Dependencies
Backend (Python)
```powershell
cd backend
pip install -r requirements.txt
```
Frontend
```powershell
cd frontend
npm install
```

4. Start Docker Services
```powershell
docker-compose up --build -d
```

5. Run the Application
   Backend
```powershell
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```
  Frontend
```powershell
cd frontend
npm start
```


