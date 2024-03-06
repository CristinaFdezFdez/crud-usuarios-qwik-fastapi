from fastapi import FastAPI, HTTPException

# Para poder utilizar campos con fecha
from datetime import date, datetime

# Pydantic es una librería para validar los datos.
# BaseModel sirve para definir clases para crear los modelos de datos que se van a usar en la API.
from pydantic import BaseModel

from typing import List

# Motor es una versión asíncrona de PyMongo,
# la biblioteca estándar de Python para trabajar con MongoDB.
import motor.motor_asyncio

# Para aceptar peticiones de diferentes dominios
from fastapi.middleware.cors import CORSMiddleware

# Define el modelo de datos para un usuario utilizando Pydantic.
# Esto ayuda a FastAPI a validar los tipos de datos entrantes.
class User(BaseModel):
    dni: str
    nombre: str
    apellido: str
    telefono: str
    direccion: str
    fecha_nacimiento: date

# Crea la instancia de la aplicación FastAPI
app = FastAPI()

# Lista de origenes permitidos
origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Métodos permitidos
    allow_headers=["*"], # Cabeceras permitidas
)
# Cadena de conexión a MongoDB con autenticación
MONGODB_URL = "mongodb://admin:123@mongodb:27017/?authSource=admin"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.usersdb

# Endpoint para listar todos los usuarios.
@app.get("/users/", response_description="Lista todos los usuarios", response_model=List[User])
async def list_users():
    users = await db["users"].find().to_list(1000)
    return users

# Endpoint para crear un nuevo usuario.
@app.post("/users/", response_description="Añade un nuevo usuario", response_model=User)
async def create_user(user: User):
    user_dict = user.dict()
    user_dict["fecha_nacimiento"] = datetime.combine(user.fecha_nacimiento, datetime.min.time())
    await db["users"].insert_one(user_dict)
    return user

# Endpoint para obtener un usuario a partir del DNI.
@app.get("/users/{dni}", response_description="Obtiene un usuario por el DNI", response_model=User)
async def find_user(dni: str):
    user = await db["users"].find_one({"dni": dni})
    if user is not None:
        return user
    raise HTTPException(status_code=404, detail=f"Usuario con DNI {dni} no se ha encontrado.")

# Endpoint para borrar un usuario específico por DNI.
@app.delete("/users/{dni}", response_description="Borra un usuario por el DNI", status_code=204)
async def delete_user(dni: str):
    delete_result = await db["users"].delete_one({"dni": dni})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Usuario con DNI {dni} no se ha encontrado.")

# Endpoint para actualizar un usuario específico por DNI.
@app.put("/users/{dni}", response_description="Actualiza un usuario por el DNI", response_model=User)
async def update_user(dni: str, user: User):
    user_dict = user.dict()
    user_dict["fecha_nacimiento"] = datetime.combine(user.fecha_nacimiento, datetime.min.time())
    await db["users"].update_one({"dni": dni}, {"$set": user_dict})
    return user


# Endpoint para obtener todos los usuarios menores de edad.
@app.get("/users/minors/", response_description="Lista todos los menores de edad", response_model=List[User])
async def list_minors():
    now = datetime.now()
    pipeline = [
        {
            "$project":{
                "dni": 1,
                "nombre": 1,
                "apellido": 1,
                "direccion": 1,
                "telefono": 1,
                "fecha_nacimiento": 1,
                "edad":
                    {
                        "$divide": [
                        {"$subtract": [now, "$fecha_nacimiento"]},
                        365 * 24 * 60 * 60 * 1000
                    ]}
            }
        },
        {
            "$match":{
                "edad":{"$lt":18}
            }
        }
    ]


    minors = await db["users"].aggregate(pipeline).to_list(1000)
    return minors


# Endpoint para obtener todos los usuarios mayores de edad.
@app.get("/users/adults/", response_description="Lista todos los mayores de edad", response_model=List[User])
async def list_adults():
    now = datetime.now()
    pipeline = [
        {
            "$project":{
                "dni": 1,
                "nombre": 1,
                "apellido": 1,
                "direccion": 1,
                "telefono": 1,
                "fecha_nacimiento": 1,
                "edad":
                    {
                        "$divide": [
                        {"$subtract": [now, "$fecha_nacimiento"]},
                        365 * 24 * 60 * 60 * 1000
                    ]}
            }
        },
        {
            "$match":{
                "edad":{"$gte":18}
            }
        }
    ]


    adults = await db["users"].aggregate(pipeline).to_list(1000)
    return adults
