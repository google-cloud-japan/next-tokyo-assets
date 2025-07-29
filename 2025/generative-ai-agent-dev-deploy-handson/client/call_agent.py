from vertexai import agent_engines

agent = agent_engines.get("projects/gossy-workstations/locations/us-central1/reasoningEngines/5943722365245456384")

for event in agent.stream_query(
    user_id="USER_ID",
    message="Hello?",
):
  print(event)