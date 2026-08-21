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

    root = _find_root(db,chosen_task)
  

    task_share = _get_share(db, root.task_id, user.user_id)
    
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
    owner_id = user.user_id  # a task with no parent belongs to whoever created it

    if task.parent_task_id is not None:
        # Called as a guard: raises 404 if the parent is missing, 403 if it is
        # neither owned by this user nor shared with them.
        parent_task = get_task(db, user, task.parent_task_id)

        owner_id = parent_task.owner_id

    new_task = models.Task(
        task_title=task.task_title,
        task_info=task.task_info,
        owner_id=owner_id,
        parent_task_id=task.parent_task_id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def update_task(
    db: Session, user: models.User, task_id: int, task: TaskUpdate) -> models.Task:
    existing = get_task(db, user, task_id) 
    data = task.model_dump(exclude_unset=True)

    if "status" in data:
        _apply_status_change(db, existing, data["status"])


    for field, value in data.items():
        setattr(existing, field, value)

    db.commit()
    return existing


def delete_task(db: Session, user: models.User, task_id: int) -> None:

    task = get_task(db, user, task_id)

    #check if the user isnt the owner of the task and the chosen task isnt a sub task.
    #if so then delete the user from the share rather then deleting the task.
    if task.owner_id != user.user_id and task.parent_task_id is None:
        task_share =  _get_share(db,task.task_id, user.user_id)
        db.delete(task_share)
        db.commit()
        return

    #otherwise(user is owner or task is a subtask) just delete the task
    db.delete(task)
    db.commit()


    









#----------------------------------------------------------------------------------------------------------------
#helper functions --------------------------------------------------------


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


#finds the root task of a chosen task
def _find_root(db: Session, task: models.Task) ->models.Task:
    root = task
    while root.parent_task_id is not None:
        root = db.get(models.Task, root.parent_task_id)

    return root



#try to find the task share the user have for a chosen task
def _get_share(db:Session, root_id: int, user_id: int) -> models.TaskShare | None:
     task_share = db.execute( 
        select(models.TaskShare).where(
            models.TaskShare.shared_task_id == root_id,
            models.TaskShare.shared_user_id == user_id
                

        )).scalars().first()

     return task_share



    




