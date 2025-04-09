# Sesplan

Webová aplikace pro správu a plánování RPG kampaní (např. Dungeons & Dragons). Umožňuje správu světů, postav, předmětů, lokací, sezení a dalšího.

## Technologický stack

*   **Frontend:**
    *   Framework: [Vue.js 3](https://vuejs.org/) (s Composition API)
    *   Jazyk: [TypeScript](https://www.typescriptlang.org/)
    *   Build tool: [Vite](https://vitejs.dev/)
    *   Routování: [Vue Router](https://router.vuejs.org/)
    *   HTTP klient: [Axios](https://axios-http.com/)
*   **Backend:**
    *   Framework: [FastAPI](https://fastapi.tiangolo.com/)
    *   Jazyk: [Python 3.12+](https://www.python.org/)
    *   ORM: [SQLAlchemy](https://www.sqlalchemy.org/)
    *   Migrace DB: [Alembic](https://alembic.sqlalchemy.org/)
    *   Validace dat: [Pydantic](https://docs.pydantic.dev/)
*   **Databáze:** [PostgreSQL 16+](https://www.postgresql.org/)
*   **Infrastruktura:**
    *   Kontejnerizace: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
    *   Reverzní proxy & HTTPS: [Traefik](https://traefik.io/traefik/) (s automatickými certifikáty Let's Encrypt)
*   **CI/CD:** [GitHub Actions](https://github.com/features/actions)

## Předpoklady

*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/)
*   Git
*   Webový prohlížeč

## Nastavení a spuštění lokálně

1.  **Klonování repozitáře:**
    ```bash
    git clone <URL_REPOZITARE>
    cd sesplan
    ```

2.  **Konfigurace prostředí:**
    *   Zkopírujte soubor `.env.example` (pokud existuje) nebo vytvořte nový soubor `.env` v kořenovém adresáři projektu.
    *   Upravte hodnoty v `.env` podle vaší lokální konfigurace. Minimálně budete potřebovat nastavit:
        *   `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` (pro databázi)
        *   `DATABASE_URL` (obvykle se sestaví z předchozích, např. `postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}`)
        *   `SECRET_KEY` (pro JWT, vygenerujte náhodný řetězec)
        *   `DOMAIN` (pro lokální vývoj nastavte na `localhost`)
        *   `LETSENCRYPT_EMAIL` (pro Traefik, i pro lokální vývoj je dobré vyplnit)
        *   `VITE_API_URL` (URL backendu, jak bude viditelný z frontendu, např. `https://api.localhost` nebo `http://localhost:8000` pokud nepoužíváte Traefik/HTTPS lokálně)

3.  **Sestavení a spuštění kontejnerů:**
    ```bash
    docker compose up --build
    ```
    Příznak `--build` zajistí sestavení image, pokud ještě neexistují nebo pokud se změnil Dockerfile.

4.  **Přístup k aplikaci:**
    *   Frontend by měl být dostupný na `http://localhost` (nebo `https://localhost`, pokud Traefik správně funguje s lokálními certifikáty, což může vyžadovat další nastavení důvěryhodnosti).
    *   Backend API by mělo být dostupné na `http://localhost:8000` (přímo) nebo `https://api.localhost` (přes Traefik).
    *   Traefik dashboard (pokud je povolen) by měl být na `http://localhost:8080`.

## Správa databázových migrací (Alembic)

Tento projekt používá Alembic pro správu změn schématu databáze.

### Vytvoření nové migrace

Když provedete změny v SQLAlchemy modelech (v `backend/src/app/models/`), postupujte následovně pro vygenerování nového migračního skriptu:

1.  **Ujistěte se, že běží potřebné kontejnery:**
    ```bash
    docker compose up -d --build backend postgres
    ```

2.  **Vygenerujte migraci pomocí `exec`:**
    Spusťte v terminálu příkaz pro automatické vygenerování. Nahraďte `"Popis vaší změny"` stručným vysvětlením, co migrace dělá.
    ```bash
    docker compose exec backend alembic revision --autogenerate -m "Popis vaší změny"
    ```
    Poznamenejte si název vygenerovaného souboru (např. `abcdef12345_nazev_migrace.py`), který se vypíše.

3.  **Zkopírujte migraci z kontejneru:**
    Nejprve zjistěte název nebo ID běžícího backend kontejneru:
    ```bash
    docker ps --filter name=sesplan-backend -q
    ```
    Poté soubor zkopírujte (nahraďte `<container_name_or_id>` a `<název_souboru>`):
    ```bash
    docker cp <container_name_or_id>:/app/alembic/versions/<název_souboru>.py backend/alembic/versions/
    ```

4.  **(Doporučeno)** **Zkontrolujte vygenerovaný skript:**
    Otevřete nový soubor v `backend/alembic/versions/` a ověřte, že obsah (`upgrade()` a `downgrade()` funkce) odpovídá vašim očekáváním. Může být potřeba ručně upravit pořadí operací kvůli závislostem cizích klíčů.

5.  **Přidejte změny do Gitu:**
    Přidejte upravené modely a **nový migrační soubor** do Gitu a commitněte.
    ```bash
    git add backend/src/app/models/ backend/alembic/versions/
    git commit -m "Popis změny schématu a přidání migrace"
    ```

### Aplikace migrací

Migrace se aplikují automaticky při startu `backend` kontejneru díky `entrypoint.sh` skriptu, který spouští `alembic upgrade head`.

Stačí tedy standardně spustit aplikaci:

```bash
docker compose up --build
```

`entrypoint.sh` zajistí, že databáze bude mít aplikované všechny migrace, které jsou součástí Docker image (tj. všechny migrace commitnuté v `backend/alembic/versions/`).

## Struktura projektu

```
/sesplan
├── .github/          # Konfigurace GitHub Actions (CI/CD)
├── backend/
│   ├── alembic/        # Alembic migrace a konfigurace
│   ├── src/
│   │   └── app/        # Zdrojový kód FastAPI aplikace
│   │       ├── api/      # API endpointy (routery)
│   │       ├── core/     # Konfigurace, základní nastavení
│   │       ├── crud/     # Funkce pro CRUD operace
│   │       ├── db/       # Připojení k DB, session
│   │       ├── models/   # SQLAlchemy modely (schéma DB)
│   │       ├── schemas/  # Pydantic schémata (validace dat)
│   │       ├── services/ # Business logika (pokud je potřeba)
│   │       └── main.py   # Hlavní soubor FastAPI aplikace
│   ├── tests/          # Testy pro backend
│   ├── alembic.ini     # Konfigurace Alembicu
│   ├── Dockerfile      # Dockerfile pro backend
│   ├── entrypoint.sh   # Skript pro spuštění migrací a aplikace
│   └── requirements.txt # Python závislosti
├── frontend/
│   ├── public/         # Statické soubory
│   ├── src/
│   │   ├── assets/     # Obrázky, fonty atd.
│   │   ├── components/ # Vue komponenty
│   │   ├── router/     # Konfigurace Vue Router
│   │   ├── services/   # Služby (např. API klient)
│   │   ├── stores/     # Správa stavu (např. Pinia)
│   │   ├── views/      # Vue stránky/views
│   │   ├── App.vue     # Hlavní Vue komponenta
│   │   └── main.ts     # Vstupní bod Vue aplikace
│   ├── Dockerfile      # Dockerfile pro frontend (multi-stage build)
│   ├── index.html      # Hlavní HTML soubor
│   ├── package.json    # Node.js závislosti a skripty
│   ├── tsconfig.json   # Konfigurace TypeScriptu
│   └── vite.config.ts  # Konfigurace Vite
├── infrastructure/     # Konfigurace infrastruktury (např. Traefik, pokud není v docker-compose)
├── scripts/          # Pomocné skripty
├── .env              # Lokální konfigurace (NECOMMITOVAT!)
├── .env.example      # Příklad konfiguračního souboru
├── docker-compose.yml # Definice služeb pro Docker Compose
└── README.md         # Tento soubor
```

## Deployment

Aplikace je navržena pro nasazení pomocí Docker kontejnerů.

*   **Reverzní proxy:** Traefik se stará o směrování provozu na frontend a backend a automaticky zajišťuje HTTPS certifikáty pomocí Let's Encrypt pro doménu definovanou v `.env` (`DOMAIN`).
*   **Databáze:** Používá se samostatný PostgreSQL kontejner.
*   **CI/CD:** Proces je připraven pro automatizaci pomocí GitHub Actions, které sestaví Docker images, nahrají je do registru a spustí deployment na cílovém serveru (konkrétní implementace deploy kroku závisí na cílovém prostředí).
*   **Zero-Downtime:** Docker a Traefik umožňují implementovat zero-downtime deployment strategie (např. blue-green deployment), i když to není explicitně nakonfigurováno v tomto základním `docker-compose.yml`.
