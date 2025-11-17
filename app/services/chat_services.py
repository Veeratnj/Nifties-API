
from app.services.agents import finance_team



async def get_agent_response(message: str) -> str:
    result = finance_team.run(message)
    return result.content











