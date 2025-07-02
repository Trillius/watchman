
import pytest
from discord.ext import commands
from bot.cogs import monitoring

class MockBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!")

@pytest.fixture
def bot():
    return MockBot()

def test_monitoring_cog_load(bot):
    try:
        bot.add_cog(monitoring.Monitoring(bot))
        assert True
    except Exception as e:
        pytest.fail(f"Failed to load Monitoring cog: {e}")
