from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

class BaseAgent(ABC):
    def __init__(self, api_client, vector_store, name: str):
        self.api_client = api_client
        self.vector_store = vector_store
        self.name = name
        self.logger = logging.getLogger(f"Agent.{name}")
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's primary task"""
        pass
    
    def log_execution(self, task_description: str, result: Dict[str, Any]):
        self.logger.info(f"{self.name} completed: {task_description}")
        return result
