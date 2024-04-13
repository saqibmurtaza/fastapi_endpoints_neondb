from fastapi.testclient import TestClient
from fastapi_endpoints_neondb.main import app, get_session, settings
from sqlmodel import Session, create_engine, SQLModel
import json

### FIRST TEST READ ROOT
def test_read_root():
    client = TestClient(app=app)
    response = client.get("/")                                          # we generate https request to server & hold server-response in variable response
    assert response.status_code == 200, "Status Code Failure"           # assertion test: if server-response == 200 (Passesd) else: Status code failure
    assert response.json() == {"Hello":"My First API Endpoint"}, "Server-Response != Content"
    
### SECOND TEST CREATE_TODO
def test_create_todo():
    
    connection_string = (str(settings.TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg2"))
    engine = create_engine(connection_string, connect_args={"sslmode":"require"})
    SQLModel.metadata.create_all(engine)                                # automatically generate db tables, passing engine as an argument, which their have dtails of test db connection details
    with Session(engine) as session:
        def dependecy_override_function():                              # return session which use engine of test_db_url
            return session
    app.dependency_overrides[get_session] = dependecy_override_function

    client = TestClient(app=app)

    todo_data = {"content":"buy Grocerry"}
    response = client.post("/todo/",json=todo_data)                     # generate http request to server with todo_content as json-payload
    assert response.status_code == 200

    extract_content = response.content
    print(f"extracted_content_from_response:{extract_content}")
    
    response_in_dict= json.loads(extract_content)                       ### Read Note:1
    print(f"response_in_dict:{response_in_dict}")
    
    assert response_in_dict["content"] == todo_data["content"], "Assertion Test Failure, 'Content Not Found'"
    assert "id" in response_in_dict, " Assertion Test Failure, 'id not found'" 

                                                                        ### Read Note:2

### THIRD TEST READ_TODO_LIST

def test_read_todo_list():
    
    connection_string= str(settings.TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg2")
    engine = create_engine(connection_string, connect_args={"sslmode":"require"},
                            pool_recycle=300)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        def dependency_override_function():
            return session
    app.dependency_overrides[get_session] = dependency_override_function
    
    client = TestClient(app=app)

    response = client.get("/todo/")
    response_in_json = response.json()
    print(f"response_in_json:{response_in_json}")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

### FOURTH TEST DELETE_TODO
def test_delete_todo():

    connection_string= str(settings.TEST_DATABASE_URL).replace(
        "postgersql", "postgresql+psycopg2")
    engine = create_engine(connection_string, connect_args={"sslmode":"require"}, pool_recycle=300)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        def dependency_override_function():
            return session
    app.dependency_overrides[get_session] = dependency_override_function

    client = TestClient(app=app)

    create_todo = {"content":"Buy coffee, milk & cream"}
    response = client.post("/todo/", json=create_todo)
    assert response.status_code == 200, "Assertion Test Failure to Post/Create Todo "
    created_todo_id = response.json()["id"]
    print(created_todo_id)

    # Delete the created todo item
    response = client.delete(f"/todo/{created_todo_id}")
    
    assert response.status_code == 200, "Assertion Test Failure to Delete Todo"
    assert response.json() == {"message": "Todo deleted successfully"}, "Delete Response Message Mismatch"

### FIFTH TEST DELETE_TODO
def test_update_todo():

    connection_string = str(settings.TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg2")
    engine = create_engine(connection_string, connect_args={"sslmode":"require"}, pool_recycle=300)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        def dependency_override_function():
            return session
    app.dependency_overrides[get_session] = dependency_override_function

    client = TestClient(app=app)

    create_todo = {"content":"Buy Toys, Xbox"}
    response = client.post("/todo/", json=create_todo)
    assert response.status_code == 200, "Assertion Test Failure to create_todo in Test_update"

    created_todo_id = response.json()["id"]
    print(f"create_todo_id:{created_todo_id}")

    # Update the created Todo
    todo_data = {"content":"Buy Jackets"}
    response = client.put(f"/todo/{created_todo_id}", json=todo_data)
    print(f"response:{response.json()}")
    

    assert response.status_code == 200, "Assertion Test Failure"
    assert response.json().get("message") == "Todo successfully updated", "Update response message mismatch"
    
    # assert response.json()["content"] == todo_data["content"]         ### Read Note:3
 
    #################### NOTES #############################
    '''
    Note:1
    json.loads() is used to parse (deserialize) the JSON-formatted bytes (or string) 
    into a Python dictionary (dict)
    - json.loads(), which expects a JSON-formatted string (str), bytes, or bytearray as input, 
    not a Response object.
    -extract the JSON content (response body) from the Response object returned by client.post() 
    and then use json.loads() to deserialize it into a Python dictionary, because json.load doesn't 
    accept obect (server-response is in json object)

    Note:2 
    Since the id field is optional in Todo model and is automatically generated upon insertion, 
    & can rely on the database behavior to assign and return this value upon creation.
    This approach allows you to validate that the created todo has the expected content 
    and optionally verify the presence of an assigned 'id' in the response.

    Note:3
   "In the test, test_todo_update, we often encounter an assertion error (KeyError: 'content') 
   when attempting to verify the updated todo item's content with 
   assert response.json()["content"] == todo_data["content"]. 
   
   This error occurs because the response from a PUT (update) or DELETE request typically 
   does not include the content of the updated or deleted item in the response body. 
   Instead, these requests usually return a success message mentioned in your main.py code
   like "message": "Todo deleted successfully" or {"message": "Todo successfully updated"} to 
   indicate the success of the operation."
    '''