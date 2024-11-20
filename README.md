# Big Data MTG Crawler

- Tino Schaare (1299322) - [inf22001@lehre.dhbw-stuttgart.de](mailto:inf22001@lehre.dhbw-stuttgart.de)
- DHBW Stuttgart - Computer Science, Year 2022, Big Data
- For task and lecture reference, see: [GitHub Repo](https://github.com/marcelmittelstaedt/BigData/)

This file contains:

1. Documentation
2. API Documentation
3. Setup and startup instructions

## 1. Documentation

As presented in the image below, the whole project is composed of five docker containers:

- The **PostgreSQL container** contains the end-user database.
- The **Flask (Frontend) container** functions as a webserver for the web UI and provides a REST API to fetch data from the end-user database.
- The **Hadoop/Hive container** contains raw data that is downloaded or provides in the ETL process.
- The **Flask (Backend) container** exposes a REST API that serves different purposes. The main task is to parse (downloaded) HTML pages and extract their information. Additionally, some tasks interact with the end-user database and the Hadoop/Hive container.
- The **Airflow container** manages the whole ETL workflow and trigger actions regarding the Flask (Backend) container and the Hadoop/Hive container.

![image docker structure](./static/img/container_structure.png)

Why use a separate **Flask (Backend) container** event though the **Airflow container** runs Python as well?

- Airflow runs on the Python version 2.7., which is deprecated since January 2020. To still use up-to-date Python (3.12) packages, the **Flask (Backend) container** is added.

### ETL Explanation

The ETL workflow runs every 10 minutes, triggered by a cronjob. With every run, more cards are added to the end-user database, which is accessible via the web UI. The whole process can be split into three steps that are explained in detail below.

1. Get a list of all available **set names**.
2. Pick a set name and get a **list of card IDs** that are in the set. Add those IDs to a backlog of cards, to be downloaded.
3. Continuously download cards from the card backlog.

#### (1) Set Names

At the [main page of *MTG Gatherer*](https://gatherer.wizards.com/Pages/Default.aspx), there is a dropdown with all set names. In this first step, the list is crawled. Each set name is saved with a boolean value if the card IDs of the set are already downloaded. This is done every run. If a new set name is added, it will be appended to the database.

![gatherer main page](./static/img/gatherer_main_page.png)

#### (2) Card-ID list

With a set name, a [*MTG Gatherer*](https://gatherer.wizards.com/Pages/Search/Default.aspx?action=advanced&set=[%22Adventures%20in%20the%20Forgotten%20Realms%22]) url can be build that leads to a table of all cards in the given set. The goal is to scrape all card IDs in the set. The IDs are encoded in the links of the card names.

The problem is that this table is paginated. Thus, the scraping starts with the first page, downloads all card IDs and then continuous with the next page until the last page is reached. This is checked by the layout of the pagination control. All these IDs are stored.Afterwards, the corresponding set in the end-user database is marked as downloaded. This is done every run until all sets are marked as downloaded.

![gatherer card IDs](./static/img/gatherer_card_ids.png)

#### (3) Card download

Each run should add new cards to the end-user database. To do so, a set of $n$ not yet downloaded cards is calculated. This is done by taking the card backlog from step (2) and subtracting all cards that are already downloaded. Then $n$ random elements are selected.

Each card in the set is then scraped. With the card ID, a [*MTG Gatherer*](https://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=527770) url can be build, that contains detailed card information. The card information gets extracted and added to the end-user database.

![gatherer card](./static/img/gatherer_card.png)

### Airflow DAG and Job/Transformations

Explanation of all Airflow DAG steps:

- **create_download_dir** and **clear_download_dir**: Creates a directory in the local airflow filesystem (not HDFS), where downloaded files can be stored before they are moved to their final destination.
- **create_hdfs_set_names_dir**: HDFS directory for storing a downloaded .html file. This file is later used to scrape a list of all available sets on *MTG Gatherer*, as explained in step (1).
- **create_hdfs_ids_dir** + **create_hive_table_ids**: Creation of HDFS directory with matching Hive table for .tsv files. This directory later holds a set of card IDs and matching set names. This tables functions as a backlog of scrapeable cards.
- **create_hdfs_to_download_dir** + **create_hive_to_download_ids**: Creation of HDFS directory with matching Hive table for .csv files. This directory will later hold a set of "prepared card IDs", updated in each run, that should be scraped shortly after.
- **create_hdfs_downloaded_dir** + **create_hive_downloaded_ids**: Creation of HDFS directory with matching Hive table for .csv files. This directory will later hold a set of card IDs and matching set names that are already downloaded and present in the end-user database.
- **postgres_create**: Creates the `ids` and `cards` tables in the end-user PostgreSQL database.
- **dummy_split**: Waits for all preparation tasks to finish and splits the DAG into two parallel paths.
- **download_downloaded_cards** + **hdfs_put_downloaded_cards_files**: The task calls the `/api/downloaded-cards` API endpoint. This will generate a CSV text with all cards that are present in the end-user database. The file is then saved to the local airflow directory and put into HDFS afterwards.
- **download_set_names** + **hdfs_put_set_names_file**: Downloads the *MTG Gatherer* main page and puts it into HDFS directory..
- **store_set_names**: Calls the `/api/store-set-names` endpoint which retrieves the just scraped *MTG Gatherer* main page via the Hadoop REST API. This is then parsed with the Python [BeautifulSoup library](https://pypi.org/project/beautifulsoup4/). Thereby, all set names are extracted. They are then stored to the end-user PostgreSQL database by appending only new elements. Each new element is enriched with a `downloaded` field which is set to `false` by insertion of a new element.
- **mark_downloaded_set_ids**: Calls the `/api/mark-stored-sets` endpoint. By using Hive with MapReduce, this will query a distinct set of set names, which card IDs were already added to the card backlog. Every set in this distinct list will be marked as `downloaded = true` in the end-user database. This will ensure that the same card IDs are not added twice to the card ID backlog.
- **download_set_ids** + **hdfs_put_ids_file**: Calls the `/api/get-set-ids` endpoint and stores the result. This will take a set name that is not downloaded, scrape all its card IDs from the paginated *MTG Gatherer* web pages and then returns them as a CSV text. This result will be saved as a .csv file and then be moved to its HDFS directory.
- **dummy_collect**: This operator waits for the two strands to both finish.
- **download_to_download_ids** + **hdfs_put_to_download_ids_file**: At this point, one Hive table contains a list of card IDs that are already in the end-user database, and another Hive table contains a list of all cards that are scrapeable. This task calls the `/api/get-to-download-ids?count=10` endpoint (with a number of cards to download). By using Hive with MapReduce, the backend subtracts the list of already downloaded cards from the list of downloadable cards. Then, a certain number of cards, matching the `count` parameter in the url, is taken. There will be returned as a CSV formatted text. This is stored as a .csv file and then moved to the according HDFS directory.
- **download_cards**: Calls the `/api/download_cards` endpoint. This will query the card IDs that were prepared for downloading by the previous two steps. Each card is scraped with all its detail from *MTG Gatherer* and added to the final card list in the end-user database.

![airflow workflow](./static/img/workflow.png)

The steps **download_to_download_ids** and **hdfs_put_to_download_ids_file** were first implemented as a PySpark transformation that did exactly the same and had the same output. After around five to ten successful runs, this script crashed the Hive server in each run from then on. By moving the functionality to the Python backend and querying the data with PyHive, the server runs without errors. The PySpark file is still viewable in the directory and the call is commented in the Airflow DAG definition file.

### Frontend

The frontend is a single page web UI. The UI features a searching bar with a target selection. The target specifies, if the search is applied to the card name, card artist or card text.

After submitting the search, the provided information is send towards the `/api/search` endpoint. This queries the end-user database by using a similarity measure of two strings. A list with information about multiple cards is returned, that is ordered by the similarity of the search target to the search query. This list is then displayed in the UI, whereas a similarity threshold prohibits really bad matches to be displayed.

![frontend list view](./static/img/frontend_list.png)

Each visualized list item is clickable. This opens a modal that fetches detailed card information from the `/api/card` endpoint.

![frontend detail view](./static/img/frontend_detail.png)

Two notes on the frontend implementation:

- The search information is attached to the URL, so that links contain the information of the search. Thus, the whole search can be shared by sharing just the link.
- Mana symbols are rendered into the text, as it can be seen in the card text. The raw text contains placeholders like `@Red@` that will be replaced by the matching HTML `<img src="..." />` tag.

### Files

All needed files are present in this repository. When setting up the project, those are provided to the containers by mounting the directories to the needed places.

- The used Airflow DAG: `airflow/mtg_airflow.py`
- The DDLs for PostgresQL and HIVE: `ddl/*.sql`. Except for the `ddl/postgres_setup.sql` file, none of those files has to be executed manually. The manual execution is part of the setup/startup instruction at the end of this fil .
- The Python files are in the `src` directory. Each Flask-Python container has a different entry point: `flask-app.py` for the **Flask (backend) container** and `flask_frontend` for the **Flask (frontend) container**.
- The files for the web UI are in the `static` folder, as they are served as static resources by the frontend Flask instance.
- Files for setting up the project are included in the `scrips` directory. For more setup instructions, see the setup/startup section in this documentation.
- The PySpark transformation: `pyspark/pyspark_prepare_download.py`

## 2. API Documentation

### Backend API

The **Flask (Backend) container** exposes an REST API with the following endpoints:

> `/api/test` \
> Tests the PostgreSQL and Hive connection.
>
> **Returns**
>
> - **200**: PostgreSQL and Hive version.
> - **400**: An error occurred during the operation.

> `/api/postgres-create` \
> Creates all needed PostgreSQL tables if the don't exist.
>
> **Returns**
>
> - **200**: Queries for creating the tables were successful
> - **400**: An error occurred during the operation.

> `/api/store-set-names` \
> Takes the downloaded .html and extracts a list of all set names.
> The list is stored to the PostgreSQL database. Existing elements
> are not overwritten. New elements will only be appended.
>
> **Returns**
>
> - **200**: Returns a string indicating the number of strings
> that were added to the PostgreSQL.
> - **400**: An error occurred during the operation.

> `/api/get-set-ids` \
> Gets a set name from the PostgreSQL that is marked as not downloaded.
> Then, it scrapes a list of all card IDs from *MTG Gatherer*.
> These IDs are then returned as a TSV text.
>
> **Returns**
>
> - **200**: Returns a TSV list with all IDs for a given set.
> - **400**: An error occurred during the operation.

> `/api/mark-stored-sets` \
> Queries a distinct list of set names which card IDs are already scraped.
> For each set in this list, the corresponding PostgreSQL entry is
> marked as downloaded.
>
> **Returns**
>
> - **200**: Returns a CSV list of all downloaded set names.
> - **400**: An error occurred during the operation.

> `/api/download-cards` \
> Retrieves the list of cards that should be downloaded via Hive.
> Then it downloads all *MTG Gatherer* .html files, extracts
> the information from then and stores
> the card information to the PostgreSQL database.
>
> **Returns**
>
> - **200**: Returns a string indicating the number of scraped cards.
> - **400**: An error occurred during the operation.

> `/api/downloaded-cards` \
> Gets a list of all cards that are already downloaded into the PostgreSQL
>
> **Returns**
>
> - **200**: CSV text of all card IDs with their set names.
> - **400**: An error occurred during the operation.

> `/api/get-to-download-ids` \
> Prepares a list of cards that should be downloaded next. These are
> cards that are in the "to download" backlog but aren't yet in the
> end-user database.
>
> **Query Params**
>
> - **count**: int, default=10, number of cards to prepare.
>
> **Returns**
>
> - **200**: CSV text of prepared cards.
> - **400**: An error occurred during the operation.

### Frontend API

The **Flask (Frontend) container** exposes an REST API with the following endpoints:

> `/api/search` \
> Given a search query, returns a list of matching cards.
>
> **Query Params**
>
> - **query**: string, search query.
> - **count**: int, default=5, number of cards to be returned.
> - **target**: string, default=name, field to which the query string
> is applied (name, text or artist).
>
> **Returns**
>
> - **200**: List of cards encoded as JSON.

> `/api/card` \
> Retrieves detailed information about a single card.
>
> **Query Params**
>
> - **query**: int, ID of the card.
>
> **Returns**
>
> - **200**: Card information encoded as JSON.

## 3. Setup and startup

To **setup the project** for the first time, follow and execute the steps listed in `scripts/setup.sh`.

To **start the project** if it is already setup, follow and execute the steps listed in `scripts/startup.sh`.

To **reset the project**, just delete all docker containers and follow the setup instructions again:

```bash
# Stop every running container
docker stop hadoop airflow python postgres frontend

# Remove all containers
docker rm hadoop airflow python postgres frontend

# Remove all images (optional)
docker rmi marcelmittelstaedt/spark_base:latest && docker rmi python:3.12.7-bookworm && docker rmi marcelmittelstaedt/airflow:latest && docker rmi postgres:latest
```

### Ports

If running the project, e.g. on a Google-Cloud VM, the following ports have to be exposed:

- 80 (443) for the Web-Frontend
- 8080 for Airflow web UI (if needed)
