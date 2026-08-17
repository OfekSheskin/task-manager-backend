from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import date
from app import models
from app.schemas.task_schemas import TaskCreate, TaskUpdate
from app.core.status import TaskStatus


def get_owned_task(db: Session, user: models.User, task_id: int) -> models.Task:

    task = db.execute(
        select(models.Task).where(
            models.Task.task_id == task_id,
            models.Task.owner_id == user.user_id,
        )
    ).scalars().first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task

def get_task(db: Session, user: models.User, task_id: int) -> models.Task:
    chosen_task = db.get(models.Task, task_id)
    if chosen_task is None:
                raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    if chosen_task.owner_id == user.user_id: # return the task without checking anything if the user is the owner
        return chosen_task

    root = chosen_task
    while root.parent_task_id is not None:#finds the root task of the chosen task
        root = db.get(models.Task, root.parent_task_id)

    task_share = db.execute( #try to the task share the user have for the chosen task
        select(models.TaskShare).where(
            models.TaskShare.shared_task_id == root.task_id,
            models.TaskShare.shared_user_id == user.user_id
            

        )).scalars().first()
    if task_share is None:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The task isn't shared with you",
        )
    return chosen_task


    


def get_tasks(db: Session, user: models.User) -> list[models.Task]:


    shared_tasks_root_ids = db.execute(
        select(models.TaskShare.shared_task_id).where(
            models.TaskShare.shared_user_id == user.user_id
        )
    ).scalars().all()

    owned_tasks = db.execute( # query for all the tasks the user owns
        select(models.Task).where(
            models.Task.owner_id == user.user_id)

    ).scalars().all()

    shared_tasks = db.execute( # query for all the tasks shared with the user
        select(models.Task).where(
            models.Task.task_id.in_(shared_tasks_root_ids))
    ).scalars().all()

    descendants = []
    frontier = shared_tasks_root_ids

    while frontier: #walk and query through the subtasks tree to find all the root task's subtasks
        children = db.execute(
            select(models.Task).where(models.Task.parent_task_id.in_(frontier))
        ).scalars().all()
        descendants.extend(children)#adds every item from the children list
        frontier = [c.task_id for c in children]




    # merge the lists by task_id so nothing shows up twice. 
    by_id = {t.task_id: t for t in owned_tasks}
    by_id.update({t.task_id: t for t in shared_tasks})
    by_id.update({t.task_id: t for t in descendants})


    return list(by_id.values())









def create_task(db: Session, user: models.User, task: TaskCreate) -> models.Task:
    if task.parent_task_id is not None:
        # Called as a guard: raises 404 if the parent is missing or is
        # not this user's, so a subtask can never hang off a stranger's task.
        get_owned_task(db, user, task.parent_task_id)

    new_task = models.Task(
        task_title=task.task_title,
        task_info=task.task_info,
        owner_id=user.user_id,
        parent_task_id=task.parent_task_id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def update_task(
    db: Session, user: models.User, task_id: int, task: TaskUpdate) -> models.Task:
    existing = get_owned_task(db, user, task_id) 
    data = task.model_dump(exclude_unset=True)

    if "parent_task_id" in data:
        _check_parent_change(db, user, existing, data["parent_task_id"])

    if "status" in data:
        _apply_status_change(db, existing, data["status"])


    for field, value in data.items():
        setattr(existing, field, value)

    db.commit()
    return existing


def delete_task(db: Session, user: models.User, task_id: int) -> None:
    task = get_owned_task(db, user, task_id)
    db.delete(task)
    db.commit()






#helper functions
def _check_parent_change(#helper function to apply parent rules when updating a task
    db: Session, user: models.User, task: models.Task, new_parent_id: int | None
) -> None:

    if new_parent_id is None:
        return

    if new_parent_id == task.task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A task cannot be its own parent",
        )

    # Raises 404 if the parent is missing or is not this user's.
    ancestor = get_owned_task(db, user, new_parent_id)

    # Walk up from the new parent. Meeting `task` on the way to the root means
    # the new parent is one of its descendants.
    while ancestor.parent_task_id is not None:
        if ancestor.parent_task_id == task.task_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A task cannot be moved under one of its own subtasks",
            )
        ancestor = get_owned_task(db, user, ancestor.parent_task_id)

def _apply_status_change(
    db: Session,  task: models.Task, new_status: str   
)-> None:
    if new_status is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="a status cannot be null"
        )
    if new_status == TaskStatus.DONE:
        #check if a task has a subtask whos not done before setting it to done.
        unfinished_child = db.execute(select(models.Task).where(
            models.Task.parent_task_id == task.task_id,
            models.Task.status == TaskStatus.TO_DO,
        )).scalars().first()
        if unfinished_child is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A task cannot be set to done if one of its children is not done"
            )
        task.done_date = date.today()
        return

    if new_status == TaskStatus.TO_DO:
        if task.parent_task_id is None:
            task.done_date = None
            return  
        parent = db.get(models.Task, task.parent_task_id)
        if parent.status == TaskStatus.DONE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A task cannot be set to to do if its parent is already done"
            )
        task.done_date = None
        return  



    if new_status == TaskStatus.CANCELLED:
        task.done_date = None
        _cascade_cancel(db, task)
        return


def _cascade_cancel(db: Session, task: models.Task) -> None:
    children = db.execute(
        select(models.Task).where(models.Task.parent_task_id == task.task_id)
    ).scalars().all()

    for child in children:
        child.status = TaskStatus.CANCELLED
        child.done_date = None
        _cascade_cancel(db, child)



