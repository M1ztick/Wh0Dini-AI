#!/usr/bin/env python3
"""
Interactive test script for Wh0Dini-AI
Allows you to chat with your AI directly from the terminal
"""

import json
import sys

import requests

BASE_URL = "http://localhost:8000"


def chat_interactive():
    """Interactive chat session with Wh0Dini-AI"""
    print("🎭 Welcome to Wh0Dini-AI Interactive Chat!")
    print("Type 'quit' or 'exit' to end the conversation")
    print("=" * 50)

    conversation_history = []

    while True:
        try:
            # Get user input
            user_input = input("\n💬 You: ").strip()

            if user_input.lower() in ["quit", "exit", "bye"]:
                print("👋 Goodbye! Thanks for chatting with Wh0Dini-AI!")
                break

            if not user_input:
                continue

            # Add user message to history
            conversation_history.append({"role": "user", "content": user_input})

            # Send to API
            chat_data = {"messages": conversation_history, "stream": False}

            print("🤔 Wh0Dini-AI is thinking...")

            response = requests.post(
                f"{BASE_URL}/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                ai_response = result["response"]

                # Add AI response to history
                conversation_history.append(
                    {"role": "assistant", "content": ai_response}
                )

                print(f"🎭 Wh0Dini-AI: {ai_response}")

            else:
                print(f"❌ Error: {response.status_code} - {response.text}")

        except KeyboardInterrupt:
            print("\n👋 Chat interrupted. Goodbye!")
            break
        except requests.exceptions.Timeout:
            print("⏰ Request timed out. Please try again.")
        except Exception as e:
            print(f"❌ Error: {e}")


def test_streaming():
    """Test streaming endpoint"""
    print("🌊 Testing streaming response...")

    chat_data = {
        "messages": [
            {
                "role": "user",
                "content": "Tell me a short story about AI and privacy in 3 sentences.",
            }
        ],
        "stream": True,
    }

    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=30,
        )

        if response.status_code == 200:
            print("🎭 Wh0Dini-AI (streaming): ", end="", flush=True)
            for line in response.iter_lines():
                if line:
                    try:
                        # Parse the streaming response
                        line_str = line.decode("utf-8")
                        if line_str.startswith("data: "):
                            data = line_str[6:]  # Remove 'data: ' prefix
                            if data.strip() and data != "[DONE]":
                                chunk_data = json.loads(data)
                                if "content" in chunk_data:
                                    print(chunk_data["content"], end="", flush=True)
                    except json.JSONDecodeError:
                        continue
            print("\n")
        else:
            print(f"❌ Streaming failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Streaming error: {e}")


def main():
    """Main menu"""
    while True:
        print("\n🎭 Wh0Dini-AI Test Menu")
        print("=" * 30)
        print("1. Interactive Chat")
        print("2. Test Streaming")
        print("3. Quick Health Check")
        print("4. Exit")

        choice = input("\nSelect an option (1-4): ").strip()

        if choice == "1":
            chat_interactive()
        elif choice == "2":
            test_streaming()
        elif choice == "3":
            print("🏥 Checking health...")
            try:
                response = requests.get(f"{BASE_URL}/health")
                result = response.json()
                status = result.get("status", "unknown")
                print(f"Status: {status}")
                if status == "healthy":
                    print("✅ All systems operational!")
                else:
                    print("⚠️ Some issues detected")
            except Exception as e:
                print(f"❌ Health check failed: {e}")
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
