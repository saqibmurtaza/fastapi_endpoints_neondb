from fastapi import FastAPI, Depends, HTTPException
from fastapi_endpoints_neondb import settings
from sqlmodel import SQLModel, create_engine, Session, Field, select
from contextlib import asynccontextmanager
from typing import Optional, Annotated
from pydantic import BaseModel

class Todo(SQLModel, table=True ):  ### Read Note:1
    id: Optional[int] = Field(default=None, primary_key=True)
    content:str = Field(index=True)

connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg2"
)

engine = create_engine(connection_string, connect_args={"sslmode":"require"}, pool_recycle=300) ### Read Note:2

def create_db_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager ### Read Note:3
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
def get_session(): ### Read Note:4
    with Session(engine) as session:
        yield session

@app.get("/")
def read_root():
    message = {"Hello":"My First API Endpoint"}
    return message

@app.post("/todo/")
def create_todo(todo:Todo, session:Annotated[Session, Depends(get_session)]): ### Read Note:5

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
def delete_todo(todo_id:int, session:Annotated[Session, Depends(get_session)]): #Read Note:7
  db_todo = session.get(Todo, todo_id)
  if db_todo:
      session.delete(db_todo)
      session.commit()
      return {"message":"Todo deleted successfully"}
  else:
      raise HTTPException(status_code= 404, detail="Todo not found")

### UPDATE_TODO_ENDPOINT
class UpdateTodoRequest(BaseModel): ### Read Note:6
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


'''
Note:1
By specifying table=True, 
--you are instructing the SQLModel to treat the class Todo as a database table.
it typically triggers the creation of a corresponding database table based on the fields defined in the class.
--The ORM framework will map the class attributes (fields) to table columns in the database. This mapping 
allows you to work with objects of the Todo class in your Python code while transparently 
interacting with database records.

Note: 2
In SQLAlchemy, the `Engine` is a central component responsible for database connection management. 
It provides an interface for executing SQL queries and managing transactions. 
The `create_engine()` function is used to create an `Engine` object,
 which represents a connection to the database.

 Note:3
 An asynccontextmanager named lifespan:
 It's used to perform initialization tasks before the application starts. 
 In this case, it prints a message and creates database tables.

 Note:4
get_session() is a function that yields an SQLAlchemy session. It's used to manage database sessions.
This function ensures that the session is properly closed after its use.
session:
represents a unit of work within a database connection. It encapsulates a series of database operations 
(such as inserts, updates, deletes, or queries) that should be treated as a single transaction

Note: 5
The session dependency is used in the API endpoints to interact with the database. 
It ensures that a session is created and passed to the endpoint functions.

Note:6
1: Importing the BaseModel class from the pydantic module. BaseModel is the foundation for 
creating Pydantic models.
2: UpdateTodoRequest: Define a new Pydantic model called UpdateTodoRequest. This model has a 
single field named content, which is of type str
We use this model to validate and parse incoming todo-request-data

Note:7
if you add parameter todo:Todo following issue be faced:
To address the issue of encountering a 422 validation error during the pytest test for delete_todo, 
specifically related to the todo: Todo parameter in the delete_todo function, you can modify the function
to remove the todo: Todo parameter from it 
{def delete_todo(todo_id:int, todo:Todo, session:Annotated[Session, Depends(get_session)]):}

Delete requests typically do not require a request body, so we can simplify the endpoint to only 
accept the todo_id for deletion.
'''