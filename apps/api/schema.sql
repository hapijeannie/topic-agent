CREATE TABLE public.articles (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_namespace text NOT NULL,
    source_id text NOT NULL,
    ownership text NOT NULL CHECK (ownership IN ('owned', 'reference')),
    title text NOT NULL,
    source_path text NOT NULL,
    raw text NOT NULL,
    body text NOT NULL,
    metadata jsonb NOT NULL,
    content_hash text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (source_namespace, source_id)
);

CREATE TABLE public.chunks (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    article_id bigint NOT NULL REFERENCES public.articles(id),
    chunk_index integer NOT NULL CHECK (chunk_index >= 0),
    text text NOT NULL,
    UNIQUE (article_id, chunk_index)
);
