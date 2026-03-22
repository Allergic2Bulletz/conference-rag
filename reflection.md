## 📝 Reflection Questions

Answer these in your submission. Use your AI assistant to discuss these — it can prompt you with follow-up questions to deepen your understanding.

### 1. Security Architecture

Draw or describe a diagram showing what protects each sensitive asset in this application. Your answer should address:
- Why is the anon key safe to expose in `config.public.json`?
    - Because our tables use RLS, unauthenticated users can only interact with tables as we permit. The anon key only has limited SELECT access to specific tables, so a malicious actor can't view data besides `page_views`
- What would happen if someone got the service role key?
    - The service role key has unrestricted access to view, edit, create, delete tables etc, which would allow an attacker to read or manipulate any data.
- How do Edge Functions protect the OpenAI API key?
    - They preserve the anonymity of the key by moving code reliant on it to Supabase instead of placing it directly inside browser code.
- What role does Row Level Security play?
    - It allows the DB manager to specify policies for  tables and rows in the database to control who can view and edit data.

### 2. Edge Functions & the "Secure Middle"

Why can't we call OpenAI directly from the browser? Explain the flow: browser → Edge Function → OpenAI. What role does JWT verification play in this chain? How does this pattern apply to other production applications?

    The browser code cannot call OpenAI directly because it does not have access to any OpenAI key.
    
    - Browser creates a Supabase client connection
    - User interacts with an element that calls a Supabase function
    - Supabase receives the request from the client and executes the edge function using an OpenAI key stored within the Supabase project
    - OpenAI verifies the key, executes the requested operation, and returns the result to Supabase
    - Supabase returns the result to the browser client

    When the browser client calls the Supabase function, it has to send a JWT auth token to prove that it has already logged in; Supabase will deny the request without it. This check is implemented to ensure that only authenticated users can use the OpenAI key on Supabase and avoid abuse of my OpenAI resources.

    This pattern allows client code to interact with 3rd party services that rely on sensitive keys without exposing those keys to users.

### 3. From SQL to Semantics

Compare keyword search (SQL `ILIKE`) vs semantic search (vector cosine similarity):
- When would each be better?
    - ILIKE is superior when searching for rows with a column search value that exactly matches at least part of the row value. If I had a number of rows where names are stored as "Dr. Garett Ryan" and "Dr. James Mundo," then I could use ILIKE keyword search for "Dr." and consistently get all the expected rows back.
    - Semantic search is superior when searching for content that is closely related to (but not exactly matching) the query. If I wanted books with prose like Tolkien, a raw DB search with paragraphs from "The Fellowship of the Ring" could *only* ever return Fellowship or books that directly quoted Fellowship. A semantic search, provided with multiple sentences and/or paragraphs from Fellowship could find other books with text similar to Fellowship - depending on how the search is tuned.
- Give a specific query example where one succeeds and the other fails
    - If I query my conference database "Can you explain the meaning of charity?" then I will return 0 results, as that exact phrase does not appear in the content of any talk. However, the semantic search will process that query without issue.
- What makes semantic search "understand" meaning?
    - Semantic search relies on embeddings. Embeddings are numerical representations of text using vectors, often in very high dimensions. The user search query is itself embedded and the resultant vector is compared to the vectors of data stored in the database. The closer two vectors align, the closer the semantic relationship between the search text and the response text.

### 4. RAG vs Fine-Tuning

We used RAG instead of fine-tuning a model on conference talks. Research what fine-tuning is (this wasn't covered in class — go find out!). Then explain:
- What are the trade-offs between RAG and fine-tuning?
    - Fine tuning removes the need to create, maintain, or retrieve data from a database as an intermediate step in the process of handling user requests. A well-trained LLM may also handle semantic questions better - user questions often have "extraneous" text that is not semantically correlated with the desired text. (i.e. inside of the phrase "I want to learn more about how to raise a faithful family," the leading text "I want to learn more about" is mostly semantically irrelevant to the actual topic "(how to) raise a faithful family", and may dilute a RAG search.)
    - RAG removes the need to prepare a dataset and train an expensive model. Developers also have much more control over what content is actually delivered to the user, meaning generally high accuracy and especially fewer false-positive responses from an LLM (hallucination).
- Why did we choose RAG for this application?
    - RAG is well suited to this task because conference talks are a relatively limited dataset to train with (which conversely makes it easier to use search directly), and because students don't have the resources for training a large model.
- When might fine-tuning be the better choice?
    - Big datasets, high available resources
    - Consistent responses are more valued than relying on specific resources (RAG cannot provide an answer if there is no semantically related resource in the database, while an LLM can "fuzz" an answer essentially from scratch that will be similar to its training data.)

### 5. AI-Assisted Development

Briefly describe how your AI coding assistant helped you during this assignment:
- What did it do well?
    - I was particularly impressed with its ability to form and execute plans, as well as its ability to debug issues. I had a problem with the DB search for my custom feature and let the AI tackle it, and it created a robust script for testing different kinds of search queries to determine what the problem was.
- Where did you need to guide it?
    - There was one occasion where I let it loose to generate code for a Supabase function and it also created some extraneous files. I think it was a case of those kinds of files being commonly used in this situation, so the AI assumed it needed to do so here as well.
    - There was another point where the AI wanted to rerun `01_create_schema.py` and I had to tell it that that was both not necessary and probably a bad idea, as I wasn't sure how the script would execute if it wasn't running for the first time on an empty Supabase project etc.
    - When I implemented my custom feature, I pointed out that `Dallin H. Oaks` would be a better search keyword for speakers, because his title may have changed in recent talks versus older talks. I thought it was obvious that this meant I wanted to use `ILIKE`, but the AI still wrote the original DB search using an exact match.
- What did you learn about working with AI tools?
    - As long as you are routinely passing "the ball" between each other and reviewing the code that the AI creates (or wants to create), the AI is capable of pretty complex tasks, including debugging.