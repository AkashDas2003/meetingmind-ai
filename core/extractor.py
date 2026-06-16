#extract actionable items, decisions, questions
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
import os

# Load environment variables
load_dotenv()

def get_mistral_model(temperature: float = 0.2):
    """
    Initializes the Mistral AI model.
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("[ERROR] MISTRAL_API_KEY is missing.")
        return None
    return ChatMistralAI(api_key=api_key, model="mistral-small", temperature=temperature)

def extract_meeting_info(transcript: str) -> str:
    """
    Analyzes a meeting transcript to extract Action Items, Key Decisions, and Open Questions.
    Uses a Map-Reduce approach to handle long transcripts efficiently.
    """
    model = get_mistral_model(temperature=0.1) # Low temperature for factual extraction
    if not model:
        return "Extraction failed: MISTRAL_API_KEY is missing."

    # Map: Process each chunk to extract raw items
    map_prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a professional meeting scribe. Extract the following from the transcript segment:\n"
            "- Action Items: Specific tasks, assigned owners, and deadlines. If it's a talk/interview, extract actionable advice or 'To-Dos' for the audience.\n"
            "- Key Decisions: Agreements, conclusions, or final decisions.\n"
            "- Open Questions: Unresolved issues or questions that need follow-up.\n\n"
            "If no relevant info is found for a category in this segment, ignore it. Do not hallucinate."
        )),
        ("human", "Transcript Segment:\n{text}")
    ])

    # Reduce: Consolidate and deduplicate extracted items
    reduce_prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a lead project manager synthesizing notes from different parts of a meeting. "
            "Consolidate these into a single report, deduplicating items while preserving all details.\n\n"
            "Organize the output into these exact sections:\n"
            "✅ Action Items\n"
            "🧠 Key Decisions\n"
            "❓ Open Questions\n\n"
            "Format for Action Items: - [ ] **Task/Advice**: <description> | **Owner/Target**: <name or audience> | **Deadline/Context**: <time or scenario>\n"
            "If a section has no items, state 'No items identified.'"
        )),
        ("human", "Collection of extracted notes:\n\n{text}\n\nProvide the final consolidated report:")
    ])

    # 4. Chains
    map_chain = map_prompt | model | StrOutputParser()
    reduce_chain = reduce_prompt | model | StrOutputParser()

    # 5. Pipeline Logic using Runnables
    chunk_step = RunnableLambda(lambda x: RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500).split_text(x))
    map_step = RunnableLambda(lambda chunks: [{"text": c} for c in chunks]) | map_chain.map()

    # Ensure the final output always passes through the reduction step for consistent 
    # formatting (headers/emojis), even if there is only one chunk.
    reduce_step = RunnableLambda(
        lambda results: reduce_chain.invoke({"text": "\n\n".join(results)}) if results else "No content to analyze."
    )

    extraction_pipeline = RunnablePassthrough() | chunk_step | map_step | reduce_step

    if not transcript or not transcript.strip():
        return "Empty transcript provided. Nothing to extract."

    print(f"[EXTRACTOR] Executing actionable extraction pipeline...")
    return extraction_pipeline.invoke(transcript).strip()

if __name__ == "__main__":
    # Quick test logic
    test_transcript = """
    John: We need to fix the login bug by Friday. Sarah, can you take that?
    Sarah: Sure, I'll handle the login bug.
    John: Great. We've also decided to move the servers to AWS next month. 
    Sarah: What about the cost implications?
    John: We'll have to look into that later.
    """
    print(extract_meeting_info(test_transcript))