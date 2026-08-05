-- Schema e dados de exemplo para o lab da aula 5.4.
-- Execute este script no DBeaver, conectado ao banco Postgres do Render.

DROP TABLE IF EXISTS matriculas;
DROP TABLE IF EXISTS alunos;
DROP TABLE IF EXISTS cursos;

CREATE TABLE cursos (
    id            SERIAL PRIMARY KEY,
    titulo        TEXT    NOT NULL,
    area          TEXT    NOT NULL,
    carga_horaria INTEGER NOT NULL,
    ativo         BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE alunos (
    id    SERIAL PRIMARY KEY,
    nome  TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE matriculas (
    id             SERIAL PRIMARY KEY,
    aluno_id       INTEGER NOT NULL REFERENCES alunos (id),
    curso_id       INTEGER NOT NULL REFERENCES cursos (id),
    data_matricula DATE    NOT NULL DEFAULT CURRENT_DATE,
    concluido      BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO cursos (titulo, area, carga_horaria, ativo) VALUES
    ('Fundamentos de LLMs',        'IA',      12, TRUE),
    ('RAG na Prática',             'IA',      16, TRUE),
    ('Agentes e Tool Use',         'IA',      20, TRUE),
    ('Modelagem Dimensional',      'Dados',   24, TRUE),
    ('APIs com FastAPI',           'Backend', 18, FALSE);

INSERT INTO alunos (nome, email) VALUES
    ('Ana Ribeiro',    'ana@exemplo.com'),
    ('Bruno Tavares',  'bruno@exemplo.com'),
    ('Carla Mendes',   'carla@exemplo.com'),
    ('Diego Sampaio',  'diego@exemplo.com');

INSERT INTO matriculas (aluno_id, curso_id, data_matricula, concluido) VALUES
    (1, 1, '2026-03-10', TRUE),
    (1, 2, '2026-04-02', FALSE),
    (2, 1, '2026-03-11', TRUE),
    (2, 3, '2026-05-20', FALSE),
    (3, 4, '2026-02-18', TRUE),
    (4, 2, '2026-04-05', FALSE),
    (4, 3, '2026-05-21', FALSE);
