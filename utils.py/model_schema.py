from enum import Enum
from pydantic import BaseModel

class Role(str, Enum):
    """
    An enumeration to represent different roles within the system.
    
    Attributes:
        USER (str): Equivalent to the queries made by the user..
        SYSTEM (str): Allows us to specify the way the model answers questions. 
        ASSISTANT (str): represent the model’s responses
    """
    USER: str = 'user'
    SYSTEM: str = 'system'
    ASSISTANT: str = 'assistant'
    
class Message(BaseModel):
    """
    A model representing a message entity with a role and content.
    
    Attributes:
        role (Role): The role of the entity sending the message. Must be an instance of the Role enum.
        content (str): The textual content of the message.
    """
    role: Role
    content: str
