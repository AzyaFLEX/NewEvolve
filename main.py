from self_classes.__all_models import Board
import configparser

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    app = Board(config['Board']['width'], config['Board']['height'],
                config['Board']['cell_size'], config['Board']['fps'])
    app.run()
