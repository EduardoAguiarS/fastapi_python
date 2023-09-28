from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session
from fastapi import FastAPI, status

app = FastAPI()


class Product(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(default=None, max_length=100)
    description: Optional[str] = Field(
        default=None, max_length=300, nullable=True)
    price: float = Field(default=None, nullable=False)
    is_offer: bool = Field(default=False, nullable=False)


SQLITE_FILE_NAME = "database.db"
sqlite_url = f"sqlite:///{SQLITE_FILE_NAME}"
engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()

session = Session(engine)


@app.get("/", status_code=status.HTTP_200_OK)
async def home():
    return {
        "message": "API de Produtos by FastAPI",
    }


# Return all products
@app.get("/produtos", status_code=status.HTTP_200_OK)
async def products():
    prod = session.query(Product).all()
    if len(prod) == 0:
        return {
            "message": "Não há produtos",
        }
    session.close()
    return {
        "message": "Todos os produtos",
        "data": prod,
    }


# Return a product by id
@app.get("/produtos/{prod_id}", status_code=status.HTTP_200_OK)
async def product_id(prod_id: int):
    prod = session.query(Product).all()
    filter_product = [product for product in prod if product.id == prod_id]
    if len(filter_product) == 0:
        return {
            "message": "Produto não existe",
        }
    session.close()
    return {
        "message": f"Produto com id {prod_id}",
        "data": filter_product,
    }


# Create a new product
@app.post("/produtos", status_code=status.HTTP_201_CREATED)
async def create_product(product: Product):
    prod = session.query(Product).all()
    if product.id in [product.id for product in prod]:
        return {
            "message": "Produto já existe",
        }
    if len(prod) == 0:
        product.id = 1
    else:
        product.id = max([product.id for product in prod]) + 1
    session.add(product)
    session.commit()

    return {
        "message": "Produto criado com sucesso",
    }


# Update a product
@app.patch("/produtos/{prod_id}", status_code=status.HTTP_200_OK)
async def update_product(prod_id: int, product: Product):
    prod = session.query(Product).all()
    filter_product = [product for product in prod if product.id == prod_id]
    if len(filter_product) == 0:
        return {
            "message": "Produto não existe",
        }
    product.id = prod_id
    filter_product[0].name = product.name
    filter_product[0].description = product.description
    filter_product[0].price = product.price
    filter_product[0].is_offer = product.is_offer
    session.add(filter_product[0])
    session.commit()
    session.close()
    return {
        "message": "Produto atualizado com sucesso",
    }


# Delete a product
@app.delete("/produtos/delete/{prod_id}", status_code=status.HTTP_200_OK)
async def delete_product(prod_id: int):
    db = session.query(Product).all()
    product = [product for product in db if product.id == prod_id]
    if len(product) == 0:
        return {
            "message": "Produto não existe",
        }
    session.delete(product[0])
    session.commit()
    session.close()
    return {
        "message": f"Produto com id {prod_id} deletado com sucesso",
    }
