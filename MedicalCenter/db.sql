-- =========================================================
--  MEDICALCENTER – Script completo (estructura + datos)
--  Probado para MySQL 8.x (Workbench)
-- =========================================================

-- 1) Crear base y preparar sesión
DROP DATABASE IF EXISTS medicalcenter;
CREATE DATABASE medicalcenter CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE medicalcenter;

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';
SET @OLD_TIME_ZONE=@@TIME_ZONE; SET TIME_ZONE='+00:00';

-- =========================================================
-- 2) Tablas base (sin dependencias)
-- =========================================================

-- USUARIOS  (de medicalcenter_usuarios.sql)
DROP TABLE IF EXISTS usuarios;
CREATE TABLE usuarios (
  id_usuario   INT NOT NULL AUTO_INCREMENT,
  rfc          VARCHAR(20)  COLLATE utf8mb4_general_ci NOT NULL,
  contrasena   VARCHAR(255) COLLATE utf8mb4_general_ci NOT NULL,
  privilegio   TINYINT NOT NULL DEFAULT 1,
  estatus      TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (id_usuario),
  UNIQUE KEY idx_rfc (rfc),
  UNIQUE KEY rfc (rfc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- PACIENTES (de medicalcenter_pacientes.sql)
DROP TABLE IF EXISTS pacientes;
CREATE TABLE pacientes (
  id_paciente      INT NOT NULL AUTO_INCREMENT,
  nombres          VARCHAR(100) COLLATE utf8mb4_general_ci NOT NULL,
  apellidos        VARCHAR(100) COLLATE utf8mb4_general_ci NOT NULL,
  fecha_nacimiento DATE NOT NULL,
  genero           ENUM('Masculino','Femenino','Otro') COLLATE utf8mb4_general_ci NOT NULL,
  tipo_sangre      VARCHAR(5) COLLATE utf8mb4_general_ci NOT NULL,
  alergias         TEXT COLLATE utf8mb4_general_ci,
  estatus          TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (id_paciente)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- MEDICOS (de medicalcenter_medicos.sql)
DROP TABLE IF EXISTS medicos;
CREATE TABLE medicos (
  id_medico          INT NOT NULL AUTO_INCREMENT,
  primer_nombre      VARCHAR(50) COLLATE utf8mb4_general_ci NOT NULL,
  segundo_nombre     VARCHAR(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  apellido_paterno   VARCHAR(50) COLLATE utf8mb4_general_ci NOT NULL,
  apellido_materno   VARCHAR(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  cedula_profesional VARCHAR(20) COLLATE utf8mb4_general_ci NOT NULL,
  especialidad       VARCHAR(50) COLLATE utf8mb4_general_ci NOT NULL,
  correo             VARCHAR(100) COLLATE utf8mb4_general_ci NOT NULL,
  rfc                VARCHAR(20) COLLATE utf8mb4_general_ci NOT NULL,
  telefono           VARCHAR(15) COLLATE utf8mb4_general_ci NOT NULL,
  centro_medico      VARCHAR(50) COLLATE utf8mb4_general_ci NOT NULL,
  estatus            TINYINT NOT NULL DEFAULT 1,
  contrasena         VARCHAR(255) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (id_medico),
  UNIQUE KEY cedula_profesional (cedula_profesional),
  KEY rfc (rfc),
  CONSTRAINT medicos_ibfk_1 FOREIGN KEY (rfc) REFERENCES usuarios (rfc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =========================================================
-- 3) Tablas dependientes
-- =========================================================

-- CITA (de medicalcenter_cita.sql)
DROP TABLE IF EXISTS cita;
CREATE TABLE cita (
  id_cita     INT NOT NULL AUTO_INCREMENT,
  id_paciente INT NOT NULL,
  id_medico   INT NOT NULL,
  fecha       DATE NOT NULL,
  hora        TIME NOT NULL,
  motivo      VARCHAR(255) COLLATE utf8mb4_general_ci NOT NULL,
  estatus     VARCHAR(20)  COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'activa',
  estado      TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id_cita),
  KEY id_paciente (id_paciente),
  KEY id_medico (id_medico),
  CONSTRAINT cita_ibfk_1 FOREIGN KEY (id_paciente) REFERENCES pacientes (id_paciente),
  CONSTRAINT cita_ibfk_2 FOREIGN KEY (id_medico)   REFERENCES medicos (id_medico)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- EXPLORACION (de medicalcenter_exploracion.sql)
DROP TABLE IF EXISTS exploracion;
CREATE TABLE exploracion (
  id_exploracion     INT NOT NULL AUTO_INCREMENT,
  id_cita            INT NOT NULL,
  id_paciente        INT NOT NULL,
  id_medico          INT NOT NULL,
  fecha              DATE NOT NULL,
  peso               DECIMAL(5,2)  DEFAULT NULL COMMENT 'en kg',
  altura             DECIMAL(5,2)  DEFAULT NULL COMMENT 'en cm',
  temperatura        DECIMAL(4,2)  DEFAULT NULL COMMENT 'en °C',
  latidos_minuto     INT           DEFAULT NULL,
  saturacion_oxigeno TINYINT UNSIGNED DEFAULT NULL COMMENT 'en porcentaje',
  glucosa            DECIMAL(6,2)  DEFAULT NULL COMMENT 'en mg/dL',
  sintomas           TEXT COLLATE utf8mb4_general_ci,
  diagnostico        TEXT COLLATE utf8mb4_general_ci,
  tratamiento        TEXT COLLATE utf8mb4_general_ci,
  estudios           TEXT COLLATE utf8mb4_general_ci,
  estatus            TINYINT DEFAULT 1 COMMENT '1: activo, 0: eliminado',
  PRIMARY KEY (id_exploracion),
  KEY id_cita (id_cita),
  KEY id_paciente (id_paciente),
  KEY id_medico (id_medico),
  CONSTRAINT exploracion_ibfk_1 FOREIGN KEY (id_cita)     REFERENCES cita (id_cita) ON DELETE CASCADE,
  CONSTRAINT exploracion_ibfk_2 FOREIGN KEY (id_paciente) REFERENCES pacientes (id_paciente),
  CONSTRAINT exploracion_ibfk_3 FOREIGN KEY (id_medico)   REFERENCES medicos (id_medico)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- EXPEDIENTES (de medicalcenter_expedientes.sql)
DROP TABLE IF EXISTS expedientes;
CREATE TABLE expedientes (
  id           INT NOT NULL AUTO_INCREMENT,
  paciente_id  INT NOT NULL,
  diagnostico  TEXT COLLATE utf8mb4_general_ci NOT NULL,
  fecha        DATETIME DEFAULT CURRENT_TIMESTAMP,
  deleted      TINYINT(1) DEFAULT 0,
  PRIMARY KEY (id),
  KEY paciente_id (paciente_id),
  CONSTRAINT expedientes_ibfk_1 FOREIGN KEY (paciente_id)
    REFERENCES pacientes (id_paciente) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =========================================================
-- 4) Datos (según tus inserts originales)
--    Ordenado para respetar FKs
-- =========================================================

-- USUARIOS: inserts
INSERT INTO usuarios (id_usuario,rfc,contrasena,privilegio,estatus) VALUES
(1,'administrador','5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5',2,1),
(2,'VKSAA-KAODA','b7b740f4a0a1ff37e44086f74949b6b3cc6b81431669e33c9b68e66428099b4c',1,0),
(3,'GZLA-RJAG','b7b740f4a0a1ff37e44086f74949b6b3cc6b81431669e33c9b68e66428099b4c',1,0),
(4,'PTOR-RCONR','b7b740f4a0a1ff37e44086f74949b6b3cc6b81431669e33c9b68e66428099b4c',1,1),
(5,'FERL-ORO-POND','b7b740f4a0a1ff37e44086f74949b6b3cc6b81431669e33c9b68e66428099b4c',1,0),
(6,'OMG-MOG-JOM','b7b740f4a0a1ff37e44086f74949b6b3cc6b81431669e33c9b68e66428099b4c',1,1),
(7,'177713737','b7b740f4a0a1ff37e44086f74949b6b3cc6b81431669e33c9b68e66428099b4c',1,1),
(10,'GNR20045Y','b7b740f4a0a1ff37e44086f74949b6b3cc6b81431669e33c9b68e66428099b4c',1,1);

-- PACIENTES: inserts
INSERT INTO pacientes (id_paciente,nombres,apellidos,fecha_nacimiento,genero,tipo_sangre,alergias,estatus) VALUES
(1,'Juan','Gomez','1990-01-01','Masculino','O+','Ninguna',1),
(2,'Samael Antonio','Gonzales Ruiz','2004-07-07','Masculino','B-','nada',1),
(3,'Isabella ','Garcia','2003-06-18','Femenino','O-','Cacao',1),
(4,'Ian','Portillo','2000-07-09','Masculino','B-','Analgesicos',0),
(5,'Orlando','Ayub','2004-08-29','Masculino','AB+','Abejas',1),
(6,'Leonardo','Dicaprio','2001-07-09','Masculino','AB+','Paracetamol',1),
(7,'Belen','Vega','2005-09-21','Femenino','O-','ninguna',0),
(8,'Ivan Isay','Guerra Lopez','1987-07-05','Masculino','A+','',1),
(9,'xxxxxxxxx','xxxxxxxxxxxxxxx','2024-07-09','Femenino','O+','xxxxxxxxxxxxxxx',0),
(10,'Guillermo','Ochoa','2004-07-16','Masculino','B+','',1),
(11,'Sebastian','Marfil Guzman','2005-12-20','Masculino','O+','',1),
(12,'Ian','Rodriguez','2025-08-09','Masculino','A+','lacteos',1);

-- MEDICOS: inserts
INSERT INTO medicos (id_medico,primer_nombre,segundo_nombre,apellido_paterno,apellido_materno,cedula_profesional,especialidad,correo,rfc,telefono,centro_medico,estatus,contrasena) VALUES
(1,'Aaron','Daniel','Oinz','Jauca','71361631317','Cirugía General','aaron@gmail.com','VKSAA-KAODA','4422592762','MedicalCenter Oriente',0,''),
(2,'Gonzalo','Alejandro','Ramiro','Josek','17712721','Cardiología','Gonzalon@gmail.com','GZLA-RJAG','4427400100','MedicalCenter Sur',0,''),
(3,'Lupita','Ramos','Rojas','Contreras','8821818318','Pediatría','Patos@gmail.com','PTOR-RCONR','0220420040','MedicalCenter Poniente',1,''),
(4,'Fernando','Austria','Pons','Orozco','1211214443','Neurología','FernandoO@gmail.com','FERL-ORO-POND','544746488499','MedicalCenter Oriente',0,''),
(5,'Omar','Jacinto','Guerra','Lopez','15525211631631','Cirugía General','Omarcito@gmail.com','OMG-MOG-JOM','4422789076','MedicalCenter Sur',1,''),
(6,'Arturo','Leonardo','Lopez','Lario','311318081183','Cirugía General','arturlario@gamil.com','177713737','56588558000','MedicalCenter Sur',1,''),
(7,'Genaro','Camilo','Arias','Brosk','882181831098','Medicina Interna','Genaro@gmail.com','GNR20045Y','44274958583','MedicalCenter Norte',1,'12345678');

-- CITA: inserts
INSERT INTO cita (id_cita,id_paciente,id_medico,fecha,hora,motivo,estatus,estado) VALUES
(1,1,5,'2025-07-25','19:30:00','Dolor abdominal agudo','cancelada',0),
(2,1,6,'2025-07-31','12:30:00','Dolor de cabeza intenso, golpe en la diagonal de la cabeza','cancelada',0),
(3,2,5,'2025-07-31','14:00:00','todooo','activa',1),
(4,3,6,'2025-07-31','19:50:00','dolor de espalda agudo','activa',1),
(5,3,6,'2025-08-16','19:10:00','nada','activa',1),
(6,6,3,'2025-08-16','19:20:00','gripa','activa',1),
(7,11,5,'2025-08-10','21:50:00','dolor de cabeza','activa',1),
(8,8,3,'2025-08-22','21:20:00','dolor estomago','activa',1);

-- EXPLORACION: inserts
INSERT INTO exploracion (id_exploracion,id_cita,id_paciente,id_medico,fecha,peso,altura,temperatura,latidos_minuto,saturacion_oxigeno,glucosa,sintomas,diagnostico,tratamiento,estudios,estatus) VALUES
(1,3,2,5,'2025-07-30',80.00,1.80,38.20,80,97,100.00,'Fiebre y vomito','Covid 19','paracetamol','examen de sangre',1),
(2,5,3,6,'2025-08-07',60.30,150.00,38.00,80,97,100.00,'fiebre','covid','paracetamol','examenes de glucosa',1),
(3,6,6,3,'2025-08-07',70.00,180.00,39.00,80,95,95.00,'asjsajsajsa','gripe','xl3','tomografia',1),
(4,8,8,3,'2025-08-09',89.00,178.00,38.00,80,90,100.10,'Dolor de estomago fuerte y abdominal','indigestión','Buscapina 600mg, paracetamol 200mg, durante 3 días ','examen de sangre.',1),
(5,8,8,3,'2025-08-09',89.00,178.00,38.00,80,90,100.10,'Dolor de estomago fuerte y abdominal fuerte vomito','indigestión','Buscapina 600mg, paracetamol 200mg, durante 3 días ','examen de sangre.',1),
(6,7,11,5,'2025-08-09',90.00,185.00,39.00,80,89,110.00,'dolor en el brazo','contusion leve','paracetamol cada 8 hrs.','radiografia brazo',1);

-- EXPEDIENTES: inserts
INSERT INTO expedientes (id,paciente_id,diagnostico,fecha,deleted) VALUES
(1,2,'dgba','2025-07-31 15:14:08',0),
(2,2,'Fiebre','2025-08-07 15:27:47',0),
(3,3,'gripe','2025-08-07 18:13:07',0),
(4,6,'tetetetet','2025-08-07 18:20:31',0),
(5,11,'contusion leve','2025-08-09 21:15:08',0),
(6,3,'covid','2025-08-09 23:32:01',0);

-- =========================================================
-- 5) Restaurar settings
-- =========================================================
SET TIME_ZONE=@OLD_TIME_ZONE;
SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- Fin del script
