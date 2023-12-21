from flask import Flask
from flask_cors import CORS
from flask import request
import useful_functions
from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import useful_functions
# 这里对数据库内容进行提取
# datalist = useful_functions.get_datalist()
# # datalist_reverse = datalist
# # datalist_reverse.reverse()

# # 这里分析数据库内容，提炼出数据库信息，并对文本内容分词
# datainfo1, string = useful_functions.get_datalist_info(datalist)

# # 计算 topK=8 的词汇对应的词频
# words,weights = useful_functions.get_word_weights(string, topK=8)

app = Flask(__name__)
# 允许来自任何来源的跨域请求到 /api/ 路径。
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["SECRET_KEY"] = "12345678"

api = Api(app, version='1.0', title='News API', description='A simple news API')

news_model = api.model('News', {
    'id': fields.Integer(description='The unique identifier of the news item'),
    'title': fields.String(required=True, description='The title of the news'),
    'publish_time': fields.String(description='The publish time of the news'),
    'content': fields.String(description='The content of the news'),
    'url': fields.String(description='The URL of the news item'),
    'key_word': fields.String(description='The keyword associated with the news'),
    'source': fields.String(description='The source of the news item'),
})
# 创建一个namespace
ns = api.namespace('news', description='News operations')

# 首页
@ns.route('/')
class NewsList(Resource):
    @ns.doc('list_news')
    @ns.marshal_with(news_model,as_list=True)
    def get(self):
        """Fetch a list of news"""
        datalist = useful_functions.get_datalist()
        # print(datalist)
        return datalist
    
# Resouce for the homepage info
@ns.route('/home')
class homepage(Resource):
    @ns.doc('home_info')
    def get(self):
        """Fetch homepage information including nes details and word weights"""
        datalist = useful_functions.get_datalist()
        data_info = useful_functions.get_datalist_info(datalist)
        response_data = {
            "newsCount": data_info[0],
            "wordsCount": data_info[1],
        }
        return response_data



if __name__ == '__main__':
    app.run(debug=True)
