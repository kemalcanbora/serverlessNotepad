from chalice import Chalice, Response, Rate
from chalicelib.es import ArticleModel, article_search
import jinja2
import os

app = Chalice(app_name='CorporateMemory')


def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or "./")).get_template(filename).render(context)


@app.schedule(Rate(24, unit=Rate.HOURS))
def es_init():
    ArticleModel.init()


@app.route('/')
def index():
    context = {'welcome': 'Corporate Memory'}
    template = render("chalicelib/index.html", context)

    return Response(template, status_code=200, headers={
        "Content-Type": "text/html",
        "Access-Control-Allow-Origin": "*"
    })


@app.route('/sendinfo', methods=['POST'])
def send_information():
    body = app.current_request.json_body
    host = app.current_request.headers.get("host")

    try:
        data = ArticleModel(text=body["text"],
                            source=host)
        data.save()
        return {"status": True}
    except KeyError:
        return {"status": False,
                "description": "You have to use text field in your query"}


@app.route('/getinfo', methods=['GET', 'POST'])
def get_information():
    body = app.current_request.json_body

    return article_search(body["text"])
