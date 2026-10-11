from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401  (importing this registers every model with Base)

Base.metadata.create_all(bind=engine)

print("Tables created:")
for table_name in Base.metadata.tables:
    print(" -", table_name)
