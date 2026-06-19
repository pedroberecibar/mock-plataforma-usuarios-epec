## 1.0.0 (2026-06-19)

### Features

* **factura:** integración experimental con API EPEC + refactor scheduler backfill ([def7420](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/def742076055df273032d3afbc3d797cbdfb9ab6))
* **ingesta:** filtrar Oracle por equipos configurados vía INGEST_EQUIPOS ([ad7415b](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/ad7415b8ec0ccafb59b397615d061f67de8c2b5d))
* **ingesta:** Sprint 4 — pipeline Oracle → SQLite con scheduler automático ([ff1e165](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/ff1e165ee74c67c684b375b1e40cdc91ff6e9477))
* initialize environment variables, package lock, and project logo asset ([b00fab0](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/b00fab0cf5d187c6c5d09f6ecde700225479e197))
* **sprint-10:** CU-C06 anomalía, CU-C07 CSV export, CU-A06 rate-limit notificaciones ([e9d31c3](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/e9d31c36e80f15804e0d1dc2f11fb2f38d59ba0b))
* **sprint-11:** producción — FacturaVerificacionPort, responsive, observabilidad, security ([cf273a1](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/cf273a16274021f335318db6ecc5cee164ddbfa0))
* **sprint-1:** ingesta y serie de consumo diario (backbone) ([4a4a5d1](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/4a4a5d12251ea19fb6a9f7a072b3145d08d4de83))
* **sprint-2:** frontend scaffold React+Vite+Recharts con tests escritos ([3ef70f2](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/3ef70f219245776ff92e76e3543f917a897a43c8))
* **sprint-2:** Módulo Consumo M2 — backend completo ([2460699](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/246069988c6ba7d61c5546b1216e9d045114f6e7))
* **sprint-3:** Alembic migration rango nullable + AppShell navigation shell ([028de7b](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/028de7bcaa93e5d9986a6d480d3a5ded4b4a64e1))
* **sprint-3:** proyección mensual + vecinos + home endpoint + frontend tokens EPEC ([01c3245](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/01c324512b29427829f1c7328a6a4476024935da))
* **sprint-5:** Login con suministroId, Mi Factura y Alertas/Notificaciones ([69cc333](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/69cc333545f0b6c6b5f8b1c9edd2fa65db811dec))
* **sprint-6:** auth argon2id, cerrar sesión y objetivos de consumo ([d974e6f](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/d974e6ffd3609aba99c00eb75992b0fd2b9d1f8e))
* **sprint-7:** barra de progreso, alerta objetivo superado y seed contraseñas ([4b740f2](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/4b740f2f92692260f90b2c80b57ddeef77521f25))
* **sprint-8:** objetivo sugerido, onboarding primer login e indicadores O1-O3 ([3649bab](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/3649bab6b3212c850070f524b8434a93d0bc3fb7))
* **sprint-9:** drill-down consumo y alerta vencimiento factura ([e902c31](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/e902c31d04a6da12dc22b55df2c23105dc43314e))

### Bug Fixes

* **alertas:** registrar envío usando fecha inyectada en vez de datetime.now ([be7f09a](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/be7f09a7992adb0e01910e06add8b0eea105ab58))
* **auth:** auto-logout cuando el JWT expira en ObjetivosPage ([c346e7a](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/c346e7ad2dd4b8dedef0ea9ab98e03d5928b73c7))
* **domain:** corregir mapeo medidor->suministro usando SRV_CODIGO de Oracle ([210f0b7](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/210f0b7de420e04fccc70d926a4aba493f165bef))
* **frontend:** AppShell header + responsive nav — corregidos ambos a la vez ([4a5ddd4](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/4a5ddd48a086ff92b946b18e690d589b99f328cc)), closes [#root](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/issues/root)
* **frontend:** AppShell responsive — mostrar sidebar O bottom-nav, no ambos ([dfd6e4c](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/dfd6e4cace4cf57cdfa66c1aac61f234e917c061))
* **frontend:** AppShell responsive via CSS media query, no JS state ([d0bb905](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/d0bb90522ce88c383fb00195e0d39fe366e540cb))
* **frontend:** eliminar header duplicado de HomePage ([09530c5](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/09530c5634e06e5e80b26888cad57cb5610a0d36))
* **frontend:** vitest 13/13 verde + build TypeScript limpio ([2777328](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/2777328129054c5cc3ff2ffdcd99580f8d6981cd))
* **ingesta:** eliminar query ANCLAS — era full scan sin cota inferior, mas de 60s por dia ([1d5d812](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/1d5d812272c54ce65cce0634b258925c98ffa806))
* **privacidad:** k-anonymity n<5 en ObtenerHomeUseCase (CU-NF02) ([e9e312a](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/e9e312a48757a87c7a45cea3a33b4592e4d1e257))
* **security:** corregir IDOR en endpoints de anomalía y CSV, encoding en ObjetivosPage ([b5c8516](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/b5c8516d0de74010e2692ec44244ebfc7b1fa3ce))
* **security:** IDOR residual + info disclosure + auth bypass + apikey ([b340146](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/b3401467be8ffcb4ff051d4bd88e0e77f51d7f8c))
* **security:** validación de inputs EPEC + tests auth estrictos (401 no 500) ([6997f6d](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/6997f6dd2709f95b65e250977995f245b26d1fd1))
* **sqlite:** usar Any en vez de assert para compatibilidad con aiosqlite en PRAGMA event ([b0a4330](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/b0a43306283ae5a3668674f23b290751de7df3d8))

### Performance Improvements

* **ingesta:** procesar de a 1 día y aumentar cursor.arraysize para Oracle a escala ([1b78a43](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/1b78a437346d7697694f3e74771c9fd0e4bd7643))
* **oracle:** GROUP BY equipo+fecha en la query para reducir 384K→~15K filas/día ([cb8f0f2](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/cb8f0f23088e601ab36882a08a2190d39b386fef))
* **sqlite:** eliminar flush() por operación para reducir round-trips a SQLite ([f56ae7f](https://github.com/pedroberecibar/mock-plataforma-usuarios-epec/commit/f56ae7f6c525235333f1e9c5891c25997ec50e59))

## 1.0.0 (2026-06-10)

### Features

* auto-bootstrap and auto-close session via CLAUDE.md ([09d09f5](https://github.com/pedroberecibar/AI-dev-starter/commit/09d09f50ab66e938f7690e471448e47176f7fb85))
