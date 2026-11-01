-- Esquema version 0 (user_version = 0), copiado de sqlite_master de
-- data/financiera.db el 2026-11-01, antes de cualquier migracion.
CREATE TABLE company (
	id INTEGER NOT NULL,
	nombre_legal VARCHAR(200) NOT NULL,
	nombre_comercial VARCHAR(200) NOT NULL,
	actividad_economica VARCHAR(200) NOT NULL,
	pais VARCHAR(100) NOT NULL,
	moneda VARCHAR(10) NOT NULL,
	anio_inicial_analisis INTEGER NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE fiscal_period (
	id INTEGER NOT NULL,
	anio INTEGER NOT NULL,
	estado VARCHAR(20) NOT NULL,
	fecha_creacion DATETIME NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_fiscal_period_anio UNIQUE (anio)
);

CREATE TABLE account (
	id INTEGER NOT NULL,
	codigo VARCHAR(30) NOT NULL,
	nombre VARCHAR(200) NOT NULL,
	categoria_principal VARCHAR(30) NOT NULL,
	subcategoria VARCHAR(30),
	efecto VARCHAR(10),
	naturaleza_saldo VARCHAR(10) NOT NULL,
	estado VARCHAR(10) NOT NULL,
	orden_presentacion INTEGER NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_account_codigo UNIQUE (codigo)
);

CREATE TABLE change_history (
	id INTEGER NOT NULL,
	tabla_afectada VARCHAR(50) NOT NULL,
	registro_id INTEGER NOT NULL,
	campo VARCHAR(100) NOT NULL,
	valor_anterior VARCHAR(200),
	valor_nuevo VARCHAR(200),
	operacion VARCHAR(20) NOT NULL,
	fecha DATETIME NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE balance_entry (
	id INTEGER NOT NULL,
	fiscal_period_id INTEGER NOT NULL,
	account_id INTEGER NOT NULL,
	valor NUMERIC(18, 2) NOT NULL,
	created_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_balance_period_account UNIQUE (fiscal_period_id, account_id),
	FOREIGN KEY(fiscal_period_id) REFERENCES fiscal_period (id) ON DELETE CASCADE,
	FOREIGN KEY(account_id) REFERENCES account (id) ON DELETE RESTRICT
);

CREATE TABLE income_entry (
	id INTEGER NOT NULL,
	fiscal_period_id INTEGER NOT NULL,
	account_id INTEGER NOT NULL,
	valor NUMERIC(18, 2) NOT NULL,
	created_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_income_period_account UNIQUE (fiscal_period_id, account_id),
	FOREIGN KEY(fiscal_period_id) REFERENCES fiscal_period (id) ON DELETE CASCADE,
	FOREIGN KEY(account_id) REFERENCES account (id) ON DELETE RESTRICT
);

CREATE TABLE initial_balance (
	id INTEGER NOT NULL,
	fiscal_period_id INTEGER NOT NULL,
	account_id INTEGER NOT NULL,
	valor NUMERIC(18, 2) NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_initial_period_account UNIQUE (fiscal_period_id, account_id),
	FOREIGN KEY(fiscal_period_id) REFERENCES fiscal_period (id) ON DELETE CASCADE,
	FOREIGN KEY(account_id) REFERENCES account (id) ON DELETE RESTRICT
);

CREATE TABLE statement_status (
	id INTEGER NOT NULL,
	fiscal_period_id INTEGER NOT NULL,
	tipo VARCHAR(20) NOT NULL,
	estado VARCHAR(10) NOT NULL,
	fecha_actualizacion DATETIME NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_statement_period_tipo UNIQUE (fiscal_period_id, tipo),
	FOREIGN KEY(fiscal_period_id) REFERENCES fiscal_period (id) ON DELETE CASCADE
);
