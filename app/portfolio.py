import pandas as pd
import chromadb 
import uuid
import os

class Portfolio:
    def __init__(self , file_path = "app/rsrc/links_portfolio.csv"):
        self.file_path = file_path
        self.data = pd.read_csv(self.file_path)
        
        # Ensure the vector_db directory exists
        db_path = "vector_db"
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize the ChromaDB client with the path
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name="portfolio_collection")

    
    def load_portfolio(self):
        if not self.collection.count():
            for _, row in self.data.iterrows():
                self.collection.add(
                    documents=[row['TechStack']],
                    metadatas=[{"link": row['Portfolio_Link']}],
                    ids=[str(uuid.uuid4())]
                )

    
    def query_links(self , skills):
        return self.collection.query(
            query_texts=[skills],
            n_results=2
        ).get('metadatas' ,[])
    

