from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
# langchain_core.runnables provides components to create a data pipeline (LCEL)
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
import os

# Load environment variables from a .env file (specifically for MISTRAL_API_KEY)
load_dotenv()

def get_mistral_model():
    """
    Initializes the Mistral AI chat model using the API key from environment variables.
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("[ERROR] MISTRAL_API_KEY is missing from environment variables.")
        return None
    
    # Returns an instance of the ChatMistralAI class configured with specific parameters
    return ChatMistralAI(
        api_key=api_key,
        model="mistral-small",  # Uses the 'small' model which is efficient and often free/cheap
        temperature=0.2         # Lower temperature (0.2) makes the output more focused and deterministic
    )

def generate_title(summary: str) -> str:
    """
    Generates a concise and professional title for the provided summary using Mistral AI.
    """
    model = get_mistral_model()
    if not model:
        return "Meeting Summary"

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a professional editor. Create a short, professional, and catchy title (maximum 10 words) for a meeting based on its summary. Return only the title text without any quotes."),
        ("human", "Meeting Summary:\n{text}")
    ])

    chain = prompt | model | StrOutputParser()
    return chain.invoke({"text": summary}).strip().strip('"')

def summarize_transcript(transcript: str) -> str:
    """
    Takes a meeting transcript and generates a concise bulleted summary using Mistral AI.
    Handles long transcripts by splitting them into manageable chunks.
    """
    # 1. Initialize the model
    if not transcript or not transcript.strip():
        return "Empty transcript provided. Nothing to summarize."

    model = get_mistral_model()
    if not model:
        return "Summary could not be generated: Mistral API key missing."

    # 3. Define the Map Step: Summarize individual chunks into concise points
    map_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a professional meeting assistant. Summarize the following meeting transcript section into clear, concise bullet points highlighting the main topics and takeaways."),
        ("human", "Transcript Segment:\n{text}")
    ])

    # 4. Define the Reduce Step: Synthesize all chunk summaries into one detailed report
    reduce_prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a professional meeting analyst. Below is a collection of summaries from different parts of a meeting. "
            "Your task is to synthesize these into a single, cohesive, and highly detailed final summary of the entire video. "
            "Organize the output with logical headings, detailed paragraphs for context, and bullet points for specific details. "
            "Ensure the flow is natural and covers all key discussions mentioned."
        )),
        ("human", "Collection of partial summaries:\n\n{text}\n\nProvide the final comprehensive summary:")
    ])

    # 5. Construct LCEL Chains
    map_chain = map_prompt | model | StrOutputParser()
    reduce_chain = reduce_prompt | model | StrOutputParser()

    # 5. Pipeline Logic using Runnables
    # Chunker: splits the raw transcript into list of chunks
    chunk_step = RunnableLambda(lambda x: RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200).split_text(x))
    
    # Mapper: Prepares the dict for the chain and uses .map() to process all chunks in parallel/sequence
    map_step = RunnableLambda(lambda chunks: [{"text": c} for c in chunks]) | map_chain.map()
    
    # Reducer: Always run through reduce_chain to ensure the cohesive structure and 
    # logical headings defined in the system prompt are applied.
    reduce_step = RunnableLambda(
        lambda summaries: reduce_chain.invoke({"text": "\n\n".join(summaries)}) if summaries else "No summary generated."
    )
    
    # Finalizer: Wraps the final summary with a generated title
    finalize_step = RunnableLambda(lambda summary: f"# {generate_title(summary)}\n\n{summary}")

    # Construct the unified LCEL pipeline
    # We use RunnablePassthrough as the entry point
    pipeline = RunnablePassthrough() | chunk_step | map_step | reduce_step | finalize_step

    print(f"[SUMMARIZE] Executing LCEL summarization pipeline...")
    return pipeline.invoke(transcript).strip()



#2:00:08