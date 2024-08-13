BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "hospitals" (
	"hospital_id"	INTEGER,
	"hospital_name"	TEXT NOT NULL,
	"address_line"	TEXT NOT NULL,
	"phone_number"	TEXT NOT NULL,
	PRIMARY KEY("hospital_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "diagnosis" (
	"diagnosis_id"	INTEGER,
	"diagnosis_name"	TEXT NOT NULL,
	"recommendations"	TEXT NOT NULL,
	PRIMARY KEY("diagnosis_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "reports" (
	"report_id"	INTEGER,
	"report_date"	TEXT NOT NULL,
	"test_name"	TEXT NOT NULL,
	"test_result"	REAL NOT NULL,
	"test_units"	TEXT NOT NULL,
	"test_reference_range"	TEXT NOT NULL,
	"report_type_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"hospital_id"	INTEGER NOT NULL,
	"interpretation"	VARCHAR(10),
	FOREIGN KEY("hospital_id") REFERENCES "hospitals"("hospital_id"),
	FOREIGN KEY("report_type_id") REFERENCES "report_type"("report_type_id"),
	FOREIGN KEY("user_id") REFERENCES "user"("user_id"),
	PRIMARY KEY("report_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "appointments" (
	"appointment_id"	INTEGER,
	"appointment_date"	TEXT NOT NULL,
	"payment_total"	REAL NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"hospital_id"	INTEGER NOT NULL,
	"doctor_id"	INTEGER NOT NULL,
	FOREIGN KEY("doctor_id") REFERENCES "doctors"("doctor_id"),
	FOREIGN KEY("hospital_id") REFERENCES "hospitals"("hospital_id"),
	FOREIGN KEY("user_id") REFERENCES "user"("user_id"),
	PRIMARY KEY("appointment_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "diagnosis_by_doctor" (
	"doctor_id"	INTEGER NOT NULL,
	"diagnosis_id"	INTEGER NOT NULL,
	FOREIGN KEY("diagnosis_id") REFERENCES "diagnosis"("diagnosis_id"),
	FOREIGN KEY("doctor_id") REFERENCES "doctors"("doctor_id"),
	PRIMARY KEY("doctor_id","diagnosis_id")
);
CREATE TABLE IF NOT EXISTS "medicine_by_diagnosis" (
	"medicine_id"	INTEGER NOT NULL,
	"diagnosis_id"	INTEGER NOT NULL,
	FOREIGN KEY("diagnosis_id") REFERENCES "diagnosis"("diagnosis_id"),
	FOREIGN KEY("medicine_id") REFERENCES "medicine"("medicine_id"),
	PRIMARY KEY("medicine_id","diagnosis_id")
);
CREATE TABLE IF NOT EXISTS "report_type" (
	"report_type_id"	INTEGER NOT NULL,
	"report_type_name"	NVARCHAR(50) NOT NULL UNIQUE,
	CONSTRAINT "PK_report_type" PRIMARY KEY("report_type_id")
);
CREATE TABLE IF NOT EXISTS "USER" (
	"user_id"	INTEGER,
	"first_name"	TEXT NOT NULL,
	"last_name"	TEXT NOT NULL,
	"gender"	NVARCHAR(5) NOT NULL,
	"birth_date"	TEXT NOT NULL,
	"phone_number"	TEXT NOT NULL,
	PRIMARY KEY("user_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "doctor_specialization" (
	"specialization_id"	INTEGER NOT NULL,
	"specialization_name"	NVARCHAR(50) NOT NULL UNIQUE,
	CONSTRAINT "PK_doctor_specialization" PRIMARY KEY("specialization_id")
);
CREATE TABLE IF NOT EXISTS "doctors" (
	"doctor_id"	INTEGER,
	"first_name"	TEXT NOT NULL,
	"last_name"	TEXT NOT NULL,
	"phone_number"	TEXT NOT NULL,
	"email"	TEXT NOT NULL,
	"specialization_id"	INTEGER NOT NULL,
	"hospital_id"	INTEGER NOT NULL,
	FOREIGN KEY("hospital_id") REFERENCES "hospitals"("hospital_id"),
	FOREIGN KEY("specialization_id") REFERENCES "doctor_specialization"("specialization_id"),
	PRIMARY KEY("doctor_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "medicine" (
	"medicine_id"	INTEGER,
	"medicine_name"	TEXT NOT NULL,
	"dosage"	INTEGER NOT NULL,
	"daily_frequency"	INTEGER NOT NULL,
	PRIMARY KEY("medicine_id" AUTOINCREMENT)
);
CREATE INDEX IF NOT EXISTS "report_type_id_idx" ON "reports" (
	"report_type_id"
);
CREATE INDEX IF NOT EXISTS "user_id_idx" ON "reports" (
	"user_id"
);
CREATE INDEX IF NOT EXISTS "hospital_id_idx" ON "reports" (
	"hospital_id"
);
CREATE INDEX IF NOT EXISTS "user_id_idx_appointments" ON "appointments" (
	"user_id"
);
CREATE INDEX IF NOT EXISTS "hospital_id_idx_appointments" ON "appointments" (
	"hospital_id"
);
CREATE INDEX IF NOT EXISTS "doctor_id_idx_appointments" ON "appointments" (
	"doctor_id"
);
CREATE TRIGGER set_interpretation
AFTER INSERT ON reports
FOR EACH ROW
BEGIN
    UPDATE reports
    SET interpretation = (
        CASE
            WHEN NEW.test_result >= CAST(substr(NEW.test_reference_range, 1, instr(NEW.test_reference_range, '-') - 1) AS NUMERIC) AND
                 NEW.test_result <= CAST(substr(NEW.test_reference_range, instr(NEW.test_reference_range, '-') + 1) AS NUMERIC) THEN 'Normal'
            WHEN NEW.test_result < CAST(substr(NEW.test_reference_range, 1, instr(NEW.test_reference_range, '-') - 1) AS NUMERIC) THEN 'Low'
            WHEN NEW.test_result > CAST(substr(NEW.test_reference_range, instr(NEW.test_reference_range, '-') + 1) AS NUMERIC) THEN 'High'
        END
    )
    WHERE report_id = NEW.report_id;
END;
CREATE TRIGGER update_interpretation
AFTER UPDATE OF test_result, test_reference_range ON reports
FOR EACH ROW
BEGIN
    UPDATE reports
    SET interpretation = (
        CASE
            WHEN NEW.test_result >= CAST(substr(NEW.test_reference_range, 1, instr(NEW.test_reference_range, '-') - 1) AS NUMERIC) AND
                 NEW.test_result <= CAST(substr(NEW.test_reference_range, instr(NEW.test_reference_range, '-') + 1) AS NUMERIC) THEN 'Normal'
            WHEN NEW.test_result < CAST(substr(NEW.test_reference_range, 1, instr(NEW.test_reference_range, '-') - 1) AS NUMERIC) THEN 'Low'
            WHEN NEW.test_result > CAST(substr(NEW.test_reference_range, instr(NEW.test_reference_range, '-') + 1) AS NUMERIC) THEN 'High'
        END
    )
    WHERE report_id = NEW.report_id;
END;
COMMIT;
