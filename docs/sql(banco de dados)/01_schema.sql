CREATE DATABASE IF NOT EXISTS plataforma_doacoes
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;
USE plataforma_doacoes;

DROP TABLE IF EXISTS usuarios;
CREATE TABLE usuarios (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  nome          VARCHAR(120)       NOT NULL,
  email         VARCHAR(120)       NOT NULL,
  senha_hash    VARCHAR(255)       NOT NULL,
  perfil        ENUM('DOADOR','BENEFICIARIO','ORGANIZACAO','ADMIN') NOT NULL,
  status        ENUM('ATIVO','INATIVO') NOT NULL DEFAULT 'ATIVO',
  criado_em     DATETIME           NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uk_usuarios_email UNIQUE (email)
) ENGINE=InnoDB;
CREATE INDEX idx_usuarios_perfil  ON usuarios(perfil);
CREATE INDEX idx_usuarios_status  ON usuarios(status);

DROP TABLE IF EXISTS itens;
CREATE TABLE itens (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  doador_id      INT            NOT NULL,
  nome           VARCHAR(120)   NOT NULL,
  categoria      VARCHAR(60)    NULL,
  quantidade     INT            NOT NULL DEFAULT 1,
  status         ENUM('DISPONIVEL','RESERVADO','ENTREGUE') NOT NULL DEFAULT 'DISPONIVEL',
  data_cadastro  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_itens_doador
    FOREIGN KEY (doador_id) REFERENCES usuarios(id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;
CREATE INDEX idx_itens_status    ON itens(status);
CREATE INDEX idx_itens_categoria ON itens(categoria);
CREATE INDEX idx_itens_doador    ON itens(doador_id);

DROP TABLE IF EXISTS solicitacoes;
CREATE TABLE solicitacoes (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  beneficiario_id   INT            NOT NULL,
  descricao         TEXT           NULL,
  status            ENUM('ABERTA','EM_ENTREGA','ATENDIDA','CANCELADA') NOT NULL DEFAULT 'ABERTA',
  data_abertura     DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  data_fechamento   DATETIME       NULL,
  CONSTRAINT fk_solic_benef
    FOREIGN KEY (beneficiario_id) REFERENCES usuarios(id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;
CREATE INDEX idx_solic_status ON solicitacoes(status);
CREATE INDEX idx_solic_benef  ON solicitacoes(beneficiario_id);

DROP TABLE IF EXISTS itens_solicitacoes;
CREATE TABLE itens_solicitacoes (
  id                   INT AUTO_INCREMENT PRIMARY KEY,
  solicitacao_id       INT NOT NULL,
  item_id              INT NOT NULL,
  quantidade_atendida  INT NOT NULL DEFAULT 1,
  CONSTRAINT fk_is_solic
    FOREIGN KEY (solicitacao_id) REFERENCES solicitacoes(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_is_item
    FOREIGN KEY (item_id)        REFERENCES itens(id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT uk_is_solic_item UNIQUE (solicitacao_id, item_id)
) ENGINE=InnoDB;
CREATE INDEX idx_is_item ON itens_solicitacoes(item_id);

DROP TABLE IF EXISTS entregas;
CREATE TABLE entregas (
  id                  INT AUTO_INCREMENT PRIMARY KEY,
  solicitacao_id      INT NOT NULL,
  responsavel_org_id  INT NOT NULL,
  data_entrega        DATETIME NOT NULL,
  observacao          TEXT NULL,
  CONSTRAINT fk_entrega_solic
    FOREIGN KEY (solicitacao_id)     REFERENCES solicitacoes(id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_entrega_org
    FOREIGN KEY (responsavel_org_id) REFERENCES usuarios(id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;
CREATE INDEX idx_entrega_solic ON entregas(solicitacao_id);
CREATE INDEX idx_entrega_org   ON entregas(responsavel_org_id);

DROP TABLE IF EXISTS parcerias;
CREATE TABLE parcerias (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  nome         VARCHAR(120) NOT NULL,
  tipo         VARCHAR(60)  NULL,
  contato      VARCHAR(120) NULL,
  observacoes  TEXT         NULL,
  ativo        BOOLEAN      NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;
CREATE INDEX idx_parcerias_ativo ON parcerias(ativo);

DROP TABLE IF EXISTS logs;
CREATE TABLE logs (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  entidade    VARCHAR(60) NOT NULL,
  entidade_id INT         NULL,
  usuario_id  INT         NULL,
  acao        ENUM('CREATE','UPDATE','DELETE') NOT NULL,
  datahora    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  detalhe     TEXT        NULL,
  CONSTRAINT fk_logs_usuario
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;
CREATE INDEX idx_logs_entidade   ON logs(entidade, entidade_id);
CREATE INDEX idx_logs_usuario    ON logs(usuario_id);
