import streamlit as st
import requests
import json

st.set_page_config(page_title="Agent Chat - Simple Streaming", layout="centered")
st.set_page_config(layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Multi-Agent Sequential Socket Streaming")
st.markdown("Hi there! 👋 &mdash; Watch each agent work in real-time!")

with st.sidebar:
    st.markdown("🌎 **Multi-Agent Pipeline**")
    
    # Show session info if available
    if "current_session_id" in st.session_state:
        st.markdown("---")
        st.markdown("**Session Info:**")
        st.text(f"User: {st.session_state.get('current_user_id', 'default_user')}")
        st.text(f"Session: {st.session_state.current_session_id}")
    
    # Create a placeholder for dynamic session info during streaming
    session_info_placeholder = st.empty()
    
    # Create a placeholder for loading indicator
    sidebar_loading_placeholder = st.empty()
    
    # Add clear chat button
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        # Clear all chat messages
        st.session_state.messages = []
        # Clear session info
        if "current_session_id" in st.session_state:
            del st.session_state.current_session_id
        if "current_user_id" in st.session_state:
            del st.session_state.current_user_id
        st.rerun()

# Display chat history
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "system":
        with st.chat_message("system", avatar="ai"):
            st.write(msg["content"])
    else:
        # For assistant messages with agent steps
        if "agent_steps" in msg:
            st.markdown("### Agent Pipeline Results:")
            for step in msg["agent_steps"]:
                status_icon = "✅" if step["is_final"] else "🔄"
                step_type = "Final Result" if step["is_final"] else "Working"
                with st.expander(f"{status_icon} {step['agent']} ({step_type})", expanded=step["is_final"]):
                    st.markdown(step["content"])
        else:
            with st.expander(f"Assistant Response {i//2 + 1}", expanded=False):
                st.markdown(msg["content"])

user_query = st.chat_input("Ask anything...")

if user_query:
    st.chat_message("user").markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Create containers for live updates
    loading_container = st.empty()
    status_container = st.empty()
    pipeline_container = st.empty()
    
    try:
        # Show loading spinner in sidebar
        with sidebar_loading_placeholder:
            st.markdown("---")
            st.markdown("**Status:**")
            # Use st.status for a nice animated indicator
            status_element = st.status("Agents working...", expanded=False, state="running")
        
        # Show simple loading indicator
        loading_container.info("🔄 Agents processing your request...")
        status_container.info("🚀 Starting agent pipeline...")
        
        # Simple streaming request
        response = requests.post(
            "http://localhost:8001/ask_stream",
            json={"query": user_query},
            stream=True
        )
        response.raise_for_status()
        
        agent_steps = []
        
        # Process streaming JSON chunks
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    chunk = json.loads(line)
                    
                    if "error" in chunk:
                        status_container.error(f"❌ Error: {chunk['error']}")
                        break
                    
                    # Capture session info on first chunk and update sidebar
                    if "session_id" in chunk and "current_session_id" not in st.session_state:
                        st.session_state.current_session_id = chunk["session_id"]
                        st.session_state.current_user_id = "default_user"  # Could be made dynamic later
                        # Update the sidebar placeholder with session info
                        with session_info_placeholder.container():
                            st.markdown("---")
                            st.markdown("**Active Session:**")
                            st.text(f"User: default_user")
                            st.text(f"Session: {chunk['session_id']}")
                    
                    # Store the step
                    agent_steps.append({
                        "agent": chunk["agent"],
                        "content": chunk["content"],
                        "is_final": chunk["is_final"]
                    })
                    
                    # Update status - only if we have the required keys
                    if "agent" in chunk and "is_final" in chunk:
                        if chunk["is_final"]:
                            status_container.success(f"✅ {chunk['agent']} completed!")
                        else:
                            status_container.info(f"🔄 {chunk['agent']} working...")
                    
                    # Live update display
                    with pipeline_container.container():
                        st.markdown("### 🔄 Live Agent Pipeline:")
                        for step in agent_steps:
                            status_icon = "✅" if step["is_final"] else "🔄"
                            step_type = "Completed" if step["is_final"] else "Working"
                            with st.expander(f"{status_icon} {step['agent']} ({step_type})", expanded=True):
                                st.markdown(step["content"])
                
                except json.JSONDecodeError:
                    continue
        
        # Store final results in session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Pipeline completed",
            "agent_steps": agent_steps
        })
        
        # Clear temporary containers and loading indicator
        sidebar_loading_placeholder.empty()  # Clear sidebar loading indicator
        loading_container.empty()  # Clear loading indicator
        status_container.success("🎊 All agents completed!")
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        sidebar_loading_placeholder.empty()  # Clear sidebar loading indicator on error
        loading_container.empty()  # Clear loading indicator on error
        status_container.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})