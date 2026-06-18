from datetime import date, datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Suministro(Base):
    __tablename__ = "suministros"

    id: Mapped[str] = mapped_column(primary_key=True)
    lat: Mapped[float]
    lon: Mapped[float]
    suministro_referencia: Mapped[str]


class ConsumoDiario(Base):
    __tablename__ = "consumo_diario"

    suministro_id: Mapped[str] = mapped_column(ForeignKey("suministros.id"), primary_key=True)
    fecha: Mapped[date] = mapped_column(primary_key=True)
    kwh: Mapped[float]


class ObjetivoConsumo(Base):
    __tablename__ = "objetivo_consumo"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    suministro_id: Mapped[str] = mapped_column(ForeignKey("suministros.id"))
    valor_kwh: Mapped[float]
    origen: Mapped[str]
    vigente_desde: Mapped[date]


class ProyeccionMensual(Base):
    __tablename__ = "proyeccion_mensual"

    suministro_id: Mapped[str] = mapped_column(ForeignKey("suministros.id"), primary_key=True)
    mes: Mapped[date] = mapped_column(primary_key=True)
    metodo_aplicado: Mapped[str]
    meses_usados_como_base: Mapped[int]
    dias_usados_como_base: Mapped[int]
    bandera_confianza: Mapped[str]
    rango_inferior_kwh: Mapped[float | None]
    rango_superior_kwh: Mapped[float | None]


class NotificacionConfig(Base):
    __tablename__ = "notificaciones_config"

    usuario_id: Mapped[str] = mapped_column(primary_key=True)
    tipo: Mapped[str] = mapped_column(primary_key=True)
    canal: Mapped[str] = mapped_column(primary_key=True)
    habilitado: Mapped[bool]


class FacturaRedireccion(Base):
    __tablename__ = "factura_redireccion"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    numero_cliente: Mapped[str]
    numero_contrato: Mapped[str]


class Usuario(Base):
    __tablename__ = "usuarios"

    usuario: Mapped[str] = mapped_column(primary_key=True)
    suministro_id: Mapped[str]
    email: Mapped[str | None] = mapped_column(nullable=True, default=None)


class NotificacionEnviada(Base):
    __tablename__ = "notificaciones_enviadas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    suministro_id: Mapped[str]
    tipo_alerta: Mapped[str]
    fecha_envio: Mapped[datetime]
