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


abhi dekh apna stock analzer barobar ban gya h thoda refine krna h backend pe output metrics aarhe h mast wle 
Stock ka data direct y finance se aa rha h usko autoate krna h ki har 5 min e naya data dd ho krke aur historical data bhi badhana h like 5 yrs tak ka data chahiye urne change h api sab barobar chl rhe h 

Pehle yeh backend run kr fir http://127.0.0.1:8000/docs yeh endpoint pe tu analyze aur market context sab le sakta h waha se 
ai analysis me ek baar dekhna h ki jo stock analyser se pura json aarha h vo pura le rha h ki nai consideration me ai based analysis ke liye
Vo tu abhi raat ko baith rha h toh kr warna mai kal krta hu 


