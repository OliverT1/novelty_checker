Below is a proposed Product Requirements Document (PRD) for a “Novelty Checker” web application. It details how the system should work, from backend to frontend, including how errors and logs should be handled, along with sample code snippets. The tech stack includes **FastAPI** for the backend and **LiteLLM** (with Gemini 2.0) for the AI integration.  

---

## 1. Overview

**Goal**: Enable users to enter a research question, then see whether it has been addressed in existing literature, with a **YES / NO** answer and a detailed explanation that cites relevant papers.  

**Key Steps**:  
1. User inputs a research question.  
2. The app calls the **Exa API** to retrieve `n` relevant research papers (titles, abstracts, and summaries).  
3. Summaries are fed into **Gemini 2.0** (via **LiteLLM**) to determine novelty.  
4. Gemini provides a **YES** or **NO** response and a more detailed explanation, with clickable links to each cited paper.  

---

## 2. Architecture

### 2.1 Backend (FastAPI)

1. **Endpoints**:  
   - `POST /novelty-check`
     - Receives user’s research question.
     - Orchestrates calls to the Exa API and Gemini 2.0.
     - Returns structured data (result, explanation, links).

2. **Modules**:  
   - **Exa API Integration Module**:  
     - Contains functions to query the Exa API, handle response parsing, and any error handling (like network errors).  
   - **AI Integration Module (Gemini 2.0 via LiteLLM)**:  
     - Handles prompt construction, calling Gemini via LiteLLM, and parsing the AI response.  
   - **Business Logic Module**:  
     - Ties together the Exa results and AI response to produce final data for the frontend.  
   - **Logging & Error Handling**:  
     - Centralized logger for capturing normal operations and errors.  

### 2.2 Frontend

1. **UI Elements**:  
   - **Text Input**: For the user’s research question.  
   - **Submit Button**: Triggers the backend call.  
   - **YES/NO Display**: Displays whether the question is novel or not.  
   - **Explanation**: Renders the detailed text from Gemini.  
   - **Clickable Citations**: Each citation is a link to a paper (the link might point directly to the paper’s source or another page).  

2. **Communication with Backend**:  
   - **AJAX / Fetch** request to `POST /novelty-check`.  
   - Receives JSON response with `novelty`, `explanation`, and `citations`.  

### 2.3 Proposed Directory Structure


novelty_checker/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration settings (API keys, env variables)
│   ├── exa_integration.py   # Functions/classes to interact with the Exa API
│   ├── gemini_integration.py# Functions/classes to interact with Gemini 2.0 via LiteLLM
│   ├── business_logic.py    # Core logic to combine Exa + Gemini results
│   ├── models.py            # Pydantic models for request/response
│   └── logger.py            # Custom logger setup
└── frontend/
    ├── package.json         # Frontend dependencies
    ├── src/
    │   ├── App.jsx          # Main React app
    │   ├── components/
    │   │   └── NoveltyChecker.jsx
    │   └── utils/
    │       └── api.js      # Functions to call the backend
    └── public/
        └── index.html       # HTML entry point
Notes:
backend/ contains the FastAPI server and integration modules.
frontend/ houses a React (or similar) application.

### 3.1 Backend

1. Classes / Modules to Implement
NoveltyCheckRequest (Pydantic model)

Fields:
research_question: str
Purpose:
Validate incoming requests to the /novelty-check endpoint.
NoveltyCheckResponse (Pydantic model)

Fields:
novelty: str (expect “YES” or “NO”)
explanation: str
Purpose:
Standardize the response structure to the client.
ExaIntegration (class)

Methods:
search_exa(query: str, limit: int) -> dict
Purpose:
Encapsulate all logic for querying the Exa API (including request formation, headers, error handling).
Return parsed data (paper titles, summaries, links).
GeminiIntegration (class)

Methods:
query_gemini(prompt: str) -> dict
Purpose:
Encapsulate logic for building prompts, calling Gemini via LiteLLM, and parsing results.
Provide error handling for Gemini timeouts or malformed responses.
BusinessLogic (class / module)

Methods:
check_novelty(research_question: str) -> dict
Purpose:
Serves as the “glue” that orchestrates calls to ExaIntegration and GeminiIntegration, merges data, and returns the final novelty check results.
Logger / logger.py (module)

Responsible for:
Setting up the logger with desired formatting.
Possibly providing wrapper methods like log_info, log_error for consistency.
config.py (module)

Holds environment-specific settings:
Exa API URL
Gemini (LiteLLM) API keys
Timeout/retry configs
main.py

Contains the FastAPI app initialization and the /novelty-check endpoint:
Imports NoveltyCheckRequest, NoveltyCheckResponse.
Uses the BusinessLogic class to handle requests.
Returns NoveltyCheckResponse.

###3.2 Frontend
App.jsx (main entry)

Renders the application’s router / main layout (if using routing).
Could import and render NoveltyChecker component.
NoveltyChecker.jsx (component)

Contains:
Input field for the research question.
Submit button that calls the backend.
Displays results (YES/NO, explanation with citations).
api.js (utility)

Functions:
postNoveltyCheck(question: string): Promise<NoveltyCheckResponse>
Purpose:
Make the fetch or axios call to the /novelty-check endpoint.
Return parsed JSON or throw an error.
HTML / CSS (either inline in JSX or separate)

Basic styling for the input field, results area, and error messages.




## 3. Detailed Steps

Below is a step-by-step outline of how the system should work from the moment a user types in a research question to displaying results.

### 3.1 Frontend Flow

1. **User Enters Question**  
   1. User types a query into the text box, e.g. “Has anyone looked into links between running and knee injuries?”  
2. **Submit Action**  
   1. User clicks the submit button.  
   2. The frontend creates a JSON payload:  
      ```json
      {
        "research_question": "Has anyone looked into links between running and knee injuries?"
      }
      ```
3. **Send to Backend**  
   1. The frontend sends this JSON to `POST /novelty-check`.  
   2. Shows a loading spinner or a “Processing...” state.  

### 3.2 Backend Processing

1. **Receive Request**  
   1. FastAPI endpoint `/novelty-check` reads `research_question` from the request body.  
   2. Perform initial validation (e.g., check if the string is empty).  
2. **Query Exa API**  
   1. Forward the `research_question` to the Exa API.  
   2. Handle potential network errors or invalid responses with logging and error messages.  
   3. Parse the response to retrieve an array of relevant papers, each containing (title, abstract, summary, link/DOI).  
3. **Assemble Prompt for Gemini**  
   1. Create a prompt that includes:  
      - The user’s original question.  
      - Summaries (and short references) of the `n` papers from Exa.  
      - Instruction to Gemini: “Determine if the question has already been researched. Return YES/NO and a detailed explanation. Cite relevant papers with clickable links.”  
4. **Call Gemini 2.0 (via LiteLLM)**  
   1. Use the LiteLLM library to send the prompt to Gemini.  
   2. Gemini responds with:  
      - `novelty`: “YES” or “NO”  
      - `explanation`: A text block explaining the answer, with citations in HTML link format or an easily parsed syntax.  
5. **Parse Gemini’s Response**  
   1. Extract the `novelty` field (YES/NO).  
   2. Extract the `explanation`, ensuring any citations are converted to a standard format (e.g., Markdown or inline HTML).  
6. **Return JSON**  
   1. Format a JSON object:  
      ```json
      {
        "novelty": "NO",
        "explanation": "It seems this topic has been studied before. [Paper A](http://link-A)..."
      }
      ```  
   2. Send this back to the frontend.  

### 3.3 Frontend Display

1. **Handle Response**  
   1. Hide the loading spinner.  
   2. Read the `novelty` and `explanation` fields from the response.  
   3. Display the “YES” or “NO” result prominently.  
   4. Render the explanation text, ensuring citations are clickable.  
2. **Error Handling**  
   1. If an error is returned (e.g., `4XX` or `5XX`), show a notification to the user.  

---

## 4. Error Checks and Logging

### 4.1 Error Checks

1. **Empty Research Question**  
   - If the user doesn’t type anything, the system should return a `400 Bad Request` with a clear message: “Research question is required.”  
2. **Exa API Errors**  
   - Handle timeouts, invalid JSON, or unexpected statuses.  
   - Log the error, return a `500 Internal Server Error` or a relevant code.  
3. **Gemini 2.0 Errors**  
   - If Gemini fails or returns malformed data, log the error.  
   - Return a fallback response or a `503 Service Unavailable` with a readable error message.  

### 4.2 Logging

- **Log Levels**:  
  - **INFO**: Log each request to `/novelty-check` with user’s query truncated for readability.  
  - **WARNING**: Log slow responses or partial failures.  
  - **ERROR**: Log exceptions from Exa or Gemini calls.  
- **Log Format**:  
  - Include timestamps, endpoint name, severity, and relevant request data.  

---

## 5. Sample Code

### 5.1 Backend (FastAPI)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import requests
from lite_llm import Gemini

app = FastAPI()

# Configuring the logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

# Define request/response models
class NoveltyCheckRequest(BaseModel):
    research_question: str

class NoveltyCheckResponse(BaseModel):
    novelty: str
    explanation: str

@app.post("/novelty-check", response_model=NoveltyCheckResponse)
def novelty_check(payload: NoveltyCheckRequest):
    research_question = payload.research_question.strip()
    
    # 1. Validate user input
    if not research_question:
        logging.warning("Empty research question received")
        raise HTTPException(status_code=400, detail="Research question is required.")
    
    # 2. Query Exa API
    try:
        # Example request to Exa API - adjust URL and payload
        exa_api_url = "https://api.exa.com/v1/search"
        exa_payload = {"query": research_question, "limit": 5}
        exa_response = requests.post(exa_api_url, json=exa_payload, timeout=10)
        exa_response.raise_for_status()  # Raises HTTPError if status != 200
        exa_data = exa_response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Exa API error: {e}")
        raise HTTPException(status_code=500, detail="Error communicating with Exa API.")
    
    # 3. Assemble data for Gemini
    papers = exa_data.get("papers", [])
    # Build a compact summary to feed into Gemini
    paper_summaries = []
    for idx, paper in enumerate(papers):
        summary_text = f"Paper {idx+1}: {paper.get('summary', '')} [Link: {paper.get('link', '#')}]"
        paper_summaries.append(summary_text)
    combined_summaries = "\n".join(paper_summaries)
    
    gemini_prompt = f"""
    The user asked: "{research_question}"
    We have the following relevant research summaries:
    {combined_summaries}
    
    Please determine if the question has already been researched.
    Return:
    - A 'YES' or 'NO' statement about novelty.
    - A detailed explanation with citations as clickable links (e.g. [Paper 1](http://...)).
    """
    
    # 4. Call Gemini 2.0 via LiteLLM
    try:
        gemini = Gemini(api_key="YOUR_GEMINI_API_KEY")  # Hypothetical usage
        gemini_response = gemini.generate(prompt=gemini_prompt)
    except Exception as e:
        logging.error(f"Gemini error: {e}")
        raise HTTPException(status_code=503, detail="Error communicating with Gemini.")
    
    # 5. Parse Gemini response (Assume we get JSON-like structure)
    # For demonstration, let's assume gemini_response is a dictionary 
    # with 'novelty' and 'explanation' keys.
    # In practice, you'll need to parse the text or JSON from gemini_response content.
    novelty = gemini_response.get("novelty", "UNKNOWN")
    explanation = gemini_response.get("explanation", "No detailed explanation provided.")
    
    return NoveltyCheckResponse(novelty=novelty, explanation=explanation)
```

### 5.2 Frontend (Example in React)

```jsx
import React, { useState } from 'react';

function NoveltyChecker() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    setLoading(true);
    setResult(null);
    setError('');

    try {
      const response = await fetch('/novelty-check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ research_question: question })
      });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Unknown error');
      }
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Novelty Checker</h1>
      <div>
        <input 
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Enter your research question"
          style={{ width: '300px', marginRight: '10px' }}
        />
        <button onClick={handleSubmit} disabled={loading}>
          {loading ? 'Checking...' : 'Check Novelty'}
        </button>
      </div>

      {error && <div style={{ color: 'red', marginTop: '10px' }}>{error}</div>}

      {result && (
        <div style={{ marginTop: '20px' }}>
          <h2>Novelty: {result.novelty}</h2>
          <p dangerouslySetInnerHTML={{ __html: result.explanation }} />
        </div>
      )}
    </div>
  );
}

export default NoveltyChecker;
```

---

## 6. Edge Cases

1. **User Spamming Requests**  
   - Implement throttling or rate-limiting in the backend.  
2. **No Papers Found by Exa**  
   - If the Exa API returns zero papers, Gemini might default to a “YES” (novel) response. Provide a fallback message like: “No papers found. It might be novel.”  
3. **Gemini ‘Hallucination’**  
   - In rare cases, Gemini might generate inaccurate citations. Offer a disclaimer or a second pass validation on links.  

---

## 7. Final Notes

- This PRD outlines a high-level architecture and a sample implementation strategy.  
- Actual production code will require robust security, performance tuning, and thorough testing before deployment.  
- Ensure you have proper environment variables for secrets (e.g., API keys).  

By following the above steps, you’ll have a solid foundation for building and deploying the Novelty Checker application using **FastAPI**, **LiteLLM**, and **Gemini 2.0**.