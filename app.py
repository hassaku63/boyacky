import os
import uuid
from datetime import datetime as dt
from flask import Flask, render_template, request, redirect, url_for
from boyaki import Boyaki

app = Flask(__name__, static_folder='static')


@app.route('/', methods=['GET'])
def index():
    key = dt.now().strftime('%Y-%m-%d')
    result = Boyaki.view_index.query(key, scan_index_forward=False)
    try:
        items = list(result)
    except Exception as ex:
        items = []
    return render_template('index.html', items=items)


@app.route('/create', methods=['POST'])
def create():
    boyaki = request.form['boyaki']
    if boyaki:
        try:
            create_data(boyaki)
        except Exception as ex:
            print('error:', ex)
    return redirect(url_for('.index'))


@app.route('/delete/<string:id>')
def delete(id: str) -> None:
    print(f'delete: id={id}')
    try:
        item = Boyaki.get(id)
        item.delete()
    except Boyaki.DoesNotExist:
        print('Boyaki does not exist')
    except Exception as ex:
        print('error:', ex)
    return redirect(url_for('.index'))


def create_data(boyaki: str) -> None:
    now = dt.now()
    id = str(uuid.uuid4())
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M:%S')
    model = Boyaki(id, boyaki=boyaki, date=date_str, time=time_str)
    model.save()
    print(f'create: id={id}, boyaki={boyaki}')


if __name__ == '__main__':
    try:
        if not Boyaki.exists():
            Boyaki.create_table(wait=True)
    except Exception as ex:
        print('error:', ex)
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
