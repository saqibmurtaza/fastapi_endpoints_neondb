from fastapi import FastAPI, Depends, HTTPException
from fastapi_endpoints_neondb import settings
from sqlmodel import SQLModel, create_engine, Session, Field, select
from contextlib import asynccontextmanager
from typing import Optional, Annotated
from pydantic import BaseModel

class Todo(SQLModel, table=True ):
    id: Optional[int] = Field(default=None, primary_key=True)
    content:str = Field(index=True)

connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg2"
)

engine = create_engine(connection_string, connect_args={"sslmode":"require"}, pool_recycle=300)

def create_db_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Creating Database Tables ...") 
    create_db_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Fastapi Endpoints & Neon DB",
    version= "1.0.0",
    servers=[{
        "url" : "http://127.0.0.1:8000",
        "description" : " Development Server"
    }]
)
def get_session():
    with Session(engine) as session:
        yield session

@app.get("/")
def read_root():
    message = {"Hello":"My First API Endpoint"}
    return message

@app.post("/todo/")
def create_todo(todo:Todo, session:Annotated[Session, Depends(get_session)]):

    session.add(todo)
    session.commit()
    session.refresh(todo)
    print(f"Capture Created Todo : {todo}")
    return todo

@app.get("/todo/")
def read_todo_list(session: Annotated[Session, Depends(get_session)]):
    todos = session.exec(select(Todo)).all()
    return todos

@app.delete("/todo/{todo_id}")
def delete_todo(todo_id:int, todo:Todo, session:Annotated[Session, Depends(get_session)]):
  db_todo = session.get(Todo, todo_id)
  if db_todo:
      session.delete(db_todo)
      session.commit()
      return {"message":"Todo deleted successfully"}
  else:
      raise HTTPException(status_code= 404, detail="Todo not found")
'''
1: Importing the BaseModel class from the pydantic module. BaseModel is the foundation for 
creating Pydantic models.
2: UpdateTodoRequest: Define a new Pydantic model called UpdateTodoRequest. This model has a 
single field named content, which is of type str
We use this model to validate and parse incoming todo-request-data
'''
class UpdateTodoRequest(BaseModel):
    content:str

@app.put("/todo/{todo_id}")
def update_todo(todo_id:int,todo_update:UpdateTodoRequest, session:Annotated[Session, Depends(get_session)]):
    todo = session.get(Todo, todo_id) #fetch existing todo by id
    if todo: # if true (not empty)
        todo.content = todo_update.content #update the todo content
        session.commit()
        print(f"Todo:{todo} Updated to:{todo_update.content}")
        return {"message":"Todo successfully updated"}
    else:
        raise HTTPException(status_code=404, detail="Todo not Found")


        
        
