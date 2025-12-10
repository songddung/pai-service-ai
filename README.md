# pai-service-ai

cd src
py -3.10 -m venv testv

.\testv\Scripts\activate
cd ..

 pip install -r requirements.txt

 uvicorn src.main:app --reload --host 0.0.0.0 --port 8080