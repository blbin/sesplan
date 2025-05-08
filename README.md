# Sesplan

Webová aplikace pro správu a plánování RPG kampaní (např. Dungeons & Dragons). Umožňuje správu světů, postav, předmětů, lokací, sezení a dalšího.

## Obsah

- [Technologický stack](#technologický-stack)
- [Požadavky](#požadavky)
- [Nastavení a spuštění](#nastavení-a-spuštění)
  - [Lokální vývoj](#lokální-vývoj)
  - [Konfigurace prostředí](#konfigurace-prostředí)
- [Struktura projektu](#struktura-projektu)
- [Správa databázových migrací](#správa-databázových-migrací)
  - [Vytvoření nové migrace](#vytvoření-nové-migrace)
  - [Aplikace migrací](#aplikace-migrací)
- [Vývojové principy](#vývojové-principy)
- [Deployment](#deployment)
- [Skripty](#skripty)

## Technologický stack

*   **Frontend:**
    *   Framework: [Vue.js 3](https://vuejs.org/) (s Composition API)
    *   Jazyk: [TypeScript](https://www.typescriptlang.org/)
    *   UI Knihovna: [Vuetify](https://vuetifyjs.com/)
    *   Stav: [Pinia](https://pinia.vuejs.org/) (aktuálně nepoužíván, ale plánován)
    *   Build tool: [Vite](https://vitejs.dev/)
    *   Routování: [Vue Router](https://router.vuejs.org/)
    *   HTTP klient: [Axios](https://axios-http.com/)
*   **Backend:**
    *   Framework: [FastAPI](https://fastapi.tiangolo.com/)
    *   Jazyk: [Python 3.12+](https://www.python.org/)
    *   ORM: [SQLAlchemy](https://www.sqlalchemy.org/) (asynchronní s `asyncpg`)
    *   Migrace DB: [Alembic](https://alembic.sqlalchemy.org/)
    *   Validace dat: [Pydantic](https://docs.pydantic.dev/)
    *   Autentizace: JWT
*   **Databáze:** [PostgreSQL 16+](https://www.postgresql.org/)
*   **Infrastruktura:**
    *   Kontejnerizace: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
    *   Reverzní proxy & HTTPS: [Traefik](https://traefik.io/traefik/) (s automatickými certifikáty Let's Encrypt)
*   **CI/CD:** [GitHub Actions](https://github.com/features/actions)

## Požadavky

*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/)
*   Git
*   Webový prohlížeč (doporučeno Chrome, Firefox)
*   PowerShell (pro spouštění některých skriptů, např. `generate_migration.ps1` ve Windows)

## Nastavení a spuštění

### Lokální vývoj

1.  **Klonování repozitáře:**
    ```bash
    git clone <URL_VAŠEHO_REPOZITÁŘE> # Nahraďte URL vašeho forku nebo hlavního repozitáře
    cd sesplan
    ```

2.  **Konfigurace prostředí:**
    *   Vytvořte soubor `.env` v kořenovém adresáři projektu. Můžete zkopírovat a upravit `.env.prod` nebo začít od nuly.
    *   Pro lokální vývoj jsou klíčové následující proměnné (viz také `docker-compose.local.yml` pro výchozí hodnoty a kontext):
        *   `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
        *   `DATABASE_URL` (např. `postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}`)
        *   `SECRET_KEY` (pro JWT, vygenerujte náhodný řetězec, např. pomocí `openssl rand -hex 32`)
        *   `DOMAIN=localhost` (pro Traefik a CORS)
        *   `API_DOMAIN=api.localhost` (pro Traefik a CORS)
        *   `TRAEFIK_ACME_EMAIL` (váš email, i pro lokální testování Traefiku s Let's Encrypt staging serverem)
        *   `VITE_API_URL=https://${API_DOMAIN}` (URL backendu pro frontend)
    *   **Důležité:** Ujistěte se, že hodnoty v `.env` odpovídají konfiguraci v `docker-compose.local.yml`, zejména pokud jde o porty a názvy služeb.

3.  **Sestavení a spuštění kontejnerů (lokální vývoj):**
    Použijte soubor `docker-compose.local.yml`, který je optimalizován pro lokální vývoj (např. s hot-reloadingem).
    ```bash
    docker compose -f docker-compose.local.yml up --build
    ```
    Příznak `--build` zajistí sestavení/přestavení image, pokud ještě neexistují nebo pokud se změnil `Dockerfile` nebo související soubory. Pro běžné spouštění již sestavených obrazů stačí `docker compose -f docker-compose.local.yml up`.

4.  **Přístup k aplikaci:**
    *   Frontend: `http://localhost` (nebo `https://localhost` pokud Traefik běží s HTTPS)
    *   Backend API: `http://localhost:8000` (přímo, pokud tak definováno v `docker-compose.local.yml`) nebo `https://api.localhost` (přes Traefik)
    *   Swagger API dokumentace: `https://api.localhost/docs` (přes Traefik) nebo `http://localhost:8000/docs`
    *   Traefik dashboard: `http://localhost:8081` (dle konfigurace v `docker-compose.local.yml`)

### Produkční nasazení

Pro produkční nasazení se používá `docker-compose.yml` a `.env.prod`. Konfigurace by měla obsahovat skutečnou doménu a silné hesla.

```bash
docker compose -f docker-compose.yml --env-file .env.prod up -d --build
```

## Struktura projektu

```
/sesplan
├── .github/            # Konfigurace GitHub Actions (CI/CD)
│   └── workflows/
├── .idea/              # Konfigurace pro IntelliJ IDE (volitelné, v .gitignore)
├── backend/
│   ├── alembic/        # Alembic migrace
│   │   └── versions/   # Vygenerované migrační skripty
│   ├── src/
│   │   └── app/        # Zdrojový kód FastAPI aplikace
│   │       ├── api/      # API endpointy (routery)
│   │       │   └── endpoints/
│   │       ├── auth/     # Logika pro autentizaci a autorizaci (JWT)
│   │       ├── core/     # Konfigurace, základní nastavení (např. config.py)
│   │       ├── crud/     # CRUD (Create, Read, Update, Delete) operace
│   │       ├── db/       # Připojení k DB, session, base model
│   │       ├── models/   # SQLAlchemy modely (schéma DB)
│   │       ├── schemas/  # Pydantic schémata (validace dat, (de)serializace)
│   │       └── services/ # Business logika, voláno z API endpointů
│   ├── tests/          # Testy pro backend (pytest)
│   ├── alembic.ini     # Konfigurace Alembicu
│   ├── Dockerfile      # Dockerfile pro backend
│   └── entrypoint.sh   # Skript pro spuštění migrací a aplikace při startu kontejneru
├── frontend/
│   ├── public/         # Statické soubory (např. favicon.ico)
│   ├── src/
│   │   ├── assets/     # Obrázky, fonty, globální styly
│   │   ├── components/ # Znovupoužitelné Vue komponenty
│   │   │   ├── availability/
│   │   │   ├── campaign/
│   │   │   ├── common/
│   │   │   └── ... další specifické komponenty ...
│   │   ├── composables/ # Vue 3 Composition API funkce
│   │   ├── plugins/    # Vue pluginy (např. Vuetify)
│   │   ├── router/     # Konfigurace Vue Router (routes.ts)
│   │   ├── services/   # Služby (např. API klient, formátování dat)
│   │   │   └── api/
│   │   ├── store/      # Pinia stores pro globální správu stavu
│   │   ├── types/      # TypeScript typy a rozhraní
│   │   ├── utils/      # Pomocné funkce
│   │   ├── views/      # Vue stránky/views (komponenty mapované na routes)
│   │   ├── App.vue     # Hlavní Vue komponenta
│   │   └── main.ts     # Vstupní bod Vue aplikace
│   ├── .vscode/        # Nastavení pro VS Code (doporučená rozšíření atd.)
│   ├── dist/           # Sestavené soubory frontendu (generováno Vitem)
│   ├── Dockerfile      # Dockerfile pro frontend (multi-stage build)
│   ├── index.html      # Hlavní HTML soubor pro Vite
│   ├── package.json    # Node.js závislosti a skripty (npm/yarn/pnpm)
│   ├── tsconfig.json   # Konfigurace TypeScriptu pro frontend
│   └── vite.config.ts  # Konfigurace Vite
├── infrastructure/     # Konfigurace pro další služby
│   ├── postgres/       # Případné specifické konfigurační soubory pro PostgreSQL
│   ├── redis/          # Případné specifické konfigurační soubory pro Redis
│   └── traefik/        # Konfigurační soubory pro Traefik (např. traefik.yml, dynamic_conf.yml)
├── letsencrypt/        # Adresář pro ukládání SSL certifikátů Let's Encrypt (mountováno Traefikem)
├── scripts/            # Pomocné skripty (např. pro generování migrací)
├── .env                # Lokální konfigurace (NECOMMITOVAT! V .gitignore)
├── .env.prod           # Produkční konfigurace (NECOMMITOVAT! Šablona může být .env.prod.example)
├── .gitignore          # Specifikuje soubory ignorované Gitem
├── docker-compose.local.yml # Docker Compose pro lokální vývoj
├── docker-compose.yml  # Docker Compose pro produkci
├── generate_migration.ps1 # PowerShell skript pro generování Alembic migrací
└── README.md           # Tento soubor
```

## Správa databázových migrací

Tento projekt používá Alembic pro správu změn schématu databáze.

### Vytvoření nové migrace

Když provedete změny v SQLAlchemy modelech (v `backend/src/app/models/`), je potřeba vygenerovat nový migrační skript.

1.  **Ujistěte se, že běží `backend` a `postgres` kontejnery:**
    Pokud neběží, spusťte je (stačí pouze tyto dva pro generování migrace):
    ```bash
    docker compose -f docker-compose.local.yml up -d --build backend postgres
    ```

2.  **Vygenerujte migraci pomocí skriptu `generate_migration.ps1`:**
    Otevřete PowerShell, přejděte do kořenového adresáře projektu a spusťte:
    ```powershell
    ./generate_migration.ps1 -m "Stručný popis vaší změny"
    ```
    Například:
    ```powershell
    ./generate_migration.ps1 -m "add_user_email_verification_status"
    ```
    Tento skript automaticky:
    *   Spustí `alembic revision --autogenerate` uvnitř backend kontejneru.
    *   Zkopíruje vygenerovaný migrační soubor z kontejneru do `backend/alembic/versions/`.

3.  **(Doporučeno)** **Zkontrolujte vygenerovaný skript:**
    Otevřete nový soubor v `backend/alembic/versions/` a ověřte, že obsah (`upgrade()` a `downgrade()` funkce) odpovídá vašim očekáváním. Někdy je potřeba ručně upravit pořadí operací nebo doplnit specifické SQL příkazy.

4.  **Přidejte změny do Gitu:**
    Přidejte upravené modely a **nový migrační soubor** do Gitu.
    ```bash
    git add backend/src/app/models/ backend/alembic/versions/
    git commit -m "feat(db): Popis změny schématu a přidání migrace" # Použijte vhodný commit prefix
    ```

### Aplikace migrací

Migrace se aplikují **automaticky** při startu `backend` kontejneru. Skript `backend/entrypoint.sh` obsahuje příkaz `alembic upgrade head`, který zajistí aktualizaci databáze na nejnovější verzi schématu.

Stačí tedy standardně spustit aplikaci pomocí `docker compose up`.

## Vývojové principy

Projekt se řídí následujícími principy (podrobněji viz interní dokumentace):
- **DRY (Don't Repeat Yourself)**
- **KISS (Keep It Simple, Stupid)**
- **Modularita**
- **Testovatelnost:** Nové funkce vyžadují testy. Backend testy jsou v `backend/tests/`.
- **Bezpečnost:** Dodržování bezpečnostních best practices.
- **Výkon:** Optimalizace frontendových assetů, API volání a databázových dotazů.
- **Code style & konvence:** Dodržujte zavedené konvence v projektu (viz existující kód).

## Deployment

Aplikace je navržena pro nasazení pomocí Docker kontejnerů.
- **Reverzní proxy:** Traefik se stará o směrování provozu a HTTPS.
- **CI/CD:** GitHub Actions jsou nastaveny pro automatizaci buildů, testů a potenciálně deploymentu. Workflow soubory jsou v `.github/workflows/`.

## Skripty

Adresář `scripts/` obsahuje pomocné skripty pro usnadnění vývoje:
- `generate_migration.ps1`: Automatizuje generování Alembic migrací (popsáno výše).

---
