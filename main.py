from contextlib import asynccontextmanager, contextmanager
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import mariadb

from model.task import Task, TaskCreateRequestBody, TaskOptionalRequestBody

# load env file
load_dotenv()


_conn: mariadb.Connection | None = None
_cursor: mariadb.Cursor | None = None

# TODO: extract into several file
# Connect to MariaDB Platform
def connect_db() -> mariadb.Connection | None:
    # TODO: read from env
    try:
        conn = mariadb.connect(
            user=os.getenv("DATABASE_USERNAME"),
            password=os.getenv("DATABASE_PASSWORD"),
            host=os.getenv("DATABASE_HOSTNAME"),
            port=int(os.getenv("DATABASE_PORT")) or 3306,
            database=os.getenv("DATABASE_NAME")

        )
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
    return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: use better method to set the value into global
    conn = connect_db()
    if conn is None:
        raise ConnectionError("Connection to database failed")
    
    global _conn
    _conn = conn

    global _cursor
    _cursor = _conn.cursor()

    yield
    # Clean up the ML models and release the resources
    conn.close()

app = FastAPI(lifespan=lifespan)


# CORS Setting
# WARNING: this may not safe, probably need to specify the origin
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/todo')
async def get_all_todo_list() -> list[Task]:
    statement = "SELECT id, name, is_done FROM task"
    _cursor.execute(statement)
    todo_list: list[Task] = [
        {
            'id': id,
            'name': name,
            'is_done': is_done
        } for (id, name, is_done) in _cursor
    ]
    return todo_list

@app.get('/todo/{id}')
async def get_single_todo_info(id: int) ->Task:
    statement = "SELECT id, name, is_done FROM task WHERE id = ?"
    _cursor.execute(statement, [id])
    
    todo: list[Task] = [
        {
            'id': id,
            'name': name,
            'is_done': is_done
        } for (id, name, is_done) in _cursor
    
    ]
    
    if (len(todo) > 1):
        todo = todo[0]

    if isinstance(todo, list):
        todo = todo[0]

    return todo

# TODO: make set the request
@app.post('/todo')
async def create_todo(request: TaskCreateRequestBody):
    _cursor.execute(
        "INSERT INTO task (name, is_done) VALUES (?, ?)", 
        [request.name, request.is_done])
    _conn.commit()
    
    return {
        'success': 'ok',
        'data': request
    }

@app.delete('/todo/{id}')
async def delete_todo(id: int):
    _cursor.execute("DELETE FROM task WHERE id = ?", [id])
    _conn.commit()
    
    return {
        'success': 'ok',
        'data': await get_all_todo_list()
    }

# PATCH for update
@app.patch('/todo/{id}')
async def patch_todo(id: int, task: TaskOptionalRequestBody):
    _previous_info = await get_single_todo_info(id)
    
    _cursor.execute(
        "UPDATE task SET name = ?, is_done = ? WHERE id = ?",
        [task.name or _previous_info.get("name"), task.is_done , id]
    )
    _conn.commit()

    return {
        'success': 'ok',
        'data': await get_single_todo_info(id)
    }


@app.put('/todo/{id}')
async def patch_todo(id: int, task: TaskOptionalRequestBody):
    _previous_info: Task = await get_single_todo_info(id)
    print(task)
    _cursor.execute(
        "UPDATE task SET name = ?, is_done = ? WHERE id = ?",
        [task.name or _previous_info.get("name"), task.is_done , id]
    )
    _conn.commit()

    return {
        'success': 'ok',
        'data': await get_single_todo_info(id)
    }