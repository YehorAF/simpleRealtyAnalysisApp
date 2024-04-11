from fastapi import FastAPI
import uvicorn
import spacy

import dotenv
import pickle
import os

from handlers.apartments import register_apartments_router
from handlers.towns import register_towns_router
from tools.database import Database

dotenv.load_dotenv()

_url = os.getenv("DBURL")
_name = os.getenv("DBNAME")
_core = os.getenv("NLPCORE")

nlp = spacy.load(_core)
db = Database(_url, _name)

with open("models/prediction_model.pkl", "rb") as fp:
    lm = pickle.load(fp)

with open("models/clustering.pkl", "rb") as fp:
    kmeans = pickle.load(fp)

with open("models/scaler.pkl", "rb") as fp:
    scaler = pickle.load(fp)

appartments_router = register_apartments_router(db, nlp, kmeans, lm, scaler)
towns_router = register_towns_router(db)

app = FastAPI()
app.include_router(appartments_router)
app.include_router(towns_router)


if __name__ == "__main__":
    uvicorn.run(
        app="main:app", 
        # ssl_keyfile="settings/key.pem", 
        # ssl_certfile="settings/cert.pem",
        lifespan="on",
        reload=True
    )