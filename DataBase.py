import psycopg2
from psycopg2.extras import RealDictCursor

# Función para obtener la conexión a la base de datos
def get_db_connection():
    return psycopg2.connect(
        # dbname='postgres',
        # user='postgres.ldsihxoskpzlzdprmvmq',
        # password='VLNVddyd2002',
        # host='aws-0-us-east-1.pooler.supabase.com',
        # port='6543'
        dbname='postgres',
        user='postgres',
        password='admin123',
        host='localhost',
        port='5432'
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
        t1ce_path TEXT, -- Path del archivo T1c
        t2_path TEXT, -- Path del archivo T2
        flair_path TEXT, -- Path del archivo FLAIR
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
        description TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
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
    ayudo_ia VARCHAR(50) NOT NULL,    -- Cambiado de BOOLEAN a VARCHAR(50) 6para almacenar las opciones
    mejoro_ia BOOLEAN NOT NULL,
    comentarios_adicionales TEXT,     -- cComentarios adicionales sobre el proceso
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE, -- Aquí se agrega ON DELETE CASCADE
    CONSTRAINT unique_patient_id UNIQUE (patient_id)  -- Restringe la tabla a solo una encuesta por paciente
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
    #subir commit
    # Modificar la tabla 'diagnostics' si es necesario
    cursor.execute("""
        DO $$
        BEGIN
            -- Crear el tipo ENUM si no existe
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type
                WHERE typname = 'cancer_status'
            ) THEN
                CREATE TYPE cancer_status AS ENUM ('no se detecta cancer', 'cancer detectado', 'diagnostico incierto');
            END IF;

            -- Eliminar la columna has_cancer si existe
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'diagnostics' AND column_name = 'has_cancer'
            ) THEN
                ALTER TABLE diagnostics DROP COLUMN has_cancer;
            END IF;

            -- Agregar la nueva columna cancer_status si no existe
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'diagnostics' AND column_name = 'cancer_status'
            ) THEN
                ALTER TABLE diagnostics ADD COLUMN cancer_status cancer_status DEFAULT 'diagnostico incierto';
            END IF;
            -- Se agrega columna cancer_prediction 
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'diagnostics' AND column_name = 'cancer_prediction'
            ) THEN
                ALTER TABLE diagnostics ADD COLUMN cancer_prediction BOOLEAN;
            END IF;
            -- Se agrega columna is_generated_by_ia 
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'diagnostics' AND column_name = 'is_generated_by_ia'
            ) THEN
                ALTER TABLE diagnostics ADD COLUMN is_generated_by_ia BOOLEAN DEFAULT FALSE;
            END IF;
        END
        $$;
    """)
    conn.commit()
    # Agregar columna 'report_path' si no existe en la tabla reports
    cursor.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name='diagnostics' AND column_name='report_path'
            ) THEN
                ALTER TABLE diagnostics ADD COLUMN report_path TEXT;
            END IF;
        END
        $$;
        """)
    conn.commit()
    # Agregar columna 'created_at' si no existe
    cursor.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name='diagnostics' AND column_name='created_at'
            ) THEN
                ALTER TABLE diagnostics ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            END IF;
        END
        $$;
        """)
    conn.commit()
    # Agregar columna 'updated_at' si no existe
    cursor.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'diagnostics' AND column_name = 'updated_at'
            ) THEN
                ALTER TABLE diagnostics ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            END IF;
        END
        $$;
    """)
    conn.commit()

    # Crear trigger para actualizar 'updated_at' automáticamente
    cursor.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_trigger
                WHERE tgname = 'set_updated_at'
            ) THEN
                CREATE TRIGGER set_updated_at
                BEFORE UPDATE ON diagnostics
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
            END IF;
        END
        $$;
    """)
    conn.commit()
    # Verificar y agregar columnas faltantes en `patients`
    cursor.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'patients' AND column_name = 'predicted_segmentation'
            ) THEN
                ALTER TABLE patients ADD COLUMN predicted_segmentation JSONB;
            END IF;

            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'patients' AND column_name = 'graph1_path'
            ) THEN
                ALTER TABLE patients ADD COLUMN graph1_path TEXT;
            END IF;

            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'patients' AND column_name = 'graph2_path'
            ) THEN
                ALTER TABLE patients ADD COLUMN graph2_path TEXT;
            END IF;

            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'patients' AND column_name = 'graph3_path'
            ) THEN
                ALTER TABLE patients ADD COLUMN graph3_path TEXT;
            END IF;

            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'patients' AND column_name = 'graph4_path'
            ) THEN
                ALTER TABLE patients ADD COLUMN graph4_path TEXT;
            END IF;

            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'patients' AND column_name = 'graph5_path'
            ) THEN
                ALTER TABLE patients ADD COLUMN graph5_path TEXT;
            END IF;

            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'patients' AND column_name = 'graph6_path'
            ) THEN
                ALTER TABLE patients ADD COLUMN graph6_path TEXT;
            END IF;
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'patients' AND column_name = 'graph_segmentation_path'
            ) THEN
                ALTER TABLE patients ADD COLUMN graph_segmentation_path TEXT;
            END IF;
            -- se agrega campo t1_path para el modelo de clasificacion
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'patients' AND column_name = 't1_path'
            ) THEN
                ALTER TABLE patients ADD COLUMN t1_path TEXT;
            END IF;
        END
        $$;
        """)

    conn.commit()

    cursor.close()
    conn.close()

