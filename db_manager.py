from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from elasticsearch import Elasticsearch


class ConnectionManager:
    def __init__(self, type: str, host: str, port: int, user: str = None, password: str = None, db_name: str = None):
        self.type = type.lower()
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name
        self.connection = None

    def connect(self):
        if self.type == "postgresql":
            # Creating a PostgreSQL connection
            self.connection = self._create_postgresql_connection()
        elif self.type == "elasticsearch":
            # Creating an Elasticsearch connection
            self.connection = self._create_elasticsearch_connection()
        else:
            raise ValueError(f"Unsupported connection type: {self.type}")

        return self.connection

    def _create_postgresql_connection(self):
        # Create a SQLAlchemy engine and session for PostgreSQL
        database_url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal()  # Return a new session instance

    def _create_elasticsearch_connection(self):
        # Create and return an Elasticsearch client
        es = Elasticsearch(host=self.host, port=self.port)
        return es

    def close(self):
        # Close the connection if applicable
        if self.type == "postgresql" and self.connection:
            self.connection.close()  # Close PostgreSQL session



# Dependency for PostgreSQL connection
def get_postgresql_connection(port, host, user, password, db_name):
    connection_manager = ConnectionManager(type="postgresql", host=host, port=port, user=user, password=password, db_name=db_name)
    db_session = connection_manager.connect()
    try:
        yield db_session
    finally:
        connection_manager.close()


# Dependency for Elasticsearch connection
def get_elasticsearch_connection(host, port):
    connection_manager = ConnectionManager(type="elasticsearch", host=host, port=port)
    es_client = connection_manager.connect()
    try:
        yield es_client
    finally:
        connection_manager.close()
