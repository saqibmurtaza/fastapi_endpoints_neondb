from fastapi.testclient import TestClient
from fastapi_endpoints_neondb.main import app, get_session, engine, settings, Todo
from sqlmodel import Session, create_engine, select, SQLModel

### FIRST TEST READ ROOT
def test_read_root():
    client = TestClient(app=app)
    response = client.get("/") # we generate https request to server & hold server-response in response
    assert response.status_code == 200, "Status Code Failure" # assertion test: if server-response == 200 (Passesd) else: Status code failure
    assert response.json() == {"Hello":"My First API Endpoint"}, "Server-Response != Content"

### SECOND TEST CREATE_TODO
def test_create_todo():
    connection_string = (str(settings.TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg2"))
    
    engine = create_engine(connection_string, connect_args={"sslmode":"require"})
    
    SQLModel.metadata.create_all(engine) # automatically generate db tables, passing engine as an argument, which their have dtails of test db connection details

    with Session(engine) as session:
        def dependecy_override_function(): # return session which use engine of test_db_url
            return session
    
    app.dependency_overrides[get_session] = dependecy_override_function

    client = TestClient(app=app)
    todo_content = Todo(id=1, content="Buy Grocery") # initiate instance of Todo class
    response = client("/todo/",json=todo_content) # generate http request to server with payload-json-request
    


