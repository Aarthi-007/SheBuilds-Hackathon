from utils.retry import async_retry


async def run_with_retry(agent, input_data, max_attempts: int = 3):
    return await async_retry(agent.run, input_data, max_attempts=max_attempts)
