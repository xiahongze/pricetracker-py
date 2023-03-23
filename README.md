# PriceTracker

This is a re-write of my _golang_ project, [pricetracker](https://github.com/xiahongze/pricetracker) in pure Python. Here are some improvements:

- fastapi with OpenAPI integration
- SQL as backend supported by sqlalchemy
- better scraping with Selenium
- easy configuration with YAML config file
- 80% test coverage
- support both chrome and firefox through their web-drivers

[Pushover](https://pushover.net/) integration is still supported by default.

## overview

The directory struction of this repo should be straightforward and only a few things
might need extra explanation:

- `pricetracker/models_orm.py`: sql models
- `pricetracker/models.py`: pydantic models
- `pricetracker/task.py`: background/cron task
- `pricetracker/api/basic_crud.py`: abstraction of common CRUD handlers

## installation

You need to have Chrome with chromedriver or FireFox with geckodriver.

`python3 setup.py install`

or

`pip3 install -r requirements.txt`

## test

`pip3 install -r requirements_test.txt`

`pytest`

## debug

`uvicorn pricetracker.main:app --reload`

## sample serving scripts

`start.sh`

```bash
CONFIG=config.yaml uvicorn pricetracker.main:app --host 0.0.0.0 > stdout 2>&1 &
echo $! > pid
```

`stop.sh`

```bash
kill -9 `cat ./pid`
```

## notes

Sometimes websites might block scraping using various means. One of the popular
javascript library in this realm is called
[fingerprintjs](https://github.com/fingerprintjs/fingerprintjs2),
which detects a number of things

- automation flag
- webdriver is not null
- user agent
- extension
- etc

If the default setting in this app did not work for you, try modify

- `pricetracker/assets/init.js`
- `pricetracker/webdriver.py`
- or simply change user agent in your config
- or try a different browser

## changelogs

- 0.2.0 more documentations
- 0.2.1 report page in send_message
- 0.2.2 page -> page_orm in except
- 0.2.3 prices are now reduced
- 0.2.4 use poetry, black, isort, ruff, upgraded to py38
