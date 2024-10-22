-- Initialize content_type enum
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'content_type') THEN
        CREATE TYPE content_type AS ENUM (
            'web_article', 'youtube_video', 'publication', 'bookmark', 'unknown'
        );
    END IF;
END $$;

-- Create or update the content table
CREATE TABLE IF NOT EXISTS content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url VARCHAR(2048) UNIQUE NOT NULL,
    content_type content_type NOT NULL,
    title TEXT,
    image_url VARCHAR(2048),
    description TEXT,
    summary TEXT,
    metadata JSONB,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP
);

-- Create index for URL
CREATE INDEX IF NOT EXISTS idx_content_url ON content (url);

-- Optional: Create trigram index on title
-- CREATE INDEX IF NOT EXISTS idx_content_title_trgm ON content USING gin (title gin_trgm_ops);

