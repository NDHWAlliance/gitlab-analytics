from ga import create_app
import os

port = os.getenv('PORT')
app = create_app()
app.run(host='0.0.0.0', debug=True, port=port)
