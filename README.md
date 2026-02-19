# elastic-search
Have Elasticsearch installed locally

Create a virtual environment `python3 -m venv venv`

Activate the virtual environment `source venv/bin/activate`

Install the requirements at `pip install -r requirements.txt`

execute `python3 scraping_file.py`

Head over to this url `http://localhost:9200/my-index/_search?pretty` to see the documents provided your Elastic search uses port 9200

To deactivate the virtual environment `deactivate`
