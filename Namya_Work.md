# Namya's Work — Streamlit Functions and Their Uses

> **Module Owner:** Namya  
> **Role:** Streamlit UI, file handling, and backend input preparation

---

## What this module does

This part of the project sits between the user and Sarthak's backend. It takes the text the user types, extracts text from uploaded PDF and DOCX files, combines everything into one input string, sends that string to the backend, and shows the returned response in the Streamlit chat UI.

In simple words: this file prepares the input, calls the backend, and displays the answer.

---

## Function table

-------------------------------------------------------------------------------
Function name                  | Use
-------------------------------------------------------------------------------
get_backend_result(user_text)  | Sends the combined text to Sarthak's backend
                                              | and returns a clean response dictionary.

                                              | What it does:
                                              | - imports ai_brain_app from sarthak_brain.py
                                              | - returns an error dictionary if import fails
                                              | - calls ai_brain_app.invoke({"pdf_text": user_text})
                                              | - returns status, final_report, retry_count,
                                              |   and error_message

                                              | Why it exists:
                                              | - keeps backend errors inside one function
                                              | - gives the UI one simple response shape
                                              | - lets the page show either the report or the error

-------------------------------------------------------------------------------
extract_pdf_text(uploaded_file) | Reads text out of uploaded PDF files.

                                              | What it does:
                                              | - wraps the uploaded file bytes with io.BytesIO
                                              | - opens the file using PdfReader
                                              | - loops through every page in the PDF
                                              | - extracts text from each page
                                              | - removes empty pages
                                              | - joins all page text into one string

                                              | Why it exists:
                                              | - Streamlit uploads a PDF as a file object
                                              | - Sarthak's backend needs plain text

-------------------------------------------------------------------------------
extract_docx_text(uploaded_file)| Reads text out of uploaded DOCX files.

                                              | What it does:
                                              | - opens the DOCX file like a zip archive
                                              | - reads word/document.xml
                                              | - parses the XML using ElementTree
                                              | - finds each paragraph
                                              | - collects text from each paragraph
                                              | - joins all paragraphs into one string

                                              | Why it exists:
                                              | - DOCX files are not plain text files
                                              | - the backend only understands plain text

-------------------------------------------------------------------------------
build_backend_input(user_text,  | Combines the user's typed message and uploaded
uploaded_files)                | file text into one backend input string.

                                              | What it does:
                                              | - starts with an empty list called chunks
                                              | - adds the user's typed text if it is not blank
                                              | - loops through every uploaded file
                                              | - uses extract_pdf_text for .pdf files
                                              | - uses extract_docx_text for .docx files
                                              | - ignores other file types
                                              | - catches extraction errors and turns them into
                                              |   a readable note
                                              | - adds the extracted file text with a label
                                              |   like FILE: filename
                                              | - joins everything together with --- separators

                                              | Why it exists:
                                              | - the backend should receive one clean block
                                              |   of text
                                              | - it keeps the user text and file text together
                                              |   in a predictable format
                                              | - it makes file uploads useful instead of
                                              |   just being stored in the UI

-------------------------------------------------------------------------------
render_message(message)        | Shows one saved chat message in the Streamlit
                                              | chat UI.

                                              | What it does:
                                              | - opens a chat bubble using st.chat_message
                                              | - displays the message content with st.markdown
                                              | - checks whether the message has uploaded files
                                              | - shows an Uploaded files caption if files exist
                                              | - prints the file name and size for each file

                                              | Why it exists:
                                              | - keeps the chat history readable
                                              | - makes user uploads visible in the conversation

-------------------------------------------------------------------------------
render_backend_result(result)  | Shows the response returned by Sarthak's backend.

                                              | What it does:
                                              | - reads status, final_report, retry_count,
                                              |   and error_message
                                              | - shows a Backend Response heading
                                              | - shows a short status line
                                              | - displays the final_report if it exists
                                              | - displays the error_message if no report exists
                                              | - shows a warning if neither exists

                                              | Why it exists:
                                              | - keeps backend output separate from chat
                                              | - makes errors easier to see
                                              | - gives the UI one place to render results

-------------------------------------------------------------------------------

---

## How the functions work together

text
User types text or uploads files
   ↓
build_backend_input()
   ↓
get_backend_result()
   ↓
render_backend_result()
   ↓
render_message() keeps the chat visible
```

---

## How the Streamlit page uses these functions

* `st.session_state.messages` stores the chat history
* `st.session_state.last_result` stores the latest backend response
* `st.chat_input(...)` collects new text and file uploads
* `build_backend_input(...)` prepares the input for the backend
* `get_backend_result(...)` sends the prepared input to Sarthak's backend
* `render_message(...)` shows previous messages
* `render_backend_result(...)` shows the backend output in a bordered box

---

## What is still blocked

* The page can run and the UI can be tested.
* Full backend analysis still depends on the Google API key for `sarthak_brain.py`.

---

## What I have already built

* chat UI with session state
* PDF text extraction
* DOCX text extraction
* combined backend input builder
* backend result rendering
* loading spinner during backend calls


