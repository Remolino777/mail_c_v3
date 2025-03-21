![Image](https://github.com/user-attachments/assets/21e28a88-d2b2-4ebb-b9d0-9dafa49e01d8)

##ReAct Email Agent: AI-Powered Email Classification & Response

Overview

ReAct Email Agent is an AI-powered system designed to classify and respond to incoming email messages efficiently. Built using LangChain and LangGraph, this intelligent agent follows the ReAct (Reasoning + Acting) paradigm to analyze emails, determine appropriate responses, and generate support or complaint tickets when necessary.

Features

Email Classification: Automatically categorizes incoming emails based on predefined classes.

Automated Responses: Generates context-aware replies to emails.

Ticket Generation: Creates support or complaint tickets based on the email's intent.

Multi-Step Reasoning: Uses LangGraph to enhance reasoning for complex queries.

Extensible Architecture: Easily adaptable for different use cases and integrations.

Tech Stack

LangChain: Provides language model orchestration.

LangGraph: Enables structured reasoning and decision-making.

Gemini API (or other LLMs): Powers natural language understanding and generation.

Installation

Requirements (Poetry)

Ensure you have Python 3.11 installed. Then, install dependencies using Poetry:

poetry install

Dependencies

The project uses the following dependencies:

python = "^3.11"
langchain = "^0.3.21"
langgraph = "^0.3.16"
langchain-core = "^0.3.45"
langchain-community = "^0.3.20"
langchain-google-genai = "^2.1.0"
jupyter = "^1.1.1"
python-dotenv = "^1.0.1"

Setup

Configure Environment Variables:

Copy the .env.example file and rename it to .env

cp .env.example .env

Add your API keys inside .env, e.g.,

GEMINI_API_KEY=your_api_key_here

Activate Virtual Environment:

poetry shell

Usage

Running the Agent

Execute the main script to start the agent:

python main.py

Contribution

Feel free to fork this repository and contribute. Pull requests are welcome!