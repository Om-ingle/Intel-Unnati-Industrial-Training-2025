from typing import List, Optional
import nltk

class Document:
    def __init__(self, page_content, metadata): 
        self.page_content = page_content 
        self.metadata = metadata 


class SimpleChunker: 
    def __init__(self, chunk_size):
        self._chunk_size = chunk_size 

    def split_documents(self, documents: List[Document]) -> List[Document]:
        result = [] 
        for doc in documents: 
            content = doc.page_content 
            chunks = [content[i:i+self._chunk_size] for i in range(0, len(content), self._chunk_size)]
            result.extend([Document(page_content = chunk, metadata = doc.metadata) for chunk in chunks])
        return result


class OverlapTextSplitter: 
    def __init__(self, chunk_size, chunk_overlap):
        self._chunk_size = chunk_size 
        self._chunk_overlap = chunk_overlap 

    def split_documents(self, documents: List[Document]) -> List[Document]:
        result = [] 
        for doc in documents: 
            content = doc.page_content 
            chunks = [content[i:i+self._chunk_size] for i in range(0, len(content), self._chunk_size - self._chunk_overlap)]
            result.extend([Document(page_content = chunk, metadata = doc.metadata) for chunk in chunks])
        return result 
    

class TokenSplitter: 
    def __init__(self, chunk_size) -> None:
        self.chunk_size = chunk_size

    def _convert_to_document(self, text:str, metadata: str = None) -> Document: 
        return Document(page_content = text, metadata = metadata)
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        current_chunk = ""
        chunks = []
        for doc in documents:
            for sentence in nltk.sent_tokenize(doc.page_content):
                if len(current_chunk) + len(sentence) > self.chunk_size:  
                    chunks.append(Document(page_content=current_chunk, metadata=doc.metadata))
                    current_chunk = ""
                current_chunk += sentence
        if current_chunk:
            chunks.append(Document(page_content=current_chunk, metadata = doc.metadata))

        return chunks 



class RecursiveCharacterTextSplitter:

    def __init__(self, chunk_size) -> None:
        super().__init__()
        self._separators = ["\n\n", "\n", ".", " "]
        self._chunk_size =  chunk_size
        self._output = []


    def _split_text(self, text: str, separator: str) -> List[str]:
        return text.split(separator)
   

    def check_splits(self, split: str, separator_count: int, chunk_size: int, metadata):

        if len(split) < chunk_size: 
            self._output.append(split)    
        else:
            separator_count += 1
            new_splits = self._split_text(split, self._separators[separator_count])
            for i in range(len(new_splits)):
                
                self.check_splits(new_splits[i], separator_count, chunk_size, metadata)
                    

    def split_documents(self, documents: List[Document]) -> List[Document]:
        final_chunks = []

        for doc in documents:
            self._output = []
            separator_count = 0
            text = doc.page_content           
            splits = self._split_text(text, self._separators[separator_count])
            for s in splits:
                self.check_splits(s, separator_count, self._chunk_size, metadata=doc.metadata)
            
            res = ""
            for i in self._output:                
                if len(res) + len(i) > self._chunk_size:
                    final_chunks.append(Document(page_content=res, metadata=doc.metadata))
                    res = ""
                else:
                    res += i    
            
            if res:
                final_chunks.append(Document(page_content=res, metadata=doc.metadata))
 
        return final_chunks



class Adapter: 
    def __init__(self, chunk_size:int = 512, verbose: bool = True) -> str: 
        self._chunk_size = chunk_size 
        self.verboseprint = print if verbose else lambda *a : None 

        self.verboseprint(f" ADAPTER: Adapter initialised successfully with the following configuration: chunk_size = {self._chunk_size}")

        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=self._chunk_size)

    def _convert_to_document(self, text:str, metadata: str = None) -> Document: 
        return Document(page_content = text, metadata = metadata)
    
    def get_chunks(self, docs: list[str]):
        documents = [self._convert_to_document(text = doc) for doc in docs]
        chunked_documents = self.text_splitter.split_documents(documents)

        self.verboseprint(f"ADAPTER: Document chunking successful.\n Number of Chunks = {len(chunked_documents)}")
        chunked_texts = [doc.page_content for doc in chunked_documents]
        return chunked_documents, chunked_texts