from database.database import Base, engine

import database.models

Base.metadata.create_all(engine)

print("Database created successfully.")