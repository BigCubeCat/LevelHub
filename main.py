from app import *
from blueprints import levels_api, maze_generator_api, user_api, results_api


def main():
    db_session.global_init(os.path.abspath("db/CubeAdventureHub.sqlite"))
    app.register_blueprint(maze_generator_api.blueprint)
    app.register_blueprint(user_api.blueprint)
    app.register_blueprint(levels_api.blueprint)
    app.register_blueprint(results_api.blueprint)
    api.add_resource(user_api.UserResource, '/api/user_data/<int:user_id>')
    api.add_resource(levels_api.LevelResource, '/api/level_data/<int:level_id>')
    api.add_resource(results_api.ResultResource, '/api/result_data/<int:result_id>')
    app.run()


main()
