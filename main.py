from contextlib import asynccontextmanager
from typing import AsyncGenerator, List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import models
import schemas
from database import engine, get_db, Base

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="Кулинарная книга", lifespan=lifespan)

@app.post("/recipes", response_model=schemas.RecipeOut, status_code=201)
async def create_recipe(recipe: schemas.RecipeIn, db: AsyncSession = Depends(get_db)) -> schemas.RecipeOut:
    new_recipe = models.Recipe(**recipe.model_dump(), views=0)
    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)
    return new_recipe

@app.get("/recipes", response_model=List[schemas.RecipeOut])
async def list_recipes(db: AsyncSession = Depends(get_db)) -> List[schemas.RecipeOut]:
    stmt = select(models.Recipe).order_by(models.Recipe.views.desc(), models.Recipe.cooking_time.asc())
    res = await db.execute(stmt)
    return res.scalars().all()

@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeOut)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)) -> schemas.RecipeOut:
    await db.execute(
        update(models.Recipe)
        .where(models.Recipe.id == recipe_id)
        .values(views=models.Recipe.views + 1)
    )
    await db.commit()
    res = await db.execute(select(models.Recipe).where(models.Recipe.id == recipe_id))
    recipe = res.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")
    return recipe

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)