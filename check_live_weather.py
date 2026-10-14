"""Verify actual WeatherAPI data through the running MCP HTTP server."""
import asyncio
import json
from pathlib import Path
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    output = {}
    async with streamablehttp_client("http://localhost:8085/mcp") as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            for name, args in [("get_current_weather", {"city": "Hanoi"}),
                               ("get_forecast", {"city": "Hanoi", "days": 3})]:
                result = await session.call_tool(name, args)
                text = "\n".join(item.text for item in result.content if hasattr(item, "text"))
                output[name] = text
                if result.isError or "Unable to fetch" in text or "not configured" in text:
                    raise RuntimeError(f"Live weather tool failed: {name}")
                if name == "get_current_weather" and "Last updated:" not in text:
                    raise RuntimeError("Missing update timestamp")
                if name == "get_forecast" and text.count("Chance of Rain:") != 3:
                    raise RuntimeError("Expected a three-day forecast")
                print(name + ":\n" + text)
    (Path(__file__).parent / "evidence/live-weather.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    asyncio.run(main())
