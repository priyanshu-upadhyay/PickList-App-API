from typing import Optional, List
import shutil
from datetime import date
from fastapi import FastAPI, File, UploadFile
from pdfDataExtract import processPDF


today = date.today()

app = FastAPI()


@app.get("/")
def index():
    return "Welcome to Item Picklist"




@app.post("/uploadfile/")
async def upload_file(files: List[UploadFile] = File(...)):
    for file in files:
        if((file.filename[-1:-5:-1]) == "fdp."):
            f = open("./uploaded_files/{}".format(str(today)+"_"+file.filename), "wb")
            with f as buffer:
                shutil.copyfileobj(file.file, buffer)
    
    message = processPDF()
    return {"Message": message}
    