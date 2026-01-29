import pinecone
import os
import json
from dotenv import load_dotenv, find_dotenv


class PineconeOperations:

    def __init__(self):
        _ = load_dotenv(find_dotenv())  # read local .env file
        api_key = os.getenv('PINECONE_KEY')
        api_env = os.getenv('PINECONE_ENVIRONMENT')

        pinecone.init(
            api_key=api_key,
            environment=api_env
        )
        self.index = None

    def create_index(self, index_name='default') -> list:
        # fetch the list of indexes
        indexes = pinecone.list_indexes()

        # create index if there are no indexes found
        if len(indexes) == 0:
            pinecone.create_index(index_name, dimension=8, metric="euclidean")

        return indexes

    def connect_index(self):
        indexes = self.create_index()
        # connect to a specific index
        self.index = pinecone.Index(indexes[0])

    def upsert(self, data):
        # sample data of the format
        # [
        #     ("A", [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]),
        #     ("B", [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]),
        #     ("C", [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]),
        #     ("D", [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4]),
        #     ("E", [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
        # ]
        # Upsert sample data (5 8-dimensional vectors)
        return json.loads(str(self.index.upsert(vectors=data, namespace="quickstart")).replace("'", '"'))

    def fetch_stats(self):
        # fetches stats about the index
        stats = self.index.describe_index_stats()
        return str(stats)

    def query(self, query_vector):
        # query from the index, eg: [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
        response = self.index.query(
            vector=query_vector,
            top_k=2,
            include_values=True,
            namespace="quickstart"
        )
        return json.loads(str(response).replace("'", '"'))