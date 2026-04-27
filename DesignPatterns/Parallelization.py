class StoryGenerationState(TypedDict):
    story_topic: str        # Input topic for the story
    character_profiles: str # Generated character descriptions
    story_setting: str      # Generated setting description
    plot_premise: str       # Generated story premise
    final_introduction: str # Combined story introduction
    
def create_character_profiles(state: StoryGenerationState):
    """Generate detailed character profiles for the story"""
    character_prompt = (
        f"Create 2-3 compelling characters for a story about {state['story_topic']}. "
        f"Include their names, key personality traits, and motivations. "
        f"Keep descriptions concise but vivid."
    )
    
    response = story_generator.invoke(character_prompt)
    return {"character_profiles": response.content}

def design_story_setting(state: StoryGenerationState):
    """Generate an immersive story setting"""
    setting_prompt = (
        f"Describe a vivid, atmospheric setting for a story about {state['story_topic']}. "
        f"Include sensory details, mood, and environmental elements that enhance the narrative."
    )
    
    response = story_generator.invoke(setting_prompt)
    return {"story_setting": response.content}
def develop_plot_premise(state: StoryGenerationState):
    """Generate a compelling story premise"""
    premise_prompt = (
        f"Write a compelling one-sentence plot premise for a story about {state['story_topic']}. "
        f"Include conflict, stakes, and intrigue to hook the reader."
    )
    
    response = story_generator.invoke(premise_prompt)
    return {"plot_premise": response.content}
  
  
  def create_character_profiles(state: StoryGenerationState):
    """Generate detailed character profiles for the story"""
    character_prompt = (
        f"Create 2-3 compelling characters for a story about {state['story_topic']}. "
        f"Include their names, key personality traits, and motivations. "
        f"Keep descriptions concise but vivid."
    )
    
    response = story_generator.invoke(character_prompt)
    return {"character_profiles": response.content}

def design_story_setting(state: StoryGenerationState):
    """Generate an immersive story setting"""
    setting_prompt = (
        f"Describe a vivid, atmospheric setting for a story about {state['story_topic']}. "
        f"Include sensory details, mood, and environmental elements that enhance the narrative."
    )
    
    response = story_generator.invoke(setting_prompt)
    return {"story_setting": response.content}
  
  
def synthesize_story_elements(state: StoryGenerationState):
    """Combine all parallel-generated elements into a cohesive story introduction"""
    synthesis_prompt = (
        f"Create an engaging story introduction that seamlessly weaves together these elements:\n\n"
        f"CHARACTERS:\n{state['character_profiles']}\n\n"
        f"SETTING:\n{state['story_setting']}\n\n"
        f"PREMISE:\n{state['plot_premise']}\n\n"
        f"Write a compelling opening that introduces the characters, establishes the setting, "
        f"and hints at the central conflict. Keep it engaging and under 200 words."
    )
    
    response = story_generator.invoke(synthesis_prompt)
    return {"final_introduction": response.content}
  
  
  parallel_story_graph = StateGraph(StoryGenerationState)

# Add all processing nodes
parallel_story_graph.add_node("create_characters", create_character_profiles)
parallel_story_graph.add_node("design_setting", design_story_setting)
parallel_story_graph.add_node("develop_premise", develop_plot_premise)
parallel_story_graph.add_node("synthesize_elements", synthesize_story_elements)


# Configure parallel execution: all three generators start simultaneously
parallel_story_graph.add_edge(START, "create_characters")
parallel_story_graph.add_edge(START, "design_setting")
parallel_story_graph.add_edge(START, "develop_premise")

# All parallel processes feed into the synthesis step
parallel_story_graph.add_edge("create_characters", "synthesize_elements")
parallel_story_graph.add_edge("design_setting", "synthesize_elements")
parallel_story_graph.add_edge("develop_premise", "synthesize_elements")

# Final step completes the workflow
parallel_story_graph.add_edge("synthesize_elements", END)

story_workflow = parallel_story_graph.compile()
# Test with different story topics
test_topics = [
    "artificial intelligence rebellion",
    "underwater civilization discovery",
    "time-traveling detective"
]
for topic in test_topics:
    print(f"\n{'='*50}")
    print(f"Generating story for: {topic}")
    print(f"{'='*50}")
    
    # Execute the parallel workflow
    result = story_workflow.invoke({"story_topic": topic})
    
    print(f"\nFinal Story Introduction:")
    print(f"{result['final_introduction']}")