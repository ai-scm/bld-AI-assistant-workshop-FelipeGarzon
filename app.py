import streamlit as st # type: ignore
from streamlit_chat import message # type: ignore
import boto3 # type: ignore
import json
import base64
import os
import PyPDF2 # type: ignore
import docx # type: ignore
from dotenv import load_dotenv # type: ignore

# Load environment variables from .env file
load_dotenv()

boto3.Session(profile_name=os.getenv("SESSION"))

# Initialize Bedrock client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN')
)

# Guardrail configuration
GUARDRAIL_ID = "your-guardrail-id"  # Replace with your guardrail ID
GUARDRAIL_VERSION = "DRAFT"  # Or specific version

# System prompt for exam preparation
SYSTEM_PROMPT = """You are an expert AI assistant specialized in helping users prepare for:
1. AWS Certified AI Practitioner exam
2. AWS Certified Cloud Practitioner exam
3. Scrum certifications (PSM, CSM)

Your responsibilities:
- Explain concepts clearly and concisely
- Provide practice questions when asked
- Analyze uploaded study materials and images
- Give exam tips and strategies
- Correct misconceptions
- Stay focused on these certification topics

Always be encouraging and supportive. If asked about topics outside these certifications, 
politely redirect the conversation back to exam preparation. Do not provide information on unrelated subjects.
Be mindful of the user's learning journey and adapt explanations to their level of understanding.
"""

def encode_image(uploaded_file):
    """Encode image to base64 for Bedrock"""
    bytes_data = uploaded_file.getvalue()
    return base64.standard_b64encode(bytes_data).decode('utf-8')

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF file"""
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(uploaded_file):
    """Extract text from DOCX file"""
    doc = docx.Document(uploaded_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_txt(uploaded_file):
    """Extract text from TXT file"""
    return uploaded_file.getvalue().decode('utf-8')

def process_uploaded_file(uploaded_file):
    """Process uploaded file and return content"""
    file_type = uploaded_file.type
    
    if file_type == "application/pdf":
        return extract_text_from_pdf(uploaded_file), "text"
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(uploaded_file), "text"
    elif file_type == "text/plain":
        return extract_text_from_txt(uploaded_file), "text"
    elif file_type in ["image/png", "image/jpeg", "image/gif", "image/webp"]:
        return encode_image(uploaded_file), "image"
    else:
        return None, None

def get_media_type(uploaded_file):
    """Get media type for image"""
    type_mapping = {
        "image/png": "png",
        "image/jpeg": "jpeg",
        "image/gif": "gif",
        "image/webp": "webp"
    }
    return type_mapping.get(uploaded_file.type, "jpeg")

def invoke_bedrock_with_guardrails(messages, image_data=None, image_type=None):
    """Invoke Bedrock with Claude model and guardrails"""
    
    # Build the content for the current message
    content = []
    
    # Add image if present
    if image_data and image_type:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": f"image/{image_type}",
                "data": image_data
            }
        })
    
    # Add text content
    if messages:
        content.append({
            "type": "text",
            "text": messages[-1]["content"] if isinstance(messages[-1]["content"], str) else messages[-1]["content"]
        })
    
    # Build conversation history - ensure alternating roles
    conversation = []
    prev_role = None
    for msg in messages[:-1]:  # All messages except the last one
        # Skip if same role as previous (to ensure alternation)
        if msg["role"] == prev_role:
            # Merge with previous message if same role
            if conversation:
                prev_text = conversation[-1]["content"][0]["text"]
                conversation[-1]["content"][0]["text"] = prev_text + "\n" + msg["content"]
            continue
        conversation.append({
            "role": msg["role"],
            "content": [{"type": "text", "text": msg["content"]}]
        })
        prev_role = msg["role"]
    
    # If last message in history was from user, we need to handle it
    if conversation and conversation[-1]["role"] == "user":
        # Merge current content with last user message
        conversation[-1]["content"].extend(content)
    else:
        # Add current message with potential image
        conversation.append({
            "role": "user",
            "content": content
        })
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "system": SYSTEM_PROMPT,
        "messages": conversation
    }
    
    try:
        # Invoke with guardrails
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",  # Or claude-3-haiku for faster responses
            body=json.dumps(body),
            guardrailIdentifier=GUARDRAIL_ID,
            guardrailVersion=GUARDRAIL_VERSION,
            trace="ENABLED"
        )
        
        response_body = json.loads(response['body'].read())
        
        # Check if guardrail intervened
        if response_body.get('stop_reason') == 'guardrail_intervened':
            return "I apologize, but I cannot respond to that request. Please ask questions related to AWS AI Practitioner, Cloud Practitioner, or Scrum certifications."
        
        return response_body['content'][0]['text']
        
    except Exception as e:
        # Fallback without guardrails if guardrail not configured
        if "guardrail" in str(e).lower():
            try:
                response = bedrock_runtime.invoke_model(
                    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                    body=json.dumps(body)
                )
                response_body = json.loads(response['body'].read())
                return response_body['content'][0]['text']
            except Exception as inner_e:
                return f"Error: {str(inner_e)}"
        return f"Error: {str(e)}"

def invoke_bedrock_simple(messages, image_data=None, image_type=None):
    """Simplified Bedrock invocation without guardrails for testing"""
    
    content = []
    
    if image_data and image_type:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": f"image/{image_type}",
                "data": image_data
            }
        })
    
    # Get the last user message
    last_message = messages[-1]["content"] if messages else ""
    content.append({
        "type": "text",
        "text": last_message
    })
    
    # Build conversation - ensure alternating roles
    conversation = []
    prev_role = None
    for msg in messages[:-1]:
        # Skip if same role as previous (to ensure alternation)
        if msg["role"] == prev_role:
            # Merge with previous message if same role
            if conversation:
                prev_text = conversation[-1]["content"][0]["text"]
                conversation[-1]["content"][0]["text"] = prev_text + "\n" + msg["content"]
            continue
        conversation.append({
            "role": msg["role"],
            "content": [{"type": "text", "text": msg["content"]}]
        })
        prev_role = msg["role"]
    
    # If last message in history was from user, merge content
    if conversation and conversation[-1]["role"] == "user":
        conversation[-1]["content"].extend(content)
    else:
        conversation.append({
            "role": "user",
            "content": content
        })
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "system": SYSTEM_PROMPT,
        "messages": conversation
    }
    
    try:
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps(body)
        )
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.title("🎓 AI Assistant for Cloud and Scrum Exams")

st.markdown("""
Welcome! I'm your AI study companion for:
- **AWS Certified AI Practitioner**
- **AWS Certified Cloud Practitioner**  
- **Scrum Certifications (PSM/CSM)**

Upload study materials or images, and ask me anything!
""")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_content" not in st.session_state:
    st.session_state.uploaded_content = None
if "uploaded_type" not in st.session_state:
    st.session_state.uploaded_type = None

# Sidebar for settings and file upload
with st.sidebar:
    st.header("📁 Upload Study Materials")
    
    uploaded_file = st.file_uploader(
        "Upload a file (PDF, DOCX, TXT, or Image)",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg", "gif", "webp"]
    )
    
    if uploaded_file:
        content, content_type = process_uploaded_file(uploaded_file)
        if content:
            st.session_state.uploaded_content = content
            st.session_state.uploaded_type = content_type
            if content_type == "image":
                st.session_state.image_media_type = get_media_type(uploaded_file)
                st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
            else:
                st.success(f"✅ File processed: {uploaded_file.name}")
                with st.expander("Preview content"):
                    st.text(content[:500] + "..." if len(content) > 500 else content)
        else:
            st.error("Unsupported file type")
    
    if st.button("Clear uploaded content"):
        st.session_state.uploaded_content = None
        st.session_state.uploaded_type = None
        st.rerun()
    
    st.divider()
    
    st.header("⚙️ Settings")
    use_guardrails = st.checkbox("Enable Guardrails", value=False, 
                                  help="Enable AWS Bedrock Guardrails for content filtering")
    
    st.divider()
    
    st.header("📚 Quick Topics")
    topic = st.selectbox("Select a topic to explore:", [
        "Choose a topic...",
        "AWS AI Services Overview",
        "Machine Learning Fundamentals",
        "AWS Cloud Concepts",
        "AWS Security & Compliance",
        "Scrum Framework",
        "Scrum Roles & Events",
        "Practice Questions"
    ])
    
    if topic != "Choose a topic..." and st.button("Ask about this topic"):
        topic_prompts = {
            "AWS AI Services Overview": "Can you explain the main AWS AI services I need to know for the AI Practitioner exam?",
            "Machine Learning Fundamentals": "What are the key machine learning concepts covered in the AWS AI Practitioner exam?",
            "AWS Cloud Concepts": "Explain the core cloud concepts I need for the Cloud Practitioner exam.",
            "AWS Security & Compliance": "What security and compliance topics are important for the Cloud Practitioner exam?",
            "Scrum Framework": "Explain the Scrum framework and its key components.",
            "Scrum Roles & Events": "What are the Scrum roles and events I need to know for certification?",
            "Practice Questions": "Give me 3 practice questions covering AWS AI, Cloud, and Scrum topics."
        }
        st.session_state.messages.append({"role": "user", "content": topic_prompts[topic]})
        st.session_state.pending_response = True  # Flag to trigger model invocation
        st.rerun()

# Display chat history
for i, msg in enumerate(st.session_state.messages):
    message(msg["content"], is_user=(msg["role"] == "user"), key=f"msg_{i}")

# Chat input
user_input = st.chat_input("Ask me about AWS AI, Cloud Practitioner, or Scrum...")

if user_input:
    # Add context from uploaded file if available
    full_message = user_input
    if st.session_state.uploaded_content and st.session_state.uploaded_type == "text":
        full_message = f"Based on this study material:\n\n{st.session_state.uploaded_content[:3000]}\n\nUser question: {user_input}"
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.pending_response = True  # Flag to trigger model invocation
    st.session_state.pending_full_message = full_message
    st.rerun()

# Process pending response (after rerun so message displays first)
if st.session_state.get("pending_response", False):
    # Prepare image data if available
    image_data = None
    image_type = None
    if st.session_state.uploaded_content and st.session_state.uploaded_type == "image":
        image_data = st.session_state.uploaded_content
        image_type = st.session_state.get("image_media_type", "jpeg")
    
    # Build messages for API
    api_messages = st.session_state.messages.copy()
    if st.session_state.uploaded_content and st.session_state.uploaded_type == "text":
        full_message = st.session_state.get("pending_full_message", api_messages[-1]["content"])
        api_messages[-1] = {"role": "user", "content": full_message}
    
    # Get response from Bedrock
    with st.spinner("Thinking..."):
        if use_guardrails:
            response = invoke_bedrock_with_guardrails(api_messages, image_data, image_type)
        else:
            response = invoke_bedrock_simple(api_messages, image_data, image_type)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.pending_response = False
    st.session_state.pending_full_message = None
    st.rerun()

# Clear chat button
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()