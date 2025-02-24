from rag_pipeline import answer_query, retrieve_docs, llm_model

import streamlit as st

uploaded_file = st.file_uploader("Upload PDF",
                                 type="pdf",
                                 accept_multiple_files=False)




user_query = st.text_area("Enter your prompt: ", height=150 , placeholder= "Ask Anything!")

ask_question = st.button("Ask PDF Reasonoer")

if ask_question:

    if uploaded_file: 

        st.chat_message("user").write(user_query)

      
        retrieved_docs=retrieve_docs(user_query)
        response=answer_query(documents=retrieved_docs, model=llm_model, query=user_query)
      
        st.chat_message("AI PDF Reasoner").write(response)
    
    else:
        st.error("Kindly upload a valid PDF file first!")