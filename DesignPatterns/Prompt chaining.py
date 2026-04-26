from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class EmailState(TypedDict):
  topic :str
  key_points : str
  draft_email : str
  final_email : str
  
  
def extract_key_points(state : EmailState):
  prompt = f"List 3 key points about: {state['topic']}"
  response = llm.invoke(prompt)
  print(f"Key points extracted")
  return {"key_points": response.content}
  
  
def validate_key_points(state: EmailState):
  """Quality check: Ensure key points are actionable and specific"""
  key_points = state["key_points"]
  
  # Check for actionable words and specific content
  actionable_words = ['request', 'need', 'require', 'propose', 'suggest', 'recommend', 'deadline', 'schedule', 'meeting', 'discuss', 'review', 'approve', 'extension', 'support', 'assistance', 'feedback', 'update', 'status', 'progress', 'complete', 'deliver']
  
  # Convert to lowercase for checking
  points_lower = key_points.lower()
  
  # Count actionable words found
  actionable_count = sum(1 for word in actionable_words if word in points_lower)
  
  # Also check minimum length (should be substantial)
  word_count = len(key_points.split())
  
  if actionable_count >= 2 and word_count >= 15:
      print(f"✅ Key points validation: PASSED (Found {actionable_count} actionable words, {word_count} total words)")
      return "proceed"
  else:
      print(f"❌ Key points validation: FAILED (Only {actionable_count} actionable words, {word_count} total words) - regenerating...")
      return "regenerate" 
      
def write_draft(state: EmailState):
  """Step 2: Write email draft using key points"""
  prompt = f"""Write a professional email draft covering these points:
  {state['key_points']}"""
  response = llm.invoke(prompt)
  print(f" Draft written")
  return {"draft_email": response.content}
  
def polish_email(state: EmailState):
  """Step 3: Polish and add proper formatting"""
  prompt = f"Polish this email and add proper greeting/closing: {state['draft_email']}"
  response = llm.invoke(prompt)
  print(f"✅ Email polished")
  return {"final_email": response.content}
  
  
workflow = StateGraph(EmailState)

# Add processing nodes
workflow.add_node("extract_points", extract_key_points)
workflow.add_node("write_draft", write_draft)
workflow.add_node("polish_final", polish_email)
# Connect nodes with conditional logic
workflow.add_edge(START, "extract_points")
workflow.add_conditional_edges(
    "extract_points",
    validate_key_points,
    {
        "proceed": "write_draft",
        "regenerate": "extract_points"
    }
)
workflow.add_edge("write_draft", "polish_final")
workflow.add_edge("polish_final", END)
# Compile the workflow
compiled_workflow = workflow.compile()


def create_email(topic: str):
    """Run the complete email creation workflow"""
    print(f"📧 Creating email about: '{topic}'")
    print("-" * 40)
    
    result = compiled_workflow.invoke({"topic": topic})
    
    print("\n🎉 Email creation completed!")
    return result["final_email"]
