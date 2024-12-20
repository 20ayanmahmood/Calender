from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from fastapi.responses import HTMLResponse,JSONResponse


app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def excel_json(file_path):
    df = pd.read_excel(file_path)
    list1 = df["Enter Date"].unique().tolist()
    list1 = [ts for ts in list1 if pd.notna(ts)]
    Total = 0
    result = {}
    i = 0
    max_length = len(list1)
    for j in range(len(df)):
        if i >= max_length:
            break

        if df["Enter Date"][j] == list1[i]:
            if pd.notnull(df["Net P/L"][j]):
                Total += df["Net P/L"][j]
        else:
            result[list1[i]] = Total
            i += 1
            Total = 0

    if i < max_length:
        result[list1[i]] = Total
    
    # Convert Timestamp objects to string in 'YYYY-MM-DD' format
    formatted_result = {date.strftime('%Y-%m-%d'): value for date, value in result.items()}
    return formatted_result


@app.post("/process_excel/")
async def process_excel(file: UploadFile):
    try:
        file_location = f"uploaded_{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())

        result = excel_json(file_location)
        os.remove(file_location)  # Clean up uploaded file
        print({"status": "success", "data": result})
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("index.html", "r") as f:
        content = f.read()
    return content