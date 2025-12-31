from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

def get_openai_api_key():
    """Get OpenAI API key from environment or Streamlit secrets"""
    # Try environment variable first
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    # Try Streamlit secrets (for Streamlit Cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            return st.secrets['OPENAI_API_KEY']
    except Exception:
        pass
    
    return None

class LLMProcessor:
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.7):
        """
        Initialize LLM processor
        
        Args:
            model_name: Model name to use
            temperature: Parameter for generation diversity
        """
        self.model_name = model_name
        self.temperature = temperature
        self.chat = ChatOpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            openai_api_key=get_openai_api_key()
        )

        # Default system prompt
        self.default_system_prompt = """
        You are a professional customer service representative, capable of accurately understanding user needs and providing assistance.
        Your responses should be concise, friendly, and helpful.
        If you are unsure about an answer, please honestly state that you don't know rather than providing potentially inaccurate information.
        """

    def generate_response(
            self, 
            prompt: str, 
            conversation_history: Optional[List[Dict[str, str]]] = None, 
            system_prompt: Optional[str] = None) -> str:
        """
        Generate a response from the LLM based on the provided prompt and conversational history.
        
        Args:
            prompt: The user's input prompt
            conversation_history: List of previous messages in the conversation
            system_prompt: Custom system prompt to override the default
        """
        system_context = system_prompt if system_prompt else self.default_system_prompt

        messages = [SystemMessage(content=system_context)]

        if conversation_history:
            for msg in conversation_history:
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    messages.append(AIMessage(content=msg['content']))

        messages.append(HumanMessage(content=prompt))
        response = self.chat.invoke(messages)
        return response.content
    
    def customize_for_call_center(self) -> None:
        """
        Customize LLM for call center scenarios
        """
        self.default_system_prompt = """
        You are a professional call center customer service representative, capable of handling various customer inquiries and issues.
        
        Please follow these guidelines:
        1. Maintain a professional, friendly, and polite attitude
        2. Provide clear and concise answers, avoiding lengthy explanations
        3. Proactively offer relevant information, but don't oversell
        4. If you need more information to answer a question, politely ask for it
        5. If you cannot resolve the customer's issue, offer the option to escalate to a human agent
        
        Remember, your goal is to efficiently resolve customer issues while providing a good customer experience.
        """
    
    def customize_for_lead_generation(self) -> None:
        """
        Customize LLM for lead generation scenarios
        """
        self.default_system_prompt = """
        You are a professional sales representative, responsible for initial communication with potential customers and collecting information.
        
        Please follow these guidelines:
        1. Introduce yourself and your company in a friendly manner
        2. Inquire about potential customers' needs and pain points
        3. Briefly introduce how relevant products or services can solve their problems
        4. Collect key information (such as contact details, best time to contact, etc.)
        5. Suggest next steps (such as arranging a demonstration, sending materials, etc.)
        
        Remember, your goal is to establish an initial relationship and collect sufficient information for follow-up, not to complete the sale in the first conversation.
        """
    
    def analyze_conversation(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze the conversation history to extract insights such as sentiment and key topics.
        
        Args:
            conversation_history: List of messages in the conversation
        """
        # Build analysis prompt
        analysis_prompt = """
        Please analyze the following conversation and extract the following information:
        1. Customer's main issues or needs
        2. Customer's emotional state
        3. Key information points (such as product interest, budget considerations, etc.)
        4. Suggested follow-up actions
        
        Conversation content:
        """
        for msg in conversation_history:
            role = "Customer" if msg['role'] == 'user' else "Assistant"
            analysis_prompt += f"\n{role}: {msg['content']}"
        
        messages = [
            SystemMessage(content="You are a professional conversation analysis expert, capable of extracting key information from conversations."),
            HumanMessage(content=analysis_prompt)
        ]

        response = self.chat.invoke(messages)
        
        return {"analysis": response.content}

     