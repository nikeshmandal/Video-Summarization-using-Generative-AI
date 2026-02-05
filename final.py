
import streamlit as st
from videoSuggestion import suggest_best_video
from transcriptExtraction import extract_transcript_details
from Notes.notesPdfNDoc import extract_pdf_text,create_notes_from_transcript,save_notes_as_docx,save_notes_as_pdf,get_pdf_answer
import requests

st.markdown("""
    <style>
        /* Style the entire sidebar container */
        .stAppDeployButton,.stSidebarHeader, .stMainMenu{
            display: none;  
        }
    </style>
""", unsafe_allow_html=True)

st.title("Smart Education")


st.sidebar.header("Choose an option")
sidebar_option = st.sidebar.radio("",["Comparison", "Summarize & Create Note", "PDF Q&A"])

if sidebar_option == "Comparison":
    st.header("Compare Multiple YouTube Videos")
    
    user_query = st.text_area("What do you want to learn or know about?")

    youtube_links = st.text_area("Enter YouTube Video Links (comma separated):")

    if st.button("Compare"):
        if youtube_links:
            youtube_links_list = youtube_links.split(",")
            if len(youtube_links_list) < 2:
                st.error("Please enter at least two video links to compare.")
            else:
                summaries = []
                for youtube_link in youtube_links_list:
                    youtube_link = youtube_link.strip() 
                    transcript_text = extract_transcript_details(youtube_link)

                    if transcript_text:
                        try:
                            req = requests.post(
                                "http://localhost:8000/api/comp",
                                json={"message": transcript_text}
                            )
                            data = req.json()
                            summary=data['reply']    
                        except Exception as e:
                            st.error(f"Error contacting backend:")
                        if summary:
                            video_id = youtube_link.split("=")[1]
                            video_thumb_url = f"http://img.youtube.com/vi/{video_id}/0.jpg"

                            summaries.append({
                                'url': youtube_link,
                                'summary': summary,
                                'thumbnail': video_thumb_url
                            })
                    else:
                        st.error(f"Could not extract transcript for the video: {youtube_link}")

                if summaries:
                    st.markdown("## Video Comparison:")
                    for idx, summary in enumerate(summaries):
                        st.subheader(f"Video {idx + 1}")
                        st.image(summary['thumbnail'], use_container_width=True)
                        st.write(summary['summary'])

                    best_video = suggest_best_video(summaries, user_query)

                    if best_video:
                        st.markdown("## Recommended Video to Watch:")
                        st.image(best_video['thumbnail'], use_container_width=True)
                        st.write(f"**Reason**: This video is the best choice based on its detailed summary and relevance to your learning goals.")
                    else:
                        st.markdown("## No Relevant Videos Found")
                        st.write("None of the videos seem to match your learning request. You might want to try different videos.")
                else:
                    st.error("No summaries available to compare.")
        else:
            st.error("Please enter valid YouTube video URLs.")



elif sidebar_option == "Summarize & Create Note":
    st.header("Summarize a Single YouTube Video")

    single_video_link = st.text_input("Enter a YouTube Video Link:")

    if 'conversationsum' not in st.session_state:
        st.session_state.conversationsum = []

    if 'summary' not in st.session_state:
        st.session_state.summary = ""

    if 'video_thumb_url' not in st.session_state:
        st.session_state.video_thumb_url = ""

    if 'transcript_text' not in st.session_state:
        st.session_state.transcript_text = ""
    
    col1,col2=st.columns([4,10])

    
    with col1:
        sum=st.button("Summarize This Video")
    with col2:
        gen=st.button("Generate Notes")

    if sum:
        transcript_text = extract_transcript_details(single_video_link)

        if transcript_text:
            st.session_state.transcript_text = transcript_text

            try:
                req = requests.post(
                    "http://localhost:8000/api/sum",
                    json={"message": transcript_text}
                )
                data = req.json()
                summary=data['reply']    
            except Exception as e:
                st.error("Error contacting backend: ")

            if summary:
                video_id = single_video_link.split("=")[-1]
                video_thumb_url = f"http://img.youtube.com/vi/{video_id}/0.jpg"
                
                st.session_state.summary = summary
                st.session_state.video_thumb_url = video_thumb_url

            else:
                st.error("Error generating the summary.")
        else:
            st.error(f"Could not extract transcript for the video: {single_video_link}")
    

    if gen:
        if single_video_link:
            transcript_text = extract_transcript_details(single_video_link)
            video_id = single_video_link.split("=")[-1]  
            video_thumb_url = f"http://img.youtube.com/vi/{video_id}/0.jpg"
            if transcript_text:

                st.session_state.conversationsum = []
                st.session_state.summary = ""
                st.session_state.video_thumb_url = ""

                notes = create_notes_from_transcript(transcript_text)

                st.subheader("Generated Notes:")
                st.image(video_thumb_url, use_container_width=True)

                st.write(notes)

                st.subheader("Download Notes as:")

                pdf_button = st.download_button(
                    label="Download as PDF",
                    data=save_notes_as_pdf(notes).getvalue(),
                    file_name="notes.pdf",
                    mime="application/pdf"
                )

                docx_button = st.download_button(
                    label="Download as DOCX",
                    data=save_notes_as_docx(notes).getvalue(),
                    file_name="notes.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )


    if st.session_state.video_thumb_url and st.session_state.summary:
        st.subheader("Summary:")
        st.image(st.session_state.video_thumb_url, use_container_width=True)
        st.write(st.session_state.summary)

 
    # Display the question input section after the summary is displayed
    if st.session_state.summary: 
        if 'question' not in st.session_state:
            st.session_state.question = ""

        question = st.text_input("Ask a question about the video content:")

        if question:
            st.session_state.question = question

            answer = get_pdf_answer(st.session_state.transcript_text, question)

            if answer:
                st.session_state.conversationsum.append({"question": question, "answer": answer})

                st.markdown("<hr>", unsafe_allow_html=True)
    
            else:
                st.error("Sorry, could not generate an answer.")


    for qna in reversed(st.session_state.conversationsum):
        st.write(f"**Question:** {qna['question']}")
        st.write(f"**Answer:** {qna['answer']}")
        st.markdown("<hr>", unsafe_allow_html=True)




elif sidebar_option == "PDF Q&A":
    st.header("Ask Questions About a PDF Document")

    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    question_input = st.empty()

    if uploaded_file:
        pdf_text = extract_pdf_text(uploaded_file)

        st.write("**PDF Content Extracted Successfully**")
        if pdf_text:

            # Initialize session state for conversation
            if "conversation" not in st.session_state:
                st.session_state.conversation = []
 
            question = st.text_input("Ask a question about the PDF:")

            if question:
                answer = get_pdf_answer(pdf_text, question)

                if answer:
                    st.session_state.conversation.append({"question": question, "answer": answer})

                    st.markdown("<hr>", unsafe_allow_html=True)

                else:
                    st.error("Sorry, could not generate an answer.")
            for qna in reversed(st.session_state.conversation):
                st.write(f"**Question:** {qna['question']}")
                st.write(f"**Answer:** {qna['answer']}")
                st.markdown("<hr>", unsafe_allow_html=True) 

        else:
            st.error("Could not extract text from the uploaded PDF.")
