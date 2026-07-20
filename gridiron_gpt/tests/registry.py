
from phred.cli.registry import register_command, run_command, list_commands

def greet(name):
    return f"Hello, {name}!"

register_command("greet", greet)

def test_greet():
    assert run_command("greet", "Fred") == "Hello, Fred!"
    assert "greet" in list_commands()

if __name__ == "__main__":
    test_greet()
    print("✅ CLI registry test passed")
