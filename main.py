import os, json
from langchain_community.llms import AI21
from langchain.prompts import PromptTemplate
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
load_dotenv()

ai21_llm = AI21(
    ai21_api_key=os.getenv("AI21_API_KEY"),
    temperature=0,
    maxTokens=1000,
    model="j2-jumbo-instruct"
)


def fetch_web_content(url):
    HEADERS = ({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US, en; q=0.5'
    })

    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.find('title').text if soup.find('title') else 'No title found'
            paragraphs = [p.get_text() for p in soup.find_all('p')]
            para = ' '.join(paragraphs)

            data = {
                "title": title,
                "content": para
            }
            with open("response.txt", 'a') as f:
                f.write(json.dumps(data))
            # print("data: ",data)
            return data
        else:
            print(f"Failed to retrieve content. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    

prompt_template = """
Use the following pieces of context to thoroughly answer the question at the end. 
If you don't know the answer or the context does not contain anything related to the question, just say that "Sorry! I could not find an answer for that in the given data.", don't try to make up an answer.

Context: {context}

Question: {question}
Answer:
"""

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=prompt_template
)

def generate_answer(context, question, llm=ai21_llm):

    formatted_prompt = prompt.format(context=context, question=question)

    try:
        response = llm.invoke(formatted_prompt)
        return response
    
    except Exception as e:
        return f"Error: {e}"

def main():
    
    url = input("Please enter the URL of the wensite: ")

    web_data = fetch_web_content(url)

    if web_data:
        context_data = web_data["content"]

        print("Chat with LLM \n")

        while True:

            question = input("User Input Question: ")

            if question.lower() in ['exit', 'quit']:
                print("Exiting. Goodbye!")
                break

            answer = generate_answer(context=context_data, question=question)

            print(f"LLM Response:{answer}")
    else:
        print("Could not fetch web content.")

if __name__ == "__main__":
    main()
