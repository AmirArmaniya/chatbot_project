import os
import json
import logging
import requests
import jwt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')
app.config['RASA_URL'] = os.environ.get('RASA_URL', 'http://rasa:5005')
app.config['DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///data/chatbot.db')

# Initialize SQLAlchemy
Base = declarative_base()

# Define SQLAlchemy models
class Tenant(Base):
    __tablename__ = 'tenants'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    api_key = Column(String(100), nullable=False)
    config = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversations = relationship("Conversation", back_populates="tenant")
    
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False)
    tenant_id = Column(Integer, ForeignKey('tenants.id'))
    name = Column(String(100), nullable=True)
    metadata = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversations = relationship("Conversation", back_populates="user")
    
class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(String(100), unique=True, nullable=False)
    tenant_id = Column(Integer, ForeignKey('tenants.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="conversations")
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")
    
class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    sender = Column(String(10), nullable=False)  # 'user' or 'bot'
    content = Column(Text, nullable=False)
    intent = Column(String(100), nullable=True)
    confidence = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")

# Create database engine and tables
engine = create_engine(app.config['DATABASE_URI'])
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Load tenant configurations from CSV
def load_tenants():
    try:
        tenant_file = 'data/tenants.csv'
        if os.path.exists(tenant_file):
            df = pd.read_csv(tenant_file)
            
            session = Session()
            for _, row in df.iterrows():
                tenant = session.query(Tenant).filter_by(tenant_id=row['tenant_id']).first()
                if not tenant:
                    tenant = Tenant(
                        tenant_id=row['tenant_id'],
                        name=row['name'],
                        api_key=generate_password_hash(row['api_key']),
                        config=row.get('config', '{}')
                    )
                    session.add(tenant)
            
            session.commit()
            session.close()
            logger.info("Tenants loaded successfully")
        else:
            logger.warning(f"Tenant file {tenant_file} not found")
    except Exception as e:
        logger.error(f"Error loading tenants: {str(e)}")

# JWT token functions
def generate_token(tenant_id):
    """Generate JWT token for tenant authentication"""
    payload = {
        'tenant_id': tenant_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Authentication decorator
def token_required(f):
    def decorated(*args, **kwargs):
        token = None
        
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token!'}), 401
        
        return f(payload, *args, **kwargs)
    
    decorated.__name__ = f.__name__
    return decorated

# API key authentication decorator
def api_key_required(f):
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        tenant_id = request.headers.get('X-Tenant-ID')
        
        if not api_key or not tenant_id:
            return jsonify({'error': 'API key or tenant ID is missing!'}), 401
        
        session = Session()
        tenant = session.query(Tenant).filter_by(tenant_id=tenant_id).first()
        session.close()
        
        if not tenant or not check_password_hash(tenant.api_key, api_key):
            return jsonify({'error': 'Invalid API key or tenant ID!'}), 401
        
        return f(tenant_id, *args, **kwargs)
    
    decorated.__name__ = f.__name__
    return decorated

# Initialize the app with tenant data
@app.before_first_request
def initialize_app():
    load_tenants()

# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    rasa_health = False
    try:
        rasa_response = requests.get(f"{app.config['RASA_URL']}/status")
        if rasa_response.status_code == 200:
            rasa_health = True
    except:
        pass
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'rasa_status': rasa_health
    })

@app.route('/auth', methods=['POST'])
@api_key_required
def authenticate(tenant_id):
    """Authenticate tenant and get JWT token"""
    token = generate_token(tenant_id)
    return jsonify({'token': token})

@app.route('/webhook', methods=['POST'])
@token_required
def webhook(payload):
    """Webhook endpoint for receiving messages from external platforms"""
    tenant_id = payload.get('tenant_id')
    data = request.json
    
    if not data or 'user_id' not in data or 'message' not in data:
        return jsonify({'error': 'Invalid payload'}), 400
    
    user_id = data['user_id']
    message_text = data['message']
    conversation_id = data.get('conversation_id')
    
    # Get or create conversation
    session = Session()
    
    tenant = session.query(Tenant).filter_by(tenant_id=tenant_id).first()
    if not tenant:
        session.close()
        return jsonify({'error': 'Invalid tenant'}), 400
    
    user = session.query(User).filter_by(user_id=user_id, tenant_id=tenant.id).first()
    if not user:
        user = User(user_id=user_id, tenant_id=tenant.id)
        session.add(user)
        session.flush()
    
    if not conversation_id:
        # Create new conversation
        conversation = Conversation(
            conversation_id=f"{tenant_id}_{user_id}_{datetime.utcnow().timestamp()}",
            tenant_id=tenant.id,
            user_id=user.id
        )
        session.add(conversation)
        session.flush()
    else:
        conversation = session.query(Conversation).filter_by(conversation_id=conversation_id).first()
        if not conversation or conversation.tenant_id != tenant.id:
            session.close()
            return jsonify({'error': 'Invalid conversation ID'}), 400
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        sender='user',
        content=message_text
    )
    session.add(user_message)
    session.commit()
    
    # Send message to Rasa
    try:
        rasa_payload = {
            "sender": user_id,
            "message": message_text,
            "metadata": {
                "tenant_id": tenant_id
            }
        }
        
        rasa_response = requests.post(
            f"{app.config['RASA_URL']}/webhooks/rest/webhook",
            json=rasa_payload
        )
        
        if rasa_response.status_code == 200:
            bot_responses = rasa_response.json()
            
            responses = []
            for bot_response in bot_responses:
                if 'text' in bot_response:
                    # Save bot message
                    bot_message = Message(
                        conversation_id=conversation.id,
                        sender='bot',
                        content=bot_response['text']
                    )
                    session.add(bot_message)
                    responses.append(bot_response)
            
            session.commit()
            session.close()
            
            return jsonify({
                'conversation_id': conversation.conversation_id,
                'responses': responses
            })
        else:
            session.close()
            return jsonify({'error': 'Failed to get response from Rasa'}), 500
    
    except Exception as e:
        session.rollback()
        session.close()
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/conversations', methods=['GET'])
@token_required
def get_conversations(payload):
    """Get list of conversations for a tenant"""
    tenant_id = payload.get('tenant_id')
    
    session = Session()
    tenant = session.query(Tenant).filter_by(tenant_id=tenant_id).first()
    
    if not tenant:
        session.close()
        return jsonify({'error': 'Invalid tenant'}), 400
    
    conversations = session.query(Conversation).filter_by(tenant_id=tenant.id).all()
    
    result = []
    for conversation in conversations:
        result.append({
            'conversation_id': conversation.conversation_id,
            'user_id': conversation.user.user_id,
            'status': conversation.status,
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat()
        })
    
    session.close()
    return jsonify({'conversations': result})

@app.route('/conversations/<conversation_id>/messages', methods=['GET'])
@token_required
def get_conversation_messages(payload, conversation_id):
    """Get messages for a specific conversation"""
    tenant_id = payload.get('tenant_id')
    
    session = Session()
    tenant = session.query(Tenant).filter_by(tenant_id=tenant_id).first()
    
    if not tenant:
        session.close()
        return jsonify({'error': 'Invalid tenant'}), 400
    
    conversation = session.query(Conversation).filter_by(
        conversation_id=conversation_id, 
        tenant_id=tenant.id
    ).first()
    
    if not conversation:
        session.close()
        return jsonify({'error': 'Conversation not found'}), 404
    
    messages = session.query(Message).filter_by(conversation_id=conversation.id).all()
    
    result = []
    for message in messages:
        result.append({
            'id': message.id,
            'sender': message.sender,
            'content': message.content,
            'intent': message.intent,
            'confidence': message.confidence,
            'created_at': message.created_at.isoformat()
        })
    
    session.close()
    return jsonify({'messages': result})

# Main entry point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)