from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':
  from views import app
  app.run(host='0.0.0.0', port='3395', debug=True)
