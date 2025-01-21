import psycopg2
from psycopg2.extras import RealDictCursor

# Función para obtener la conexión a la base de datos
def get_db_connection():
    return psycopg2.connect(
        dbname='postgres',
        user='postgres.ldsihxoskpzlzdprmvmq',
        password='VLNVddyd2002',
        host='aws-0-us-east-1.pooler.supabase.com',
        port='6543'
    )

# Función para inicializar las tablas
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL
    );
    CREATE TABLE IF NOT EXISTS predictions (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        patient_id VARCHAR(255) NOT NULL,
        patient_name VARCHAR(255) NOT NULL,
        patient_age INT NOT NULL,
        patient_gender VARCHAR(10) NOT NULL,
        prediagnosis TEXT NOT NULL,
        video BYTEA NOT NULL,
        AI_BraTs_Function_report BYTEA NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    patient_id VARCHAR(255) NOT NULL UNIQUE,
    numero_historia_clinica VARCHAR(255) NOT NULL,
    survey_completed BOOLEAN DEFAULT FALSE, -- Campo que indica si la encuesta ha sido completada
    FOREIGN KEY (user_id) REFERENCES users(id)
);

    CREATE TABLE IF NOT EXISTS password_reset_tokens (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        token VARCHAR(255) NOT NULL,
        expiration TIMESTAMP NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS diagnostics (
        id SERIAL PRIMARY KEY,
        patient_id VARCHAR(255) NOT NULL,
        user_id INT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
    );
    CREATE TABLE IF NOT EXISTS reports (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        patient_id VARCHAR(255) NOT NULL,
        report_text2 TEXT NOT NULL,
        report_text5 TEXT NOT NULL,
        graph2_image_path TEXT NOT NULL,
        graph5_image_path TEXT NOT NULL,
        feedback JSON NOT NULL,
        modalities_description TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS reports (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        patient_id VARCHAR(255) NOT NULL,
        report_text2 TEXT NOT NULL,
        report_text5 TEXT NOT NULL,
        graph2_image_path TEXT NOT NULL,
        graph5_image_path TEXT NOT NULL,
        feedback JSON NOT NULL,
        modalities_description TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS surveys (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(255) NOT NULL, -- Usar VARCHAR(255) para permitir IDs alfanuméricos
    ayudo_ia BOOLEAN NOT NULL,        -- Indica si la IA ayudó a mejorar el diagnóstico
    comentarios_adicionales TEXT,    -- Comentarios adicionales sobre el proceso
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) -- Asegúrate de que patients.patient_id también sea VARCHAR
);
    """)
    conn.commit()

    # Agregar columna si no existe
    cursor.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name='diagnostics' AND column_name='is_generated'
        ) THEN
            ALTER TABLE diagnostics ADD COLUMN is_generated BOOLEAN DEFAULT FALSE;
        END IF;
    END
    $$;
    """)
    conn.commit()
    
    cursor.close()
    conn.close()

