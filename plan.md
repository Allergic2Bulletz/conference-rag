## Plan: Add Oaks-Specific RAG Feature

Add a new RAG panel that returns AI-generated answers based only on talks by Dallin H. Oaks. This feature will mirror the existing RAG functionality but filter database results to a single speaker.

**TL;DR**: Create a speaker-filtered database function, add a fourth UI panel, and wire up the frontend logic to call the filtered search. All existing edge functions (`embed-question`, `generate-answer`) can be reused without modification.

**Steps**

- [x] 1. **Create new database function** — Add `match_sentences_by_speaker` function directly to Supabase
   - **Priority**: Execute SQL directly via Supabase SQL Editor or Python script (do NOT rerun entire `01_create_schema.py`)
   - Function signature: `match_sentences_by_speaker(query_embedding vector(1536), speaker_name text, match_count int DEFAULT 20)`
   - Add WHERE clause to filter: `WHERE sentence_embeddings.speaker = speaker_name`
   - Returns same columns as `match_sentences`: id, talk_id, title, speaker, text, similarity
   - **Optional**: Update [scripts/01_create_schema.py](scripts/01_create_schema.py) for documentation/replicability (after line 129)

- [x] 2. **Add UI panel to index.html** (*parallel with step 1*)
   - Insert new search panel after existing `rag-panel` (around line 148)
   - Structure: header with title "🎤 Ask Dallin H. Oaks (RAG)", status badge, input field, button
   - IDs: `oaks-panel`, `oaks-status`, `oaks-input`, `oaks-btn`, `oaks-results`
   - Copy structure from existing `rag-panel` div block

- [x] 3. **Add frontend logic in app.js** (*depends on steps 1-2*)
   - Add DOM element references for new panel around line 83 (input, button, results, status)
   - Create `askOaksQuestion()` async function after line 586 (similar to `askQuestion()`)
   - Modify call to invoke `match_sentences_by_speaker` RPC with `speaker_name: 'Dallin H. Oaks'`
   - Reuse existing helper functions: `getEmbedding()`, `groupByTalk()`, `fetchFullTalkText()`, `generateAnswer()`
   - Add event listeners around line 750 for button click and Enter key press
   - Update `checkSearchReadiness()` around line 340 to include readiness check for Oaks panel

- [x] 4. **Update CSS (if needed)** (*parallel with step 3*)
   - Verify existing `.search-panel` styles work for fourth panel
   - Current CSS uses reusable classes, so likely minimal or no changes needed
   - Add distinguishing styles only if desired (e.g., different accent color)

- [ ] 5. **Test feature** (*depends on steps 1-4*)
   - Verify database function deploys successfully via Python script
   - Check UI panel renders correctly and status badge shows readiness
   - Test with Oaks-specific question and verify only his talks appear in sources
   - Confirm error handling for edge cases

**Relevant Files**

- **Supabase SQL Editor** — Execute SQL to create `match_sentences_by_speaker` function directly in database
- [scripts/01_create_schema.py](scripts/01_create_schema.py) — (Optional) Add function for documentation at line 113-129 within `schema_sql` string
- [index.html](index.html) — Insert new panel after line 148 (after `rag-panel` closing div)
- [app.js](app.js) — Add DOM references (line 83), `askOaksQuestion()` function (after line 586), event listeners (line 750), update `checkSearchReadiness()` (line 340)
- [styles.css](styles.css) — Existing styles should work; only modify if custom styling desired

**Verification**

1. Verify database function exists: Query Supabase SQL Editor or test RPC call from browser console
2. Check browser console for JavaScript errors on page load
3. Verify "🎤 Ask Dallin H. Oaks (RAG)" panel shows "🟢 Ready" status after login
4. Test query: "What does President Oaks teach about freedom?" and verify all source talks show "Dallin H. Oaks" as speaker
5. Test edge case: graceful handling if database has no Oaks talks

**Decisions**

- **Speaker name filtering**: Using exact match `speaker = 'Dallin H. Oaks'` in SQL WHERE clause
- **Scope**: Only adding Oaks-specific feature; not creating generalized "filter by speaker" system
- **Code reuse**: Leveraging existing edge functions (`embed-question`, `generate-answer`) and helper functions; no backend changes
- **UI placement**: Fourth panel below existing RAG panel, maintaining consistent layout
- **Excluded**: Generalizing to other speakers, adding dropdown selector, modifying existing panels

**Further Considerations**

1. **Speaker name variations**: If "Dallin H. Oaks" doesn't match all records (e.g., "President Dallin H. Oaks"), should we use SQL LIKE pattern matching? **Recommendation**: Start with exact match, test with actual data, and adjust if needed.
2. **Empty results handling**: Should we fall back to general search if no Oaks talks match, or show "No results"? **Recommendation**: Show "No matching talks found" message for clarity.
3. **Panel ordering**: Should Oaks panel be positioned differently? **Recommendation**: Keep after RAG panel to maintain feature progression.
