# Routing Schema

class ContentRoute(BaseModel):
  content_type : Literal["story " , "poem " , "joke "] = Field
  (description = "Type of content to generate")
  
  
  content_router = language_model.with_structured_output(ContentRoute)
  
  ##create the workflow state 
class RoutingState(TypedDict):
  user_input :str
  routing_decision : str
  final_output :str
  
  ##content handlers
def generate_story(state :RoutingState):
  story_prompt = f"Write an engaging short story based on: {state['user_input']}"
  response = language_model.invoke(story_prompt)
  return {"final_output": response.content}
  
def generate_poem(state :RoutingState):
  poem_prompt = f"Write an engaging short poem based on: {state['user_input']}"
  response = language_model.invoke(poem_prompt)
  return {"final_output": response.content}

  
def generate_joke(state :RoutingState): 
  joke_prompt = f"Tell me a funny joke based on: {state['user_input']}"
  response = language_model.invoke(joke_prompt)
  return {"final_output": response.content}
  
  
  
#router logic

def route_content_request(state :RoutingState):
  """Analyze input and determine the appropriate content type"""
  routing_messages = [
    SystemMessage(content="You are a content router that decides whether to generate a story, poem, or joke based on user input.Consider keywords, tone, and intent in your decision"),
    HumanMessage(content  = state['user_input'])
  ]
  decision = content_router.invoke(routing_messages)
  return {"routing_decison " : decision.content_type}


def determine_next_step(state: RoutingState):
    """Conditional function to route to the appropriate handler"""
    routing_map = {
        "story": "generate_story",
        "poem": "generate_poem",
        "joke": "generate_joke"
    }
    return routing_map.get(state["routing_decision"], "generate_story")
  
  
routing_graph = StateGraph(RoutingState)

# Add all processing nodes
routing_graph.add_node("route_content_request", route_content_request)
routing_graph.add_node("generate_story", generate_story)
routing_graph.add_node("generate_poem", generate_poem)
routing_graph.add_node("generate_joke", generate_joke)
# Define the workflow connections
routing_graph.add_edge(START, "route_content_request")
# Add conditional routing based on decision
routing_graph.add_conditional_edges(
    "route_content_request",
    determine_next_step,
    {
        "generate_story": "generate_story",
        "generate_poem": "generate_poem",
        "generate_joke": "generate_joke"
    }
)
# Connect all handlers to the end
routing_graph.add_edge("generate_story", END)
routing_graph.add_edge("generate_poem", END)
routing_graph.add_edge("generate_joke", END)
# Compile the workflow
content_routing_workflow = routing_graph.compile()