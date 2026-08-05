-- Tabela e dados de exemplo para o lab da aula 5.4.
-- Execute este script no DBeaver, conectado ao banco Postgres do Render.

DROP TABLE IF EXISTS cursos;

CREATE TABLE cursos (
    id            SERIAL PRIMARY KEY,
    titulo        TEXT    NOT NULL,
    area          TEXT    NOT NULL,
    carga_horaria INTEGER NOT NULL
);

INSERT INTO cursos (titulo, area, carga_horaria) VALUES
    ('Fundamentos de LLMs',   'IA',      12),
    ('RAG na Prática',        'IA',      16),
    ('Agentes e Tool Use',    'IA',      20),
    ('Modelagem Dimensional', 'Dados',   24),
    ('APIs com FastAPI',      'Backend', 18);
