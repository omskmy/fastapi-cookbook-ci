from pydantic import BaseModel


class BaseRecipe(BaseModel):
    title: str
    cooking_time: int
    ingredients: str
    description: str


class RecipeIn(BaseRecipe):
    pass


class RecipeOut(BaseRecipe):
    id: int
    views: int

    class Config:
        from_attributes = True
