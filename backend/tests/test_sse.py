import pytest
import httpx


@pytest.mark.asyncio
async def test_sse_logs():
    url = 'http://127.0.0.1:8000/servers/mc-vanilla-plus/logs'

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers={'Accept': 'text/event-stream'}, timeout=None)

        assert response.status_code == 200

        async for line in response.aiter_lines():
            if line:
                print(f"Log: {line}")

                assert "log" in line


if __name__ == '__main__':
    pytest.main()
