from datetime import datetime
from elasticsearch_dsl import connections, Search
from elasticsearch_dsl import Document, Text, Date
from chalicelib.settings import ES_INDEX, ES_DOMAIN, ES_USER, ES_PASS
from elasticsearch_dsl import Q

con = connections.create_connection(hosts=[{'host': ES_DOMAIN,
                                            'port': 443}],
                                    http_auth=(ES_USER, ES_PASS),
                                    use_ssl=True,
                                    verify_certs=True)


class ArticleModel(Document):
    text: Text()
    source: Text()
    created_time: Date()

    class Index:
        name = ES_INDEX

    def save(self, **kwargs):
        self.created_time = datetime.now()
        return super().save(**kwargs)


def article_search(text):
    q = Q({"fuzzy": {
            "text": {
                "value": text,
                "boost": 1.0,
                "fuzziness": 2,
                "prefix_length": 0,
                "max_expansions": 100,
                "transpositions": True,
                "rewrite": "constant_score"

            }
        }
        })

    q1 = Q({"match_bool_prefix":{"text":text}})

    s = Search(index=ES_INDEX, using=con).query(q)
    response = s.execute()
    results = response.to_dict()

    if results["hits"]["total"]["value"] > 0:
        return [item["_source"] for item in results["hits"]["hits"]]
    else:
        s = Search(index=ES_INDEX, using=con).query(q1)
        response = s.execute()
        results = response.to_dict()
        return [item["_source"] for item in results["hits"]["hits"]]


def remove_index(index_name):
    return con.indices.delete(index=index_name, ignore=[400, 404])