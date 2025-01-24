# importing a necessary library
from langgraph.graph import StateGraph,MessagesState, START, END
from langgraph.graph.message import add_messages
from typing import Annotated, Literal, TypedDict
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults

import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
os.environ["GROQ_API_KEY"]= GROQ_API_KEY

class chatbot:
    def __init__(self): #initializing the model using groq
        
        self.llm=ChatGroq(model_name="Gemma2-9b-It")
    
        
    def call_tool(self): #Agent tool - Tavily serach tool
        tool = TavilySearchResults(max_results=2)
        tools = [tool]
        self.tool_node = ToolNode(tools=[tool]) #tool node
        self.llm_with_tool=self.llm.bind_tools(tools) #integrate the tool with LLM
        
    def call_model(self,state: MessagesState): 
        messages = state['messages']
        response = self.llm_with_tool.invoke(messages)
        return {"messages": [response]}
    
    def router_function(self,state: MessagesState) -> Literal["tools", END]:
        messages = state['messages']
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END
    
    
                
    def __call__(self): #Special method - whenever i call the class object(mybot()), it will call this method in backend
        self.call_tool() 
        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", self.tool_node)
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent",self.router_function,{"tools": "tools", END: END})
        workflow.add_edge("tools", 'agent')
        self.app = workflow.compile()
        return self.app
        
if __name__=="__main__":
    mybot=chatbot()
    workflow=mybot()
    response=workflow.invoke({"messages": ["who is a current prime minister of USA?"]})
    print(response['messages'][-1].content)
    
    