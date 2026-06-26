"""Caso de uso: arma el perfil de "Mi cuenta" del usuario autenticado.

Combina datos del usuario (SQLite) con la metadata del suministro (Oracle),
cifra y persiste la PII en reposo, y devuelve un resultado con la PII enmascarada
y los campos faltantes en None (degradado elegante).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from domain.cuenta import componer_direccion, enmascarar, normalizar_fase
from domain.ports.cuenta_reader import CuentaReader
from domain.ports.cuenta_sensible_repository import CuentaSensibleRepository
from domain.ports.pii_cipher import PiiCipher
from domain.ports.usuario_repository import UsuarioRepository

_VISIBLES_DOCUMENTO = 4
_VISIBLES_CUIT = 3


@dataclass(frozen=True)
class PersonalesResult:
    nombre_o_razon_social: str | None
    tipo_documento: str | None
    nro_documento_masked: str | None
    cuit_masked: str | None
    email: str | None


@dataclass(frozen=True)
class SuministroResult:
    numero: str
    estado_servicio: str | None
    direccion: str | None
    barrio: str | None
    localidad: str | None
    cp: str | None


@dataclass(frozen=True)
class TarifaResult:
    codigo: str | None
    descripcion: str | None
    grupo_tarifario: str | None
    clase: str | None
    clase_descripcion: str | None
    tension: str | None


@dataclass(frozen=True)
class MedidorResult:
    numero: str | None
    marca: str | None
    fase: str
    inteligente_desde: date | None


@dataclass(frozen=True)
class CuentaResult:
    personales: PersonalesResult
    suministro: SuministroResult
    tarifa: TarifaResult
    medidor: MedidorResult


class ObtenerCuentaUseCase:
    def __init__(
        self,
        cuenta_reader: CuentaReader,
        usuario_repo: UsuarioRepository,
        pii_cipher: PiiCipher,
        sensible_repo: CuentaSensibleRepository,
    ) -> None:
        self._cuenta_reader = cuenta_reader
        self._usuario_repo = usuario_repo
        self._pii_cipher = pii_cipher
        self._sensible_repo = sensible_repo

    async def ejecutar(self, usuario: str, suministro_id: str) -> CuentaResult | None:
        raw = await self._cuenta_reader.leer_cuenta(suministro_id)
        if raw is None:
            return None

        email = await self._usuario_repo.get_email(usuario)

        nro_enc = self._pii_cipher.cifrar(raw.nro_documento) if raw.nro_documento else None
        cuit_enc = self._pii_cipher.cifrar(raw.cuit) if raw.cuit else None
        if nro_enc is not None or cuit_enc is not None:
            await self._sensible_repo.upsert(suministro_id, nro_enc, cuit_enc)

        return CuentaResult(
            personales=PersonalesResult(
                nombre_o_razon_social=raw.razon_social,
                tipo_documento=raw.tipo_documento,
                nro_documento_masked=enmascarar(raw.nro_documento, _VISIBLES_DOCUMENTO),
                cuit_masked=enmascarar(raw.cuit, _VISIBLES_CUIT),
                email=email,
            ),
            suministro=SuministroResult(
                numero=suministro_id,
                estado_servicio=raw.estado_servicio,
                direccion=componer_direccion(raw),
                barrio=raw.barrio,
                localidad=raw.localidad,
                cp=raw.cp,
            ),
            tarifa=TarifaResult(
                codigo=raw.codigo_tarifa,
                descripcion=raw.tarifa,
                grupo_tarifario=raw.grupo_tarifario,
                clase=raw.clase,
                clase_descripcion=raw.clase_descripcion,
                tension=raw.tension,
            ),
            medidor=MedidorResult(
                numero=raw.medidor,
                marca=raw.telemedible,
                fase=normalizar_fase(raw.medidor_fases),
                inteligente_desde=raw.telemedible_desde,
            ),
        )
