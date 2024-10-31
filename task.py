from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import sqlite3
from typing import List, Optional

app = FastAPI()

def db():
    con = sqlite3.connect("task.db")
    con.row_factory = sqlite3.Row
    return con

class Task(BaseModel):
    id: int
    title: str
    description: str
    completed: bool = False

class UpdateTask(BaseModel):
    title: str
    description: str

@app.get("/")
def read_root():
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM task")
    data = cur.fetchall()
    return data

@app.get("/tasks/{id}")
def get_task(id: int):
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM task WHERE id = ?", (id,))
    data = cur.fetchone()
    
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    return data

@app.post("/tasks")
def create_task(create: Task):
    con = db()
    cur = con.cursor()
    cur.execute("INSERT INTO task (title, description, status) VALUES (?, ?, ?)", 
                (create.title, create.description, "Pending"))
    con.commit()
    return {"message": "Task created successfully"}

@app.put("/tasks/{id}")
def update_task(id: int, update: UpdateTask):
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM task WHERE id = ?", (id,))
    data = cur.fetchone()

    if data is None:
        raise HTTPException(status_code=404, detail="No Task Found")
    
    cur.execute("UPDATE task SET title = ?, description = ? WHERE id = ?", 
                (update.title, update.description, id))
    con.commit()
    return {"message": "Task updated successfully"}

@app.delete("/tasks/{id}")
def delete_task(id: int):
    con = db()
    cur = con.cursor()
    cur.execute("DELETE FROM task WHERE id = ?", (id,))
    con.commit()
    return {"message": "Task deleted successfully"}

@app.put("/tasks/{id}/complete")
def mark_task_completed(id: int):
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM task WHERE id = ?", (id,))
    data = cur.fetchone()

    if data is None:
        raise HTTPException(status_code=404, detail="Task not found")

    cur.execute("UPDATE task SET status = 'Completed' WHERE id = ?", (id,))
    con.commit()
    return {"message": "Task marked as completed"}

@app.get("/tasks/completed")
def get_completed_tasks():
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM task WHERE status = 'Completed'")
    data = cur.fetchall()
    return data

@app.get("/tasks/status/{status}")
def get_tasks_by_status(status: str):
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM task WHERE status = ?", (status,))
    data = cur.fetchall()
    
    if not data:
        raise HTTPException(status_code=404, detail=f"No tasks with status: {status}")
    
    return data

@app.delete("/tasks/completed")
def delete_completed_tasks():
    con = db()
    cur = con.cursor()
    cur.execute("DELETE FROM task WHERE status = 'Completed'")
    con.commit()
    return {"message": "Completed tasks deleted successfully"}

@app.get("/tasks/search/{keyword}")
def search_tasks(keyword: str):
    con = db()
    cur = con.cursor()
    search_query = f"%{keyword}%"
    cur.execute("SELECT * FROM task WHERE title LIKE ? OR description LIKE ?", (search_query, search_query))
    data = cur.fetchall()
    
    if not data:
        raise HTTPException(status_code=404, detail="No tasks found matching the keyword")
    
    return data

@app.get("/tasks/count")
def count_total_tasks():
    con = db()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM task")
    count = cur.fetchone()[0]
    return {"total_tasks": count}

@app.get("/tasks/title/{keyword}")
def search_tasks_by_title(keyword: str):
    con = db()
    cur = con.cursor()
    search_query = f"%{keyword}%"
    cur.execute("SELECT * FROM task WHERE title LIKE ?", (search_query,))
    data = cur.fetchall()
    
    if not data:
        raise HTTPException(status_code=404, detail="No tasks found matching the keyword in title")
    
    return data

@app.get("/tasks/description/{keyword}")
def search_tasks_by_description(keyword: str):
    con = db()
    cur = con.cursor()
    search_query = f"%{keyword}%"
    cur.execute("SELECT * FROM task WHERE description LIKE ?", (search_query,))
    data = cur.fetchall()
    
    if not data:
        raise HTTPException(status_code=404, detail="No tasks found matching the keyword in description")
    
    return data

@app.get("/tasks/")
def get_tasks(skip: int = 0, limit: int = 10):
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM task LIMIT ? OFFSET ?", (limit, skip))
    data = cur.fetchall()
    return data

@app.put("/tasks/{id}/pending")
def mark_task_pending(id: int):
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM task WHERE id = ?", (id,))
    data = cur.fetchone()

    if data is None:
        raise HTTPException(status_code=404, detail="Task not found")

    cur.execute("UPDATE task SET status = 'Pending' WHERE id = ?", (id,))
    con.commit()
    return {"message": "Task marked as pending"}

@app.get("/tasks/expired")
def get_expired_tasks():
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM task WHERE status = 'Expired'")
    data = cur.fetchall()
    
    if not data:
        raise HTTPException(status_code=404, detail="No expired tasks found")
    
    return data

@app.put("/tasks/{id}/expire")
def mark_task_expired(id: int):
    con = db()
    cur = con.cursor()
    cur.execute("SELECT * FROM task WHERE id = ?", (id,))
    data = cur.fetchone()

    if data is None:
        raise HTTPException(status_code=404, detail="Task not found")

    cur.execute("UPDATE task SET status = 'Expired' WHERE id = ?", (id,))
    con.commit()
    return {"message": "Task marked as expired"}

@app.get("/tasks/count/completed")
def count_completed_tasks():
    con = db()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM task WHERE status = 'Completed'")
    count = cur.fetchone()[0]
    return {"completed_tasks": count}

@app.get("/tasks/titles")
def get_task_titles():
    con = db()
    cur = con.cursor()
    cur.execute("SELECT title FROM task")
    data = cur.fetchall()
    return [item["title"] for item in data]

@app.get("/tasks/{id}/status")
def get_task_status(id: int):
    con = db()
    cur = con.cursor()
    cur.execute("SELECT status FROM task WHERE id = ?", (id,))
    data = cur.fetchone()

    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"task_status": data["status"]}
