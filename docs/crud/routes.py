from flask import Blueprint, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .db import get_session
from .models import Usuario, Item, Solicitacao, ItemSolicitacao, Entrega
from datetime import datetime

bp = Blueprint("api", __name__)


# --------------------------------------
# Utilidades simples
# --------------------------------------
def bad_request(msg, code=400):
    return jsonify({"error": msg}), code

def not_found(entidade="recurso"):
    return jsonify({"error": f"{entidade} não encontrado(a)"}), 404

# --------------------------------------
# USUÁRIOS (CRUD)
# --------------------------------------
@bp.get("/usuarios")
def list_usuarios():
    with get_session() as s:
        data = s.scalars(select(Usuario)).all()
        return jsonify([{
            "id":u.id, "nome":u.nome, "email":u.email,
            "perfil":u.perfil, "status":u.status
        } for u in data])

@bp.get("/usuarios/<int:uid>")
def get_usuario(uid):
    with get_session() as s:
        u = s.get(Usuario, uid)
        if not u: return not_found("usuário")
        return jsonify({
            "id":u.id, "nome":u.nome, "email":u.email,
            "perfil":u.perfil, "status":u.status
        })

@bp.post("/usuarios")
def create_usuario():
    body = request.json or {}
    required = ["nome","email","perfil"]
    if any(k not in body for k in required):
        return bad_request(f"Campos obrigatórios: {', '.join(required)}")
    u = Usuario(
        nome=body["nome"],
        email=body["email"],
        senha_hash=body.get("senha_hash","hash"),  # placeholder
        perfil=body["perfil"],
        status=body.get("status","ATIVO")
    )
    try:
        with get_session() as s:
            s.add(u); s.commit(); s.refresh(u)
            return jsonify({"id":u.id}), 201
    except IntegrityError:
        return bad_request("E-mail já existente", 409)

@bp.put("/usuarios/<int:uid>")
def update_usuario(uid):
    body = request.json or {}
    with get_session() as s:
        u = s.get(Usuario, uid)
        if not u: return not_found("usuário")
        u.nome = body.get("nome", u.nome)
        u.email = body.get("email", u.email)
        u.perfil = body.get("perfil", u.perfil)
        u.status = body.get("status", u.status)
        if "senha_hash" in body:
            u.senha_hash = body["senha_hash"]
        try:
            s.commit()
            return jsonify({"ok": True})
        except IntegrityError:
            s.rollback()
            return bad_request("E-mail já existente", 409)

@bp.delete("/usuarios/<int:uid>")
def delete_usuario(uid):
    with get_session() as s:
        u = s.get(Usuario, uid)
        if not u: return not_found("usuário")
        s.delete(u); s.commit()
        return jsonify({"ok": True})

# --------------------------------------
# ITENS (CRUD)
# --------------------------------------
@bp.get("/itens")
def list_itens():
    with get_session() as s:
        data = s.scalars(select(Item)).all()
        return jsonify([{
            "id":i.id, "nome":i.nome, "categoria":i.categoria,
            "quantidade":i.quantidade, "status":i.status,
            "doador_id":i.doador_id
        } for i in data])

@bp.get("/itens/<int:iid>")
def get_item(iid):
    with get_session() as s:
        i = s.get(Item, iid)
        if not i: return not_found("item")
        return jsonify({
            "id":i.id, "nome":i.nome, "categoria":i.categoria,
            "quantidade":i.quantidade, "status":i.status,
            "doador_id":i.doador_id
        })

@bp.post("/itens")
def create_item():
    body = request.json or {}
    required = ["doador_id","nome"]
    if any(k not in body for k in required):
        return bad_request(f"Campos obrigatórios: {', '.join(required)}")
    i = Item(
        doador_id=body["doador_id"],
        nome=body["nome"],
        categoria=body.get("categoria"),
        quantidade=body.get("quantidade", 1),
        status=body.get("status","DISPONIVEL")
    )
    with get_session() as s:
        s.add(i); s.commit(); s.refresh(i)
        return jsonify({"id":i.id}), 201

@bp.put("/itens/<int:iid>")
def update_item(iid):
    body = request.json or {}
    with get_session() as s:
        i = s.get(Item, iid)
        if not i: return not_found("item")
        i.nome = body.get("nome", i.nome)
        i.categoria = body.get("categoria", i.categoria)
        i.quantidade = body.get("quantidade", i.quantidade)
        i.status = body.get("status", i.status)
        if "doador_id" in body:
            i.doador_id = body["doador_id"]
        s.commit()
        return jsonify({"ok": True})

@bp.delete("/itens/<int:iid>")
def delete_item(iid):
    with get_session() as s:
        i = s.get(Item, iid)
        if not i: return not_found("item")
        s.delete(i); s.commit()
        return jsonify({"ok": True})

# --------------------------------------
# SOLICITAÇÕES (CRUD)
# --------------------------------------
@bp.get("/solicitacoes")
def list_solicitacoes():
    with get_session() as s:
        data = s.scalars(select(Solicitacao)).all()
        return jsonify([{
            "id":x.id, "beneficiario_id":x.beneficiario_id,
            "status":x.status, "descricao":x.descricao,
            "data_abertura": x.data_abertura.isoformat() if x.data_abertura else None,
            "data_fechamento": x.data_fechamento.isoformat() if x.data_fechamento else None
        } for x in data])

@bp.get("/solicitacoes/<int:sid>")
def get_solicitacao(sid):
    with get_session() as s:
        x = s.get(Solicitacao, sid)
        if not x: return not_found("solicitação")
        return jsonify({
            "id":x.id, "beneficiario_id":x.beneficiario_id,
            "status":x.status, "descricao":x.descricao,
            "data_abertura": x.data_abertura.isoformat() if x.data_abertura else None,
            "data_fechamento": x.data_fechamento.isoformat() if x.data_fechamento else None
        })

@bp.post("/solicitacoes")
def create_solicitacao():
    body = request.json or {}
    if "beneficiario_id" not in body:
        return bad_request("Campo obrigatório: beneficiario_id")
    obj = Solicitacao(
        beneficiario_id=body["beneficiario_id"],
        descricao=body.get("descricao"),
        status=body.get("status","ABERTA")
    )
    with get_session() as s:
        s.add(obj); s.commit(); s.refresh(obj)
        return jsonify({"id":obj.id}), 201

@bp.put("/solicitacoes/<int:sid>")
def update_solicitacao(sid):
    body = request.json or {}
    with get_session() as s:
        x = s.get(Solicitacao, sid)
        if not x: return not_found("solicitação")
        x.descricao = body.get("descricao", x.descricao)
        x.status = body.get("status", x.status)
        if "beneficiario_id" in body:
            x.beneficiario_id = body["beneficiario_id"]
        if "data_fechamento" in body:
            from datetime import datetime
            try:
                x.data_fechamento = datetime.fromisoformat(body["data_fechamento"])
            except Exception:
                return bad_request("data_fechamento inválida (use ISO8601)")
        s.commit()
        return jsonify({"ok": True})

@bp.delete("/solicitacoes/<int:sid>")
def delete_solicitacao(sid):
    with get_session() as s:
        x = s.get(Solicitacao, sid)
        if not x: return not_found("solicitação")
        s.delete(x); s.commit()
        return jsonify({"ok": True})
# --------------------------------------
# ITENS_SOLICITACOES (N:N) – CRUD
# --------------------------------------
@bp.get("/itens-solicitacoes")
def list_itens_solicitacoes():
    solicitacao_id = request.args.get("solicitacao_id", type=int)
    with get_session() as s:
        stmt = select(ItemSolicitacao)
        if solicitacao_id:
            stmt = stmt.filter(ItemSolicitacao.solicitacao_id == solicitacao_id)
        data = s.scalars(stmt).all()
        return jsonify([{
            "id":r.id,
            "solicitacao_id":r.solicitacao_id,
            "item_id":r.item_id,
            "quantidade_atendida":r.quantidade_atendida
        } for r in data])

@bp.get("/itens-solicitacoes/<int:rid>")
def get_item_solicitacao(rid):
    with get_session() as s:
        r = s.get(ItemSolicitacao, rid)
        if not r: return not_found("item_solicitacao")
        return jsonify({
            "id":r.id,
            "solicitacao_id":r.solicitacao_id,
            "item_id":r.item_id,
            "quantidade_atendida":r.quantidade_atendida
        })

@bp.post("/itens-solicitacoes")
def create_item_solicitacao():
    body = request.json or {}
    required = ["solicitacao_id","item_id"]
    if any(k not in body for k in required):
        return bad_request(f"Campos obrigatórios: {', '.join(required)}")
    r = ItemSolicitacao(
        solicitacao_id=body["solicitacao_id"],
        item_id=body["item_id"],
        quantidade_atendida=body.get("quantidade_atendida", 1)
    )
    try:
        with get_session() as s:
            s.add(r); s.commit(); s.refresh(r)
            return jsonify({"id": r.id}), 201
    except IntegrityError:
        # IDs inexistentes ou violação de FK
        return bad_request("IDs inválidos: verifique solicitacao_id e item_id.", 409)


@bp.put("/itens-solicitacoes/<int:rid>")
def update_item_solicitacao(rid):
    body = request.json or {}
    with get_session() as s:
        r = s.get(ItemSolicitacao, rid)
        if not r: return not_found("item_solicitacao")
        if "solicitacao_id" in body: r.solicitacao_id = body["solicitacao_id"]
        if "item_id" in body: r.item_id = body["item_id"]
        if "quantidade_atendida" in body: r.quantidade_atendida = body["quantidade_atendida"]
        s.commit()
        return jsonify({"ok": True})

@bp.delete("/itens-solicitacoes/<int:rid>")
def delete_item_solicitacao(rid):
    with get_session() as s:
        r = s.get(ItemSolicitacao, rid)
        if not r: return not_found("item_solicitacao")
        try:
            s.delete(r); s.commit()
            return jsonify({"ok": True})
        except IntegrityError:
            s.rollback()
            return bad_request("Não é possível excluir: vínculo utilizado em outra relação.", 409)


# --------------------------------------
# ENTREGAS – CRUD
# --------------------------------------
@bp.get("/entregas")
def list_entregas():
    with get_session() as s:
        data = s.scalars(select(Entrega)).all()
        return jsonify([{
            "id":e.id,
            "solicitacao_id":e.solicitacao_id,
            "responsavel_org_id":e.responsavel_org_id,
            "data_entrega": e.data_entrega.isoformat() if e.data_entrega else None,
            "observacao": e.observacao
        } for e in data])

@bp.get("/entregas/<int:eid>")
def get_entrega(eid):
    with get_session() as s:
        e = s.get(Entrega, eid)
        if not e: return not_found("entrega")
        return jsonify({
            "id":e.id,
            "solicitacao_id":e.solicitacao_id,
            "responsavel_org_id":e.responsavel_org_id,
            "data_entrega": e.data_entrega.isoformat() if e.data_entrega else None,
            "observacao": e.observacao
        })

@bp.post("/entregas")
def create_entrega():
    body = request.json or {}
    required = ["solicitacao_id","responsavel_org_id"]
    if any(k not in body for k in required):
        return bad_request(f"Campos obrigatórios: {', '.join(required)}")
    # data_entrega opcional → agora por padrão "agora"
    data_entrega = body.get("data_entrega")
    if data_entrega:
        try:
            data_entrega = datetime.fromisoformat(data_entrega)
        except Exception:
            return bad_request("data_entrega inválida (use ISO8601)")
    else:
        data_entrega = datetime.utcnow()

    e = Entrega(
        solicitacao_id=body["solicitacao_id"],
        responsavel_org_id=body["responsavel_org_id"],
        data_entrega=data_entrega,
        observacao=body.get("observacao")
    )
    with get_session() as s:
        s.add(e); s.commit(); s.refresh(e)
        return jsonify({"id":e.id}), 201

@bp.put("/entregas/<int:eid>")
def update_entrega(eid):
    body = request.json or {}
    with get_session() as s:
        e = s.get(Entrega, eid)
        if not e: return not_found("entrega")
        if "solicitacao_id" in body: e.solicitacao_id = body["solicitacao_id"]
        if "responsavel_org_id" in body: e.responsavel_org_id = body["responsavel_org_id"]
        if "observacao" in body: e.observacao = body["observacao"]
        if "data_entrega" in body:
            try:
                e.data_entrega = datetime.fromisoformat(body["data_entrega"])
            except Exception:
                return bad_request("data_entrega inválida (use ISO8601)")
        s.commit()
        return jsonify({"ok": True})

@bp.delete("/entregas/<int:eid>")
def delete_entrega(eid):
    with get_session() as s:
        e = s.get(Entrega, eid)
        if not e: return not_found("entrega")
        try:
            s.delete(e); s.commit()
            return jsonify({"ok": True})
        except IntegrityError:
            s.rollback()
            return bad_request("Não é possível excluir: entrega referenciada.", 409)



