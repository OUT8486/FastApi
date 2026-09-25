from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello FastAPI"}

@app.get("/out")
def out():
    return {"ooout":"123456789"}

@app.get("/book/{id}")
def book(id:int):
    if id>0 and id <100:
        return {"id":id,"msg":f"this is {id}"}
    else:
        return {"false"}
