import json
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from fastapi import HTTPException

load_dotenv()


def generate_mcq(topic: str, difficulty: int, count: int = 15) -> list[dict]:

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = """
        Your task is to generate a coding question with multiple choice answers.
        The question should be appropriate for the specified difficulty level (1 - 5)
        Level 1: Focus on basic trivia, common beginner questions
        Level 2: Focus on basic syntax, simple operations, or common programming concepts.
        Level 3: Cover intermediate concepts like data structures, algorithms, or language features, and 'gotcha' type of questions.
        Level 4: Include advanced topics, deeper concepts such as parallelism, concurrency, multithreading, threading, and async
        Level 5: Anything that pertains to the specific programming language, as long as it is more difficult than level 4 
        Return the challenge in the following JSON format (this is just an example):
        {
            "id": 8,
            "question": "What is the output of the following C++ code?\n\n```cpp\nint arr[] = {10, 20, 30};\nint* p = arr;\nstd::cout << *(p + 2);\n```",,
            "options": [
            "10",
            "20",
            "30",
            "Undefined behavior"
            ],
            "correct_answer": 3, // index of correct answer
            "explanation": // a short explanation of why it is correct
            "difficulty": 2, // level 3
            "topic": "C++"
        },
        Make sure the options are plausible but with only one clearly correct answer.
        Use the following format for code questions:
        "What is the output of the following C++ code?\n\ncpp\nint arr[] = {10, 20, 30};\nint* p = arr;\nstd::cout << *(p + 2);\n"
        You can see we have included ``` from markdown just before the language (cpp), and after \n at the end, this is for rendering purposes on the frontend.
        Generate 10 questions on the topic using difficulty level.
        Return as a JSON
    """

    try:
        print("Sending structured request to Gemini...")
    
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=f"You are an MCQ question generator. The questions should prepare a user for an interview. Topic: {topic}. Difficulty {difficulty}.",
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )
    
        parsed_json = json.loads(response.text)

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")

    return parsed_json