-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: For the VECTOR type, you will need to install a PostgreSQL extension like pgvector.
-- Example: CREATE EXTENSION vector;

-- Table for Users (single-user system, but good practice for extensibility)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for Conversations
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    source_platform VARCHAR(255), -- e.g., "ChatGPT", "Bard", "Claude"
    source_id TEXT UNIQUE, -- Original ID from the source platform
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}' -- Flexible storage for additional conversation metadata
);

-- Index on user_id for faster lookup
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);

-- Table for Messages within Conversations
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- e.g., "user", "assistant"
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    token_count INTEGER,
    metadata JSONB DEFAULT '{}' -- Flexible storage for additional message metadata
);

-- Index on conversation_id for faster lookup
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);

-- Table for Embeddings (e.g., for messages or conversation summaries)
CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    embedding VECTOR(1536), -- Example dimension, adjust as needed for the chosen model (e.g., OpenAI ada-002 is 1536)
    model_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Ensure either message_id or conversation_id is present, but not both (or neither)
    CONSTRAINT chk_embedding_target CHECK (
        (message_id IS NOT NULL AND conversation_id IS NULL) OR
        (message_id IS NULL AND conversation_id IS NOT NULL)
    )
);

-- Indexes for embeddings
CREATE INDEX IF NOT EXISTS idx_embeddings_message_id ON embeddings(message_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_conversation_id ON embeddings(conversation_id);

-- Table for User Feedback
CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    feedback_type VARCHAR(50) NOT NULL, -- e.g., "bug", "feature_request", "general"
    message TEXT NOT NULL,
    context JSONB DEFAULT '{}', -- Additional context like conversation_id, message_id, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index on user_id for feedback
CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id);

-- Table for Correlation Results (e.g., storing relationships between conversations/messages)
CREATE TABLE IF NOT EXISTS correlation_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    source_message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    target_conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    target_message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    similarity_score REAL NOT NULL,
    correlation_type VARCHAR(255), -- e.g., "semantic_similarity", "topic_overlap"
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Ensure at least one source and one target is present
    CONSTRAINT chk_correlation_source CHECK (source_conversation_id IS NOT NULL OR source_message_id IS NOT NULL),
    CONSTRAINT chk_correlation_target CHECK (target_conversation_id IS NOT NULL OR target_message_id IS NOT NULL)
);

-- Indexes for correlation results
CREATE INDEX IF NOT EXISTS idx_correlation_source_conv_id ON correlation_results(source_conversation_id);
CREATE INDEX IF NOT EXISTS idx_correlation_source_msg_id ON correlation_results(source_message_id);
CREATE INDEX IF NOT EXISTS idx_correlation_target_conv_id ON correlation_results(target_conversation_id);
CREATE INDEX IF NOT EXISTS idx_correlation_target_msg_id ON correlation_results(target_message_id);

-- Add a trigger to update `updated_at` columns automatically
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_timestamp
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_conversations_timestamp
BEFORE UPDATE ON conversations
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();
