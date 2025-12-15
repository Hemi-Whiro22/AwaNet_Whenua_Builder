-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE rongohia.artifacts (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  script_id uuid,
  output_type text,
  output_content text,
  meta jsonb,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT artifacts_pkey PRIMARY KEY (id),
  CONSTRAINT artifacts_script_id_fkey FOREIGN KEY (script_id) REFERENCES rongohia.scripts(id)
);
CREATE TABLE rongohia.audit_logs (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  action text,
  admin_user_id uuid,
  target_user_id uuid,
  details text,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT audit_logs_pkey PRIMARY KEY (id)
);
CREATE TABLE rongohia.carver_memory (
  user_id uuid NOT NULL,
  interests ARRAY,
  verification_style text,
  trust_level integer,
  language_preference text,
  last_updated timestamp with time zone,
  CONSTRAINT carver_memory_pkey PRIMARY KEY (user_id)
);
CREATE TABLE rongohia.carvings (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  script_id uuid,
  artifact_id uuid,
  status text DEFAULT 'complete'::text,
  feedback text,
  created_at timestamp with time zone DEFAULT now(),
  validation_id uuid,
  CONSTRAINT carvings_pkey PRIMARY KEY (id),
  CONSTRAINT carvings_script_id_fkey FOREIGN KEY (script_id) REFERENCES rongohia.scripts(id),
  CONSTRAINT carvings_artifact_id_fkey FOREIGN KEY (artifact_id) REFERENCES rongohia.artifacts(id)
);
CREATE TABLE rongohia.chat_sessions (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid,
  title text,
  created_at timestamp with time zone DEFAULT now(),
  last_message_at timestamp with time zone,
  message_count integer,
  CONSTRAINT chat_sessions_pkey PRIMARY KEY (id)
);
CREATE TABLE rongohia.config_files (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  filename text,
  file_type text,
  content text,
  tags ARRAY,
  access_level text,
  version integer,
  created_by uuid,
  created_at timestamp with time zone DEFAULT now(),
  description text,
  CONSTRAINT config_files_pkey PRIMARY KEY (id)
);
CREATE TABLE rongohia.config_versions (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  config_id uuid,
  version integer,
  content text,
  created_by uuid,
  created_at timestamp with time zone DEFAULT now(),
  change_note text,
  CONSTRAINT config_versions_pkey PRIMARY KEY (id)
);
CREATE TABLE rongohia.messages (
  id bigint NOT NULL DEFAULT nextval('rongohia.messages_id_seq'::regclass),
  user_id uuid,
  session_id text,
  role text,
  content text,
  genealogy_context jsonb,
  created_at timestamp with time zone DEFAULT now(),
  embedding USER-DEFINED,
  CONSTRAINT messages_pkey PRIMARY KEY (id)
);
CREATE TABLE rongohia.meta (
  id bigint NOT NULL DEFAULT nextval('rongohia.meta_id_seq'::regclass),
  timestamp timestamp with time zone DEFAULT now(),
  rotation_nonce text NOT NULL,
  signature text NOT NULL,
  source text,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT meta_pkey PRIMARY KEY (id)
);
CREATE TABLE rongohia.prompts (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  session_id text,
  prompt text,
  model text,
  timestamp timestamp with time zone DEFAULT now(),
  CONSTRAINT prompts_pkey PRIMARY KEY (id)
);
CREATE TABLE rongohia.scripts (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  title text,
  content text,
  type text DEFAULT 'prompt'::text,
  author text,
  tags ARRAY,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT scripts_pkey PRIMARY KEY (id)
);