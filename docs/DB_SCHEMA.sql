-- docs/DB_SCHEMA.sql
-- PostgreSQL 15 Schema for NexusKnowledge Project

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table for storing raw ingested data
CREATE TABLE IF NOT EXISTS raw_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type VARCHAR(50) NOT NULL, -- e.g., 'deepseek_chat', 'deepthink', 'grok_chat'
    source_id VARCHAR(255), -- Original ID from the source system
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'INGESTED' -- e.g., 'INGESTED', 'NORMALIZED', 'FAILED'
);

-- Table for storing normalized conversation turns
CREATE TABLE IF NOT EXISTS conversation_turns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    raw_data_id UUID REFERENCES raw_data(id) ON DELETE SET NULL,
    conversation_id UUID NOT NULL,
    turn_index INT NOT NULL,
    speaker VARCHAR(50) NOT NULL,
    text TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE (conversation_id, turn_index)
);

-- Table for storing analyzed entities (e.g., persons, organizations, topics)
CREATE TABLE IF NOT EXISTS entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_turn_id UUID REFERENCES conversation_turns(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- e.g., 'PERSON', 'ORG', 'TOPIC'
    value TEXT NOT NULL,
    sentiment VARCHAR(20), -- e.g., 'POSITIVE', 'NEGATIVE', 'NEUTRAL'
    relevance FLOAT,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Table for storing relationships between entities or turns
CREATE TABLE IF NOT EXISTS relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
    target_entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- e.g., 'MENTIONS', 'RELATES_TO', 'DISCUSSES'
    strength FLOAT,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Table for storing user feedback
CREATE TABLE IF NOT EXISTS user_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feedback_type VARCHAR(50) NOT NULL, -- e.g., 'bug', 'feature_request', 'general'
    message TEXT NOT NULL,
    user_id UUID, -- Optional, if user is authenticated
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'NEW' -- e.g., 'NEW', 'REVIEWED', 'RESOLVED'
);

-- Table for storing MLflow experiment run details (simplified representation)
CREATE TABLE IF NOT EXISTS mlflow_runs (
    run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id VARCHAR(255) NOT NULL,
    run_name VARCHAR(255),
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50),
    params JSONB DEFAULT '{}'::jsonb,
    metrics JSONB DEFAULT '{}'::jsonb,
    artifacts_uri TEXT
);

-- Table for DVC-versioned data assets (metadata only)
CREATE TABLE IF NOT EXISTS dvc_data_assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_name VARCHAR(255) NOT NULL UNIQUE,
    path TEXT NOT NULL,
    latest_version VARCHAR(255),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_raw_data_source_type ON raw_data(source_type);
CREATE INDEX IF NOT EXISTS idx_raw_data_status ON raw_data(status);
CREATE INDEX IF NOT EXISTS idx_conversation_turns_conversation_id ON conversation_turns(conversation_id);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
CREATE INDEX IF NOT EXISTS idx_entities_value ON entities(value);
CREATE INDEX IF NOT EXISTS idx_user_feedback_type ON user_feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_mlflow_runs_experiment_id ON mlflow_runs(experiment_id);
