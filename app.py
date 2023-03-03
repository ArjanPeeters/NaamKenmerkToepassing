from flask import Flask, render_template, request

app = Flask('NaamKenmerkToepassing')

selections = []
@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        selection1 = request.form['selection1']
        selection2 = request.form['selection2']
        selection3 = request.form['selection3']
        # Do something with the selections
        selections.append(f'{selection1}_{selection2}_{selection3}')

    return render_template('index.html', selections=selections)


if __name__ == '__main__':
    app.run(debug=True)