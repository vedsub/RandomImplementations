class TravelTask(BaseModel):
    """Structure for individual travel planning tasks"""
    task_id: str = Field(description="Unique identifier for the task")
    task_type: str = Field(description="Type of travel planning task")
    task_description: str = Field(description="Detailed description of what needs to be done")
    priority: int = Field(description="Task priority (1-5, where 5 is highest)")
    required_context: List[str] = Field(description="Context needed from original request")

class TaskPlan(BaseModel):
    """Complete task breakdown from orchestrator"""
    tasks: List[TravelTask] = Field(description="List of travel planning tasks")
    estimated_duration: str = Field(description="Estimated time to complete all tasks")
    special_requirements: List[str] = Field(description="Any special considerations")

# Create structured orchestrator
task_orchestrator = travel_planner_llm.with_structured_output(TaskPlan)

def merge_worker_results(current: Dict[str, str], new: Dict[str, str]) -> Dict[str, str]:
    """Merge worker results from multiple concurrent workers"""
    if current is None:
        current = {}
    current.update(new)
    return current

def merge_execution_metadata(current: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    """Merge execution metadata from multiple concurrent workers"""
    if current is None:
        current = {}
    
    # Merge workers_executed lists
    current_workers = current.get('workers_executed', [])
    new_workers = new.get('workers_executed', [])
    
    merged_metadata = current.copy()
    merged_metadata.update(new)
    
    # Combine worker lists without duplicates
    all_workers = list(set(current_workers + new_workers))
    merged_metadata['workers_executed'] = all_workers
    
    return merged_metadata
  
class TravelPlanningState(TypedDict):
    original_request: str                                      # User's travel request
    task_breakdown: Dict[str, Any]                            # Orchestrator's task analysis
    accommodation_result: str                                 # Accommodation worker result
    activities_result: str                                    # Activities worker result
    dining_result: str                                        # Dining worker result
    transportation_result: str                                # Transportation worker result
    worker_results: Annotated[Dict[str, str], merge_worker_results]  # Combined worker results with reducer
    final_itinerary: str                                      # Synthesized travel plan
    execution_metadata: Annotated[Dict[str, Any], merge_execution_metadata]


def orchestrate_travel_planning(state: TravelPlanningState):
    """
    Orchestrator: Analyzes travel request and creates dynamic task breakdown
    """
    orchestrator_prompt = [
        SystemMessage(
            content="""You are a master travel planning orchestrator. Your job is to analyze 
            travel requests and break them down into specific, actionable tasks for specialist workers.
            
            Common travel planning tasks include:
            - accommodation_research: Find suitable hotels/lodging
            - activity_planning: Research attractions and experiences
            - dining_recommendations: Find restaurants and food experiences
            - transportation_planning: Plan getting around and between locations
            - budget_optimization: Ensure recommendations fit within budget
            - cultural_insights: Provide local customs and cultural information
            
            Consider the user's specific needs, timeline, budget, and preferences when creating tasks.
            Each task should be focused and actionable for a specialist worker."""
        ),
        HumanMessage(content=f"Plan travel tasks for: {state['original_request']}")
    ]
    
    # Get structured task breakdown
    task_plan = task_orchestrator.invoke(orchestrator_prompt)
    
    # Convert to dictionary for easier processing
    task_breakdown = {
        "tasks": [task.model_dump() for task in task_plan.tasks],
        "estimated_duration": task_plan.estimated_duration,
        "special_requirements": task_plan.special_requirements,
        "total_tasks": len(task_plan.tasks)
    }
    
    return {
        "task_breakdown": task_breakdown,
        "worker_results": {},  # Initialize worker results
        "execution_metadata": {
            "orchestration_timestamp": datetime.now().isoformat(),
            "task_count": len(task_plan.tasks),
            "workers_executed": []  # Track executed workers
        }
    }